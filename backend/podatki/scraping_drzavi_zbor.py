
import os
import re
import json
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin

import psycopg
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

VIR = "Državni zbor Republike Slovenije"

URL_SEZNAM = (
    "https://www.dz-rs.si/wps/portal/Home/pos/pp/"
)


def izracunaj_sha256(vsebina: str) -> str:
    return hashlib.sha256(vsebina.encode("utf-8")).hexdigest()


def shrani_v_bronze(
    povezava,
    url: str,
    tip_strani: str,
    html: str,
    naslov: str,
    podatki: dict,
):

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
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (url, sha256)
            DO NOTHING;
            """,
            (
                VIR,
                url,
                tip_strani,
                naslov,
                html,
                json.dumps(podatki, ensure_ascii=False),
                sha256,
            ),
        )

    povezava.commit()



def pridobi_podatke_strani(html: str) -> dict:
    """Iz HTML-ja izlušči samo vsebino profila osebe."""

    soup = BeautifulSoup(html, "html.parser")

    nepotrebni_elementi = [
        "header",
        "footer",
        "nav",
        "aside",
        "script",
        "style",
        "noscript",
        "iframe",
        "form",
        "button",
    ]

    for element in soup.select(",".join(nepotrebni_elementi)):
        element.decompose()

    nepotrebni_razredi = [
        ".navigation",
        ".breadcrumb",
        ".breadcrumbs",
        ".menu",
        ".main-menu",
        ".sidebar",
        ".side-menu",
        ".cookie",
        ".cookie-banner",
        ".footer",
        ".header",
        ".social-media",
        ".share",
    ]

    for selector in nepotrebni_razredi:
        for element in soup.select(selector):
            element.decompose()

    glavni_del = (
        soup.select_one("main")
        or soup.select_one('[role="main"]')
        or soup.select_one("#content")
        or soup.select_one(".content")
        or soup.select_one(".portlet-body")
        or soup.body
        or soup
    )

    naslov_element = glavni_del.find(["h1", "h2"])

    naslov = (
        naslov_element.get_text(" ", strip=True)
        if naslov_element
        else ""
    )

    besedilo = glavni_del.get_text(" ", strip=True)

    podatki_tabele = []

    for tabela in glavni_del.find_all("table"):
        for vrstica in tabela.find_all("tr"):
            celice = vrstica.find_all(["th", "td"])

            vrednosti = [
                celica.get_text(" ", strip=True)
                for celica in celice
            ]

            vrednosti = [
                vrednost
                for vrednost in vrednosti
                if vrednost
            ]

            if vrednosti:
                podatki_tabele.append(vrednosti)

    podatki_definicij = {}

    for dt in glavni_del.find_all("dt"):
        dd = dt.find_next_sibling("dd")

        if dd:
            oznaka = dt.get_text(" ", strip=True)
            vrednost = dd.get_text(" ", strip=True)

            if oznaka and vrednost:
                podatki_definicij[oznaka] = vrednost

    kontakti = []

    for povezava in glavni_del.find_all("a", href=True):
        href = povezava["href"]
        ime = povezava.get_text(" ", strip=True)

        if href.startswith("mailto:"):
            kontakti.append({
                "tip": "email",
                "vrednost": href.replace("mailto:", ""),
            })

        elif href.startswith("tel:"):
            kontakti.append({
                "tip": "telefon",
                "vrednost": href.replace("tel:", ""),
            })

    html_osebe = str(glavni_del)

    return {
        "ime": naslov,
        "besedilo": besedilo,
        "podatki_tabele": podatki_tabele,
        "podatki": podatki_definicij,
        "kontakti": kontakti,
        "html": html_osebe,
    }


def pridobi_povezave_poslancev(html: str) -> list:

    soup = BeautifulSoup(html, "html.parser")

    poslanci = []
    ze_obdelane_povezave = set()

    for povezava in soup.find_all("a", href=True):
        href = povezava["href"]

        if "izbranP" not in href or "idOsebe=" not in href:
            continue

        url = urljoin(URL_SEZNAM, href)

        if url in ze_obdelane_povezave:
            continue

        ze_obdelane_povezave.add(url)

        ime = povezava.get_text(" ", strip=True)

        if not ime:
            continue

        poslanci.append({
            "ime": ime,
            "url": url,
        })

    return poslanci


def zajemi_podatke():

    povezava_db = os.getenv("SUPABASE_DB_URL")

    if not povezava_db:
        raise RuntimeError(
            "Okoljska spremenljivka SUPABASE_DB_URL ni nastavljena."
        )

    with psycopg.connect(povezava_db) as povezava:
        with sync_playwright() as playwright:

            brskalnik = playwright.chromium.launch(
                headless=True
            )

            stran = brskalnik.new_page(
                locale="sl-SI"
            )

            print("Odpiram seznam poslancev...")

            stran.goto(
                URL_SEZNAM,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            stran.locator(
                "a[href*='izbranP']"
            ).first.wait_for(
                state="visible",
                timeout=60000,
            )

            stran.wait_for_timeout(3000)

            html_seznam = stran.content()

            podatki_seznam = pridobi_podatke_strani(
                html_seznam
            )

            poslanci = pridobi_povezave_poslancev(
                html_seznam
            )

            print(
                f"Najdenih profilnih povezav: {len(poslanci)}"
            )


            for indeks, poslanec in enumerate(
                poslanci,
                start=1,
            ):
                url_profila = poslanec["url"]

                print(
                    f"[{indeks}/{len(poslanci)}] "
                    f"Zajemam: {poslanec['ime']}"
                )

                try:
                    stran.goto(
                        url_profila,
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    stran.wait_for_timeout(1500)

                    html_profila = stran.content()

                    podatki_profila = pridobi_podatke_strani(
                        html_profila
                    )

                    
                    shrani_v_bronze(
                        povezava=povezava,
                        url=url_profila,
                        tip_strani="profil_poslanca",
                        html=podatki_profila["html"],
                        naslov=podatki_profila["ime"],
                        podatki={
                            "ime": podatki_profila["ime"],
                            "ime_iz_seznama": poslanec["ime"],
                            "url_profila": url_profila,
                            "besedilo": podatki_profila["besedilo"],
                            "podatki_tabele": podatki_profila["podatki_tabele"],
                            "podatki": podatki_profila["podatki"],
                            "kontakti": podatki_profila["kontakti"],
                        },
                    )


                except Exception as napaka:
                    print(
                        f"Napaka pri profilu "
                        f"{poslanec['ime']}: {napaka}"
                    )

            brskalnik.close()

    print("Zajem podatkov je končan.")


if __name__ == "__main__":
    zajemi_podatke()
