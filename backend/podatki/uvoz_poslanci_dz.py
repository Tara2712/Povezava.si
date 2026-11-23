
import hashlib
import os
import urllib.request
import xml.etree.ElementTree as ET
import psycopg


VIR_URL = "https://fotogalerija.dz-rs.si/datoteke/opendata/SIF.XML"
VIR_KEY = "sifrant-drzavnega-zbora"
VIR_NAZIV = "Šifrant Državnega zbora"
LICENCA = "CC BY 4.0"


def prenesi_xml():

    zahteva = urllib.request.Request(
        VIR_URL,
        headers={"User-Agent": "Povezava.si/1.0"},
    )

    with urllib.request.urlopen(zahteva, timeout=60) as odgovor:
        xml_original = odgovor.read()
        content_type = odgovor.headers.get_content_type()

    ET.fromstring(xml_original)

    return xml_original, content_type


def shrani_xml(xml_original, content_type):
    povezava = os.environ.get("SUPABASE_DB_URL")

    if not povezava:
        raise RuntimeError(
            "Manjka okoljska spremenljivka SUPABASE_DB_URL."
        )

    sha256 = hashlib.sha256(xml_original).hexdigest()

    with psycopg.connect(povezava) as baza:
        rezultat = baza.execute(
            """
            INSERT INTO bronze.xml_viri (
                vir_key,
                vir_naziv,
                vir_url,
                licenca,
                sha256,
                content_type,
                xml_original
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vir_key, sha256) DO NOTHING
            RETURNING id
            """,
            (
                VIR_KEY,
                VIR_NAZIV,
                VIR_URL,
                LICENCA,
                sha256,
                content_type,
                xml_original,
            ),
        ).fetchone()

    if rezultat:
        print(f"XML uspešno shranjen. ID zapisa: {rezultat[0]}")
    else:
        print("XML je že shranjen. Nova kopija ni bila dodana.")


def main():
    xml_original, content_type = prenesi_xml()
    shrani_xml(xml_original, content_type)


if __name__ == "__main__":
    main()
