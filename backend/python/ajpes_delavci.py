import argparse  #branje argumentov iz terminala
import asyncio  #več strani hkratno obdeluje
import csv
import logging  #izpisovanje info.
import os  
import random
import re
import time
from pathlib import Path  #pot do datotek
from typing import Dict, List, Set
from urllib.parse import urljoin  #url

import pandas as pd
from playwright.async_api import async_playwright  #odpiranje strani brskalnika

VHODNA_DATOTEKA = "opsiprs.csv"
IZHODNA_DATOTEKA = "ajpes_osebe.csv"
AJPES_URL = "https://www.ajpes.si/"

ST_DELAVCEV = 5
VELIKOST_VRSTE = 500
SHRANI_NA_VSAKIH = 50
ST_POSKUSOV = 3
ZAKASNITEV_MIN = 0.2
ZAKASNITEV_MAX = 0.8

STATUS_OK = "ok"
STATUS_NI_NAJDENO = "ni_najdeno"
STATUS_NAPAKA = "napaka"
KONCNI_STATUSI = {STATUS_OK, STATUS_NI_NAJDENO}

STOLPEC_MATICNA = "Matična številka podjetja"
STOLPEC_STATUS = "Status zajema"

STOLPCI_IZHODA = [
    STOLPEC_MATICNA,
    STOLPEC_STATUS,
    "Telefon",
    "Email",
    "Datum vpisa",
    "Status aktivnosti",
    "Velikost",
    "Glavna dejavnost",
    "Ustanovitelji",
    "Zastopniki",
]


OZNAKA_V_STOLPEC = {
    "telefon": "Telefon",
    "elektronski naslov": "Email",
    "datum vpisa": "Datum vpisa",
    "datum vpisa pri registrskem organu": "Datum vpisa",
    "status aktivnosti": "Status aktivnosti",
    "velikost": "Velikost",
    "glavna dejavnost": "Glavna dejavnost",
    "glavna dejavnost (skd)": "Glavna dejavnost",
    "ustanovitelji": "Ustanovitelji",
    "zastopniki": "Zastopniki",
}

OZNAKA_KONTAKT = "telefon/telefaks/e-pošta"
VRSTE_TELEFON = {"telefon", "gsm"}
VRSTE_EMAIL = {"elektronska pošta"}


JS_IZVLECI_PARE = """
() => {
  const pari = [];
  document.querySelectorAll('div.row').forEach(vrstica => {
    const oznaka = vrstica.querySelector(':scope > div.col-sm-5.text-thin');
    const vrednost = vrstica.querySelector(':scope > div.col-sm-7');
    if (oznaka && vrednost) {
      pari.push([oznaka.innerText.trim(), vrednost.innerText.trim()]);
    }
  });
  return pari;
}
"""

OZNAKE_IZPISA = {
    "ustanovitelji": "Ustanovitelji",
    "ustanovitelj": "Ustanovitelji",
    "zastopniki": "Zastopniki",
    "zastopnik": "Zastopniki",
}

JS_IZPIS = """
(oznake) => {
  const norm = s => s.replace(/\\s+/g, ' ').trim().replace(/:$/, '').trim().toLowerCase();
  const rezultat = {};
  document.querySelectorAll('td, th, div, span, dt, label, b, strong, p').forEach(el => {
    if (el.children.length > 0) return;
    const o = norm(el.innerText || el.textContent || '');
    if (!oznake.includes(o) || (o in rezultat)) return;

    let nivo = el;
    let sosed = nivo.nextElementSibling;
    for (let i = 0; i < 2 && !sosed && nivo.parentElement; i++) {
      nivo = nivo.parentElement;
      sosed = nivo.nextElementSibling;
    }
    if (sosed) {
      const besedilo = (sosed.innerText || sosed.textContent || '').trim();
      if (besedilo) rezultat[o] = besedilo;
    }
  });
  return rezultat;
}
"""

dnevnik = logging.getLogger("ajpes")


class PodjetjeNiNajdeno(Exception):
    """Stran se je naložila, a ni ne podatkov podjetja ne prijave."""



def preberi_vhodni_csv(pot: str) -> pd.DataFrame:
    """Prebere CSV in preizkusi več kodiranj. Vse vrednosti so besedilo."""
    if not os.path.exists(pot):
        raise FileNotFoundError(
            f"Vhodna datoteka '{pot}' ne obstaja (iščem v: {Path.cwd()}). "
            "Podajte pot z --vhod."
        )

    kodiranja = ["utf-8-sig", "utf-16", "cp1250", "latin1"]
    zadnja_napaka = None
    for kodiranje in kodiranja:
        try:
            df = pd.read_csv(
                pot,
                encoding=kodiranje,
                sep=None,
                engine="python",
                dtype=str,
                on_bad_lines="warn",
            )
            dnevnik.info("CSV prebran (kodiranje=%s, vrstic=%d)", kodiranje, len(df))
            return df
        except Exception as e:
            zadnja_napaka = e
    raise RuntimeError(f"CSV ni bilo mogoče prebrati. Zadnja napaka: {zadnja_napaka}")


def normaliziraj_maticno(vrednost) -> str:
    if pd.isna(vrednost):
        return ""
    s = str(vrednost).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def nalozi_obdelane_maticne(izhodna_pot: str) -> Set[str]:
    """Vrne matične številke s končnim statusom. Napake se ob ponovnem zagonu ponovijo."""
    if not os.path.exists(izhodna_pot) or os.path.getsize(izhodna_pot) == 0:
        return set()

    df = pd.read_csv(izhodna_pot, encoding="utf-8-sig", dtype=str)
    if STOLPEC_STATUS not in df.columns or list(df.columns) != STOLPCI_IZHODA:
        raise RuntimeError(
            f"'{izhodna_pot}' ima drugačne stolpce kot trenutna skripta. "
            "Preimenujte ali izbrišite datoteko ali podajte drug --izhod."
        )

    koncni = df[df[STOLPEC_STATUS].isin(KONCNI_STATUSI)]
    obdelane = set(koncni[STOLPEC_MATICNA].dropna().str.strip())
    dnevnik.info("Že obdelanih (ok/ni_najdeno): %d", len(obdelane))
    return obdelane



def normaliziraj_oznako(oznaka: str) -> str:
    return " ".join(oznaka.split()).rstrip(":").strip().lower()


def dodaj_vrednost(podatki: Dict[str, str], stolpec: str, vrednost: str) -> None:
    if not vrednost or vrednost in podatki[stolpec].split(" | "):
        return
    if podatki[stolpec]:
        podatki[stolpec] += " | " + vrednost
    else:
        podatki[stolpec] = vrednost


def razvrsti_kontakte(podatki: Dict[str, str], besedilo: str) -> None:
    """Vrstice oblike '01 7507 231 (Telefon)' razvrsti v Telefon ali Email."""
    for vrstica in besedilo.split("\n"):
        vrstica = vrstica.strip()
        if not vrstica:
            continue
        ujemanje = re.match(r"^(.*?)\s*\(([^()]+)\)\s*$", vrstica)
        if not ujemanje:
            continue
        vrednost = ujemanje.group(1).strip()
        vrsta = ujemanje.group(2).strip().lower()
        if vrsta in VRSTE_TELEFON:
            dodaj_vrednost(podatki, "Telefon", vrednost)
        elif vrsta in VRSTE_EMAIL:
            dodaj_vrednost(podatki, "Email", vrednost)
        # telefaks namenoma izpuščen


def razvrsti_pare(pari, maticna: str) -> Dict[str, str]:
    podatki = {stolpec: "" for stolpec in STOLPCI_IZHODA}
    podatki[STOLPEC_MATICNA] = maticna
    zadnja_oznaka = ""

    for oznaka, besedilo in pari:
        if not besedilo:
            continue

        # Vrstica s prazno oznako je nadaljevanje prejšnje (npr. druge dejavnosti).
        o = normaliziraj_oznako(oznaka) if oznaka else zadnja_oznaka
        zadnja_oznaka = o

        if o == OZNAKA_KONTAKT:
            razvrsti_kontakte(podatki, besedilo)
            continue

        stolpec = OZNAKA_V_STOLPEC.get(o)
        if stolpec is None:
            dnevnik.debug("Preskočena oznaka '%s' (%s)", o, maticna)
            continue

        vrednost = " | ".join(" ".join(t.split()) for t in besedilo.split("\n") if t.strip())
        dodaj_vrednost(podatki, stolpec, vrednost)

    return podatki


async def pohitri_kontekst(kontekst):
    """Blokira slike, pisave in medije za vse strani v kontekstu."""
    async def obdelaj_pot(pot):
        if pot.request.resource_type in {"image", "font", "media"}:
            await pot.abort()
        else:
            await pot.continue_()

    await kontekst.route("**/*", obdelaj_pot)
    kontekst.set_default_timeout(10000)
    kontekst.set_default_navigation_timeout(20000)


async def poisci_podjetje(page, maticna: str) -> None:
    """Poišče podjetje in po potrebi opravi anonimno prijavo."""
    await page.goto(AJPES_URL, wait_until="domcontentloaded")

    iskalno_polje = page.locator("#prva_OsnovnoIskanje")
    await iskalno_polje.wait_for(state="visible")
    await iskalno_polje.fill(maticna)
    await page.locator("input[type='submit'][value='IŠČI']").first.click()

    osnovni_podatki = page.locator("h4:has-text('OSNOVNI PODATKI')")
    gumb_prijava = page.locator("a.btn.btn-warning:has-text('PRIJAVA V SISTEM')")

    try:
        await osnovni_podatki.or_(gumb_prijava).first.wait_for(timeout=15000)
    except Exception:
        raise PodjetjeNiNajdeno(maticna)

    if await osnovni_podatki.count() > 0:
        return

    dnevnik.debug("Potrebna prijava")
    await gumb_prijava.first.click()

    anonimno = page.locator("text=Vstopi kot anonimni uporabnik")
    await anonimno.wait_for(state="visible")
    await anonimno.click()

    nadaljuj = page.locator("button.btn.btn-success:has-text('Nadaljuj s prijavo')")
    await nadaljuj.wait_for(state="visible")
    await nadaljuj.click()

    await osnovni_podatki.first.wait_for(timeout=15000)


async def zajemi_osebe(page, maticna: str) -> Dict[str, str]:
    pari = await page.evaluate(JS_IZVLECI_PARE)
    return razvrsti_pare(pari, maticna)


async def zajemi_izpis(page) -> Dict[str, str]:
    """Odpre 'Izpis iz poslovnega registra' in prebere ustanovitelje in zastopnike."""
    povezava = page.locator("a:has-text('Izpis iz poslovnega registra')").first
    href = await povezava.get_attribute("href", timeout=5000)
    if not href:
        return {}

    await page.goto(urljoin(page.url, href), wait_until="domcontentloaded")

# Počakaj CAPTCHA
    try:
        await page.wait_for_function(
            """() => {
                const tekst = document.body.innerText;
                return !tekst.includes('Preverjanje CAPTCHA poteka')
                    && tekst.length > 500;
            }""",
            timeout=30000
        )
    except Exception:
        dnevnik.warning("Izpis se ni pravilno naložil (CAPTCHA): %s", page.url)
        return {}

    surovo = await page.evaluate(JS_IZPIS, list(OZNAKE_IZPISA))

    rezultat: Dict[str, str] = {stolpec: "" for stolpec in set(OZNAKE_IZPISA.values())}
    for oznaka, besedilo in surovo.items():
        vrednost = " | ".join(" ".join(t.split()) for t in besedilo.split("\n") if t.strip())
        dodaj_vrednost(rezultat, OZNAKE_IZPISA[oznaka], vrednost)
    return {stolpec: v for stolpec, v in rezultat.items() if v}


async def dopolni_iz_izpisa(page, podatki: Dict[str, str]) -> None:
    """Ustanovitelji in zastopniki iz registra (ustanovitelji najprej, nato zastopniki)."""
    maticna = podatki[STOLPEC_MATICNA]
    try:
        izpis = await zajemi_izpis(page)
    except Exception as e:
        dnevnik.warning("%s: izpis iz registra ni uspel: %s", maticna, e)
        return

    if not izpis:
        dnevnik.warning("%s: v izpisu iz registra ni ustanoviteljev ni zastopnikov", maticna)
        return

    if "Ustanovitelji" in izpis:
        podatki["Ustanovitelji"] = izpis["Ustanovitelji"]
    if "Zastopniki" in izpis:
        podatki["Zastopniki"] = izpis["Zastopniki"]


async def obdelaj_maticno(kontekst, page, maticna: str):
    """Poskusi večkrat. Vrne (page, podatki), podatki imajo vedno status."""
    prazno = {stolpec: "" for stolpec in STOLPCI_IZHODA}
    prazno[STOLPEC_MATICNA] = maticna

    for poskus in range(1, ST_POSKUSOV + 1):
        try:
            await poisci_podjetje(page, maticna)
            podatki = await zajemi_osebe(page, maticna)
            await dopolni_iz_izpisa(page, podatki)
            podatki[STOLPEC_STATUS] = STATUS_OK
            return page, podatki

        except PodjetjeNiNajdeno:
            if poskus == ST_POSKUSOV:
                prazno[STOLPEC_STATUS] = STATUS_NI_NAJDENO
                return page, prazno
            dnevnik.debug("%s ni najdeno (poskus %d)", maticna, poskus)

        except Exception as e:
            dnevnik.warning("%s napaka (poskus %d/%d): %s", maticna, poskus, ST_POSKUSOV, e)
            if poskus == ST_POSKUSOV:
                prazno[STOLPEC_STATUS] = STATUS_NAPAKA
                return page, prazno
            try:
                await page.close()
            except Exception:
                pass
            page = await kontekst.new_page()

        await asyncio.sleep(2 ** poskus)

    prazno[STOLPEC_STATUS] = STATUS_NAPAKA
    return page, prazno


# Delavci 
async def delavec(id_delavca: int, brskalnik, vrsta_nalog: asyncio.Queue,
                  vrsta_rezultatov: asyncio.Queue):
    kontekst = await brskalnik.new_context()
    await pohitri_kontekst(kontekst)
    page = await kontekst.new_page()

    try:
        while True:
            naloga = await vrsta_nalog.get()
            try:
                if naloga is None:
                    break

                maticna = naloga
                try:
                    page, podatki = await obdelaj_maticno(kontekst, page, maticna)
                except Exception as e:
                    dnevnik.error("[W%d] Nepričakovana napaka %s: %s", id_delavca, maticna, e)
                    podatki = {stolpec: "" for stolpec in STOLPCI_IZHODA}
                    podatki[STOLPEC_MATICNA] = maticna
                    podatki[STOLPEC_STATUS] = STATUS_NAPAKA
                    page = await kontekst.new_page()

                await vrsta_rezultatov.put(podatki)
                await asyncio.sleep(random.uniform(ZAKASNITEV_MIN, ZAKASNITEV_MAX))
            finally:
                vrsta_nalog.task_done()
    finally:
        await kontekst.close()


def oblikuj_cas(sekunde: float) -> str:
    sekunde = int(sekunde)
    return f"{sekunde // 3600}h {sekunde % 3600 // 60:02d}m {sekunde % 60:02d}s"


async def zapisovalec(vrsta_rezultatov: asyncio.Queue, izhodna_pot: str, skupaj: int):
    datoteka_obstaja = os.path.exists(izhodna_pot) and os.path.getsize(izhodna_pot) > 0
    zapisanih = 0
    po_statusu = {STATUS_OK: 0, STATUS_NI_NAJDENO: 0, STATUS_NAPAKA: 0}
    zacetek = time.monotonic()

    with open(izhodna_pot, "a", newline="", encoding="utf-8-sig") as f:
        pisec = csv.DictWriter(f, fieldnames=STOLPCI_IZHODA, extrasaction="ignore")
        if not datoteka_obstaja:
            pisec.writeheader()
            f.flush()

        while True:
            vrstica = await vrsta_rezultatov.get()
            if vrstica is None:
                vrsta_rezultatov.task_done()
                break

            pisec.writerow(vrstica)
            zapisanih += 1
            po_statusu[vrstica[STOLPEC_STATUS]] += 1

            if zapisanih % SHRANI_NA_VSAKIH == 0 or zapisanih == skupaj:
                f.flush()
                os.fsync(f.fileno())
                pretekli = time.monotonic() - zacetek
                hitrost = zapisanih / pretekli
                preostalo = (skupaj - zapisanih) / hitrost if hitrost else 0
                dnevnik.info(
                    "%d/%d | %.2f/s | preteklo %s | preostalo ~%s | ok=%d ni=%d napake=%d",
                    zapisanih, skupaj, hitrost,
                    oblikuj_cas(pretekli), oblikuj_cas(preostalo),
                    po_statusu[STATUS_OK], po_statusu[STATUS_NI_NAJDENO],
                    po_statusu[STATUS_NAPAKA],
                )

            vrsta_rezultatov.task_done()

        f.flush()
        os.fsync(f.fileno())

# Diagnostika
# pri ukazu dodaj --diagnostika
async def diagnostika(maticna: str, viden: bool):
    """Shrani HTML strani podjetja, prebrane pare in HTML izpisa iz registra."""
    async with async_playwright() as p:
        brskalnik = await p.chromium.launch(headless=not viden)
        try:
            kontekst = await brskalnik.new_context()
            page = await kontekst.new_page()
            await poisci_podjetje(page, maticna)

            pari = await page.evaluate(JS_IZVLECI_PARE)
            Path(f"diagnostika_{maticna}.html").write_text(
                await page.content(), encoding="utf-8"
            )
            with open(f"diagnostika_{maticna}_pari.txt", "w", encoding="utf-8") as f:
                for oznaka, vrednost in pari:
                    f.write(f"{oznaka!r} -> {vrednost!r}\n")
            print(f"Shranjeno: diagnostika_{maticna}.html in diagnostika_{maticna}_pari.txt")

            print("\nRazvrščeni podatki:")
            for stolpec, vrednost in razvrsti_pare(pari, maticna).items():
                skrajsano = vrednost if len(vrednost) <= 100 else vrednost[:100] + " ..."
                print(f"  {stolpec}: {skrajsano}")

            try:
                izpis = await zajemi_izpis(page)
                print("\nIz izpisa iz registra:")
                if not izpis:
                    print("  (nič najdeno: potrebujem diagnostika_%s_izpis.html)" % maticna)
                for stolpec, vrednost in izpis.items():
                    print(f"  {stolpec}: {vrednost}")
            finally:
                Path(f"diagnostika_{maticna}_izpis.html").write_text(
                    await page.content(), encoding="utf-8"
                )
                print(f"\nShranjeno: diagnostika_{maticna}_izpis.html")
        finally:
            await brskalnik.close()


async def glavna(args):
    df = preberi_vhodni_csv(args.vhod)

    if "Matična številka" not in df.columns:
        raise RuntimeError(f"Manjka stolpec 'Matična številka'. Stolpci v CSV: {list(df.columns)}")

    obdelane = nalozi_obdelane_maticne(args.izhod)

    maticne: List[str] = []
    videne: Set[str] = set()
    for vrednost in df["Matična številka"]:
        m = normaliziraj_maticno(vrednost)
        if m and m not in obdelane and m not in videne:
            videne.add(m)
            maticne.append(m)

    if args.limit is not None:
        maticne = maticne[: args.limit]

    skupaj = len(maticne)
    dnevnik.info("Za obdelavo: %d | delavcev: %d", skupaj, args.delavcev)
    if skupaj == 0:
        dnevnik.info("Ni nič za obdelati.")
        return

    vrsta_nalog: asyncio.Queue = asyncio.Queue(maxsize=VELIKOST_VRSTE)
    vrsta_rezultatov: asyncio.Queue = asyncio.Queue(maxsize=VELIKOST_VRSTE)

    async with async_playwright() as p:
        brskalnik = await p.chromium.launch(headless=not args.viden)
        try:
            naloga_zapisovalca = asyncio.create_task(
                zapisovalec(vrsta_rezultatov, args.izhod, skupaj)
            )
            naloge_delavcev = [
                asyncio.create_task(delavec(i + 1, brskalnik, vrsta_nalog, vrsta_rezultatov))
                for i in range(args.delavcev)
            ]

            for maticna in maticne:
                await vrsta_nalog.put(maticna)
            for _ in range(args.delavcev):
                await vrsta_nalog.put(None)

            await asyncio.gather(*naloge_delavcev)
            await vrsta_rezultatov.put(None)
            await naloga_zapisovalca
        finally:
            await brskalnik.close()

    dnevnik.info("KONČANO. Izhod: %s", Path(args.izhod).resolve())


def preberi_argumente():
    parser = argparse.ArgumentParser(description="Zajem podatkov z AJPES po matični številki")
    parser.add_argument("--vhod", default=VHODNA_DATOTEKA, help="vhodni CSV")
    parser.add_argument("--izhod", default=IZHODNA_DATOTEKA, help="izhodni CSV")
    parser.add_argument("--delavcev", type=int, default=ST_DELAVCEV, help="število sočasnih delavcev")
    parser.add_argument("--limit", type=int, default=None, help="obdelaj samo prvih N številk")
    parser.add_argument("--viden", action="store_true", help="prikaži okno brskalnika (za testiranje)")
    parser.add_argument("--podrobno", action="store_true", help="podrobnejši izpis (debug)")
    parser.add_argument("--diagnostika", metavar="MATICNA",
                        help="shrani HTML in prebrane pare za eno matično številko")
    return parser.parse_args()


if __name__ == "__main__":
    argumenti = preberi_argumente()
    logging.basicConfig(
        level=logging.DEBUG if argumenti.podrobno else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    if argumenti.diagnostika:
        asyncio.run(diagnostika(argumenti.diagnostika, argumenti.viden))
    else:
        asyncio.run(glavna(argumenti))
