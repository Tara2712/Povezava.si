
import os
import re
import json
import hashlib
import html as html_lib
from datetime import datetime, timezone
from urllib.parse import urljoin
import psycopg
from psycopg.types.json import Jsonb
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

VIR = "Državni zbor Republike Slovenije"

URL_SEZNAM = "https://www.dz-rs.si/wps/portal/Home/pos/pp/"

def izracunaj_sha256(vsebina: str) -> str:
    return hashlib.sha256(
        vsebina.encode("utf-8")
    ).hexdigest()


def pocisti_vrednost(vrednost: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        vrednost or ""
    ).strip()


def normaliziraj_ime(ime: str) -> str:
    """Odstrani presledke in ločila za primerjavo imen."""
    return re.sub(
        r"[^a-zA-ZčšžČŠŽ0-9]",
        "",
        ime or ""
    ).casefold()

def shrani_v_bronze(
    povezava,
    url: str,
    tip_strani: str,
    html: str,
    naslov: str,
    podatki: dict,
) -> bool:

    sha256 = izracunaj_sha256(html)

    with povezava.cursor() as kurzor:

        kurzor.execute(
            """
            INSERT INTO bronze.drzavni_zbor_zajemi (
                vir,
                url,
                tip_strani,
                naslov,
                vsebina_html,
                podatki,
                sha256
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url, sha256)
            DO NOTHING;
            """,
            (
                VIR,
                url,
                tip_strani,
                naslov,
                html,
                Jsonb(podatki),
                sha256,
            ),
        )

        shranjeno = kurzor.rowcount == 1

    povezava.commit()

    return shranjeno

OZNAKE_RAZDELKOV = [
    "DELOVNA TELESA",
    "MEDNARODNA DEJAVNOST",
    "Poslanec",
    "Poslanska pisarna",
    "Vse poslanke in poslanci",
    "Državni zbor",
]


def najdi_oznako(
    besedilo: str,
    oznaka: str,
    zacetek: int = 0,
) -> int:

    vzorec = re.escape(oznaka)
    vzorec = vzorec.replace(r"\ ", r"\s+")

    zadetki = list(
        re.finditer(
            r"(?<!\w)" + vzorec + r"(?!\w)",
            besedilo,
            flags=re.IGNORECASE,
        )
    )

    for zadetek in zadetki:
        if zadetek.start() >= zacetek:
            return zadetek.start()

    return -1


def najdi_poslanca(besedilo: str) -> int:

    vzorec = re.compile(
        r"(?<!\w)Poslanec(?!\w)",
        flags=re.IGNORECASE,
    )

    for zadetek in vzorec.finditer(besedilo):

        nadaljevanje = besedilo[
            zadetek.end():zadetek.end() + 800
        ]

        if re.search(
            r"Datum\s+nastopa\s+funkcije",
            nadaljevanje,
            flags=re.IGNORECASE,
        ):
            return zadetek.start()

    return -1


def najdi_poslansko_pisarno(besedilo: str) -> int:

    vzorec = re.compile(
        r"(?<!\w)Poslanska\s+pisarna(?!\w)",
        flags=re.IGNORECASE,
    )

    zadetki = list(vzorec.finditer(besedilo))

    for zadetek in zadetki:

        nadaljevanje = besedilo[
            zadetek.end():zadetek.end() + 600
        ]

        if re.search(
            r"Uradne\s+ure|ulica|cesta|trg",
            nadaljevanje,
            flags=re.IGNORECASE,
        ):
            return zadetek.start()

    if zadetki:
        return zadetki[-1].start()

    return -1

def izlusci_razdelek(
    besedilo: str,
    zacetek: int,
    naslednje_oznake: list,
) -> str | None:

    if zacetek < 0:
        return None

    konec_oznake = None

    for oznaka in OZNAKE_RAZDELKOV:

        pozicija = najdi_oznako(
            besedilo,
            oznaka,
            zacetek + 1,
        )

        if pozicija == zacetek:
            konec_oznake = zacetek + len(oznaka)
            break

    if konec_oznake is None:
        konec_oznake = zacetek

    konci = []

    for oznaka in naslednje_oznake:

        pozicija = najdi_oznako(
            besedilo,
            oznaka,
            konec_oznake,
        )

        if pozicija >= 0:
            konci.append(pozicija)

    if konci:
        konec = min(konci)
    else:
        konec = len(besedilo)

    rezultat = pocisti_vrednost(
        besedilo[konec_oznake:konec]
    )

    if not rezultat:
        return None

    return rezultat

def pridobi_url_slike(
    soup,
    ime: str,
    osnovni_url: str,
) -> str | None:

    iskano_ime = normaliziraj_ime(ime)
    kandidati = []

    for slika in soup.find_all("img"):

        alt = slika.get("alt", "")
        title = slika.get("title", "")

        url_slike = (
            slika.get("src")
            or slika.get("data-src")
            or slika.get("data-original")
            or slika.get("data-lazy-src")
        )

        if not url_slike:

            srcset = slika.get("srcset")

            if srcset:
                url_slike = (
                    srcset.split(",")[0]
                    .strip()
                    .split(" ")[0]
                )

        if not url_slike:
            continue

        if url_slike.startswith("data:"):
            continue

        url_slike = urljoin(
            osnovni_url,
            url_slike,
        )

        opis = normaliziraj_ime(
            alt + " " + title
        )

        ime_okolice = ""

        nadrejeni = slika.parent

        for _ in range(4):

            if nadrejeni is None:
                break

            ime_okolice += " " + nadrejeni.get_text(
                " ",
                strip=True
            )

            nadrejeni = nadrejeni.parent

        ime_okolice = normaliziraj_ime(
            ime_okolice
        )

        pot_slike = normaliziraj_ime(
            url_slike
        )

        ocena = 0

        if iskano_ime and iskano_ime in opis:
            ocena += 10

        if iskano_ime and iskano_ime in ime_okolice:
            ocena += 5

        if "poslanec" in pot_slike or "oseba" in pot_slike:
            ocena += 2

        if "foto" in pot_slike or "image" in pot_slike:
            ocena += 1

        if ocena > 0:

            kandidati.append({
                "url": url_slike,
                "ocena": ocena,
            })

    if not kandidati:
        return None

    kandidati.sort(
        key=lambda x: x["ocena"],
        reverse=True,
    )

    return kandidati[0]["url"]

def pridobi_podatke_strani(
    html: str,
    ime_iz_seznama: str,
    osnovni_url: str,
    besedilo_strani: str,
) -> dict:

    soup = BeautifulSoup(html, "html.parser")

    ime = pocisti_vrednost(ime_iz_seznama)

    url_slike = pridobi_url_slike(
        soup,
        ime,
        osnovni_url,
    )

    besedilo = pocisti_vrednost(besedilo_strani)

    vzorec_delovna = re.search(
        r"DELOVNA\s+TELESA",
        besedilo,
        re.IGNORECASE,
    )

    vzorec_mednarodna = re.search(
        r"MEDNARODNA\s+DEJAVNOST",
        besedilo,
        re.IGNORECASE,
    )

    vzorec_poslanec = None

    for zadetek in re.finditer(
        r"Poslanec",
        besedilo,
        re.IGNORECASE,
    ):

        nadaljevanje = besedilo[
            zadetek.end():zadetek.end() + 1000
        ]

        if re.search(
            r"Datum\s+nastopa\s+funkcije",
            nadaljevanje,
            re.IGNORECASE,
        ):
            vzorec_poslanec = zadetek
            break

    vzorec_pisarna = None

    zacetek_iskanja = (
        vzorec_poslanec.end()
        if vzorec_poslanec
        else 0
    )

    for zadetek in re.finditer(
        r"Poslanska\s+pisarna",
        besedilo,
        re.IGNORECASE,
    ):

        if zadetek.start() < zacetek_iskanja:
            continue

        vzorec_pisarna = zadetek
        break

    oznake = []

    if vzorec_delovna:
        oznake.append((
            "delovna_telesa",
            vzorec_delovna.start(),
            vzorec_delovna.end(),
        ))

    if vzorec_mednarodna:
        oznake.append((
            "mednarodna_dejavnost",
            vzorec_mednarodna.start(),
            vzorec_mednarodna.end(),
        ))

    if vzorec_poslanec:
        oznake.append((
            "poslanec",
            vzorec_poslanec.start(),
            vzorec_poslanec.end(),
        ))

    if vzorec_pisarna:
        oznake.append((
            "poslanska_pisarna",
            vzorec_pisarna.start(),
            vzorec_pisarna.end(),
        ))

    oznake.sort(key=lambda x: x[1])

    podatki = {
        "ime": ime,
        "url_slike": url_slike,
        "delovna_telesa": None,
        "mednarodna_dejavnost": None,
        "poslanec": None,
        "poslanska_pisarna": None,
    }

    for indeks, oznaka in enumerate(oznake):

        naziv, zacetek, konec = oznaka

        if indeks + 1 < len(oznake):
            konec_razdelka = oznake[indeks + 1][1]
        else:
            konec_razdelka = len(besedilo)

        vsebina = pocisti_vrednost(
            besedilo[konec:konec_razdelka]
        )

        vsebina = re.split(
            r"Vse poslanke in poslanci|"
            r"Državni zbor Republike Slovenije",
            vsebina,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        if vsebina:
            podatki[naziv] = vsebina

    izbrani_deli = BeautifulSoup(
        "<div id='profil-poslanca'></div>",
        "html.parser",
    )

    glavni_element = izbrani_deli.find(
        id="profil-poslanca"
    )

    naslov = izbrani_deli.new_tag("h1")
    naslov.string = ime
    glavni_element.append(naslov)

    if url_slike:
        slika = izbrani_deli.new_tag(
            "img",
            src=url_slike,
            alt=ime,
        )
        glavni_element.append(slika)

    razdelki = [
        ("Delovna telesa", "delovna_telesa"),
        ("Mednarodna dejavnost", "mednarodna_dejavnost"),
        ("Poslanec", "poslanec"),
        ("Poslanska pisarna", "poslanska_pisarna"),
    ]

    for naziv, kljuc in razdelki:

        vsebina = podatki[kljuc]

        if not vsebina:
            continue

        razdelek = izbrani_deli.new_tag("section")

        h2 = izbrani_deli.new_tag("h2")
        h2.string = naziv

        odstavek = izbrani_deli.new_tag("p")
        odstavek.string = vsebina

        razdelek.append(h2)
        razdelek.append(odstavek)

        glavni_element.append(razdelek)

    koncno_besedilo = pocisti_vrednost(
        glavni_element.get_text(" ", strip=True)
    )

    return {
        "ime": ime,
        "besedilo": koncno_besedilo,
        "podatki": podatki,
        "html": str(glavni_element),
    }

def pridobi_povezave_poslancev(
    html: str,
) -> list:

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    poslanci = []
    ze_obdelane_povezave = set()

    for povezava in soup.find_all(
        "a",
        href=True,
    ):

        href = povezava["href"]

        if (
            "izbranP" not in href
            or "idOsebe=" not in href
        ):
            continue

        url = urljoin(
            URL_SEZNAM,
            href,
        )

        if url in ze_obdelane_povezave:
            continue

        ze_obdelane_povezave.add(url)

        ime = pocisti_vrednost(
            povezava.get_text(" ", strip=True)
        )

        if not ime:
            continue

        poslanci.append({
            "ime": ime,
            "url": url,
        })

    return poslanci

def pocakaj_na_profil(stran):

    stran.wait_for_load_state(
        "domcontentloaded",
        timeout=30000,
    )

    stran.wait_for_timeout(2500)

    stran.locator("body").wait_for(
        state="visible",
        timeout=15000,
    )

def zajemi_podatke():

    povezava_db = os.getenv(
        "SUPABASE_DB_URL"
    )

    if not povezava_db:
        raise RuntimeError(
            "Okoljska spremenljivka SUPABASE_DB_URL ni nastavljena."
        )

    uspesno = 0
    podvojeno = 0
    napake = 0

    with psycopg.connect(povezava_db) as povezava:

        with sync_playwright() as playwright:

            brskalnik = playwright.chromium.launch(
                headless=True
            )

            try:

                stran = brskalnik.new_page(
                    locale="sl-SI"
                )

                stran.set_default_timeout(30000)

                print("Odpiram seznam poslancev...")

                stran.goto(
                    URL_SEZNAM,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                stran.locator(
                    "a[href*='izbranP'][href*='idOsebe=']"
                ).first.wait_for(
                    state="visible",
                    timeout=60000,
                )

                stran.wait_for_timeout(2000)

                html_seznam = stran.content()

                poslanci = pridobi_povezave_poslancev(
                    html_seznam
                )

                print(
                    f"Najdenih profilov: {len(poslanci)}"
                )

                for indeks, poslanec in enumerate(
                    poslanci,
                    start=1,
                ):

                    url_profila = poslanec["url"]
                    ime = poslanec["ime"]

                    print(
                        f"\n[{indeks}/{len(poslanci)}] "
                        f"{ime}"
                    )

                    try:

                        stran.goto(
                            url_profila,
                            wait_until="domcontentloaded",
                            timeout=60000,
                        )

                        pocakaj_na_profil(stran)

                        html_profila = stran.content()

                        besedilo_strani = stran.locator("body").inner_text(
                            timeout=15000
                        )

                        podatki_profila = pridobi_podatke_strani(
                            html_profila,
                            ime,
                            url_profila,
                            besedilo_strani,
                        )

                        podatki = podatki_profila["podatki"]

                        uporabni_podatki = [
                            podatki["delovna_telesa"],
                            podatki["mednarodna_dejavnost"],
                            podatki["poslanec"],
                            podatki["poslanska_pisarna"],
                        ]

                        if not any(uporabni_podatki):
                            raise ValueError(
                                "Na profilu ni bilo mogoče najti zahtevanih podatkov."
                            )

                        zapis = {
                            "ime": podatki_profila["ime"],
                            "url_profila": url_profila,
                            "url_slike": podatki["url_slike"],
                            "delovna_telesa": podatki["delovna_telesa"],
                            "mednarodna_dejavnost": podatki["mednarodna_dejavnost"],
                            "poslanec": podatki["poslanec"],
                            "poslanska_pisarna": podatki["poslanska_pisarna"],
                            "besedilo": podatki_profila["besedilo"],
                            "zajeto_ob": datetime.now(
                                timezone.utc
                            ).isoformat(),
                        }

                        shranjeno = shrani_v_bronze(
                            povezava=povezava,
                            url=url_profila,
                            tip_strani="profil_poslanca",
                            html=podatki_profila["html"],
                            naslov=podatki_profila["ime"],
                            podatki=zapis,
                        )

                        if shranjeno:

                            uspesno += 1

                            print(
                                f"  Shranjeno v Bronze: {ime}"
                            )

                        else:

                            podvojeno += 1

                            print(
                                f"  Že obstaja v bazi: {ime}"
                            )

                        najdeni = [
                            naziv
                            for naziv, vrednost in [
                                ("Delovna telesa", podatki["delovna_telesa"]),
                                ("Mednarodna dejavnost", podatki["mednarodna_dejavnost"]),
                                ("Poslanec", podatki["poslanec"]),
                                ("Poslanska pisarna", podatki["poslanska_pisarna"]),
                                ("Fotografija", podatki["url_slike"]),
                            ]
                            if vrednost
                        ]

                        print(
                            "  Najdeno: "
                            + (
                                ", ".join(najdeni)
                                if najdeni
                                else "nič"
                            )
                        )

                    except PlaywrightTimeoutError:

                        napake += 1

                        print(
                            f"  Napaka: časovna omejitev pri {ime}"
                        )

                    except Exception as napaka:

                        napake += 1

                        print(
                            f"  Napaka pri {ime}: {napaka}"
                        )

            finally:

                brskalnik.close()

    print("ZAJEM JE KONČAN")
    print(f"Najdenih profilov: {len(poslanci)}")
    print(f"Novo shranjenih: {uspesno}")
    print(f"Že obstoječih: {podvojeno}")
    print(f"Napak: {napake}")


if __name__ == "__main__":
    zajemi_podatke()
