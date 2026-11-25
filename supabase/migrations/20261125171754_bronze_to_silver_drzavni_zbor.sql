
CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE IF NOT EXISTS silver.drzavni_zbor_poslanci (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    bronze_id BIGINT REFERENCES bronze.drzavni_zbor_zajemi(id),

    ime TEXT NOT NULL,
    id_osebe TEXT NOT NULL,
    mandat_id TEXT,

    delovna_telesa TEXT,
    mednarodna_dejavnost TEXT,

    datum_nastopa_funkcije DATE,
    poslanska_skupina TEXT,
    volilna_enota TEXT,

    poslanska_pisarna TEXT,
    url_slike TEXT,

    profil_url TEXT NOT NULL,
    vir TEXT,

    CONSTRAINT uq_drzavni_zbor_poslanec
        UNIQUE (id_osebe, mandat_id)
);

WITH bronze_podatki AS (
    SELECT
        b.id AS bronze_id,
        b.vir,
        b.url,
        b.naslov,
        b.podatki,

        COALESCE(
            NULLIF(TRIM(b.podatki ->> 'ime'), ''),
            NULLIF(TRIM(b.naslov), '')
        ) AS ime,

        (regexp_match(b.url, '[?&]idOsebe=([^&]+)'))[1]
            AS id_osebe,

        (regexp_match(b.url, '[?&]mandatId=([^&]+)'))[1]
            AS mandat_id,

        NULLIF(TRIM(b.podatki ->> 'delovna_telesa'), '')
            AS delovna_telesa,

        NULLIF(TRIM(b.podatki ->> 'mednarodna_dejavnost'), '')
            AS mednarodna_dejavnost,

        NULLIF(TRIM(b.podatki ->> 'poslanec'), '')
            AS poslanec,

        NULLIF(TRIM(b.podatki ->> 'poslanska_pisarna'), '')
            AS poslanska_pisarna,

        NULLIF(TRIM(b.podatki ->> 'url_slike'), '')
            AS url_slike

    FROM bronze.drzavni_zbor_zajemi b

    WHERE
        b.tip_strani = 'profil_poslanca'
        AND b.podatki IS NOT NULL
        AND b.url IS NOT NULL
),

ocisceni_podatki AS (
    SELECT
        *,

        CASE
            WHEN poslanec ~
                'Datum nastopa funkcije:\s*[0-9]{1,2}\.\s*[0-9]{1,2}\.\s*[0-9]{4}'
            THEN TO_DATE(
                regexp_replace(
                    substring(
                        poslanec
                        FROM 'Datum nastopa funkcije:\s*([0-9]{1,2}\.\s*[0-9]{1,2}\.\s*[0-9]{4})'
                    ),
                    '\s+',
                    '',
                    'g'
                ),
                'DD.MM.YYYY'
            )
            ELSE NULL
        END AS datum_nastopa_funkcije,

        NULLIF(
            TRIM(
                regexp_replace(
                    regexp_replace(
                        poslanec,
                        '^.*Datum nastopa funkcije:\s*[0-9]{1,2}\.\s*[0-9]{1,2}\.\s*[0-9]{4}\s*',
                        ''
                    ),
                    '\s*Volilna enota.*$',
                    ''
                )
            ),
            ''
        ) AS poslanska_skupina,

        NULLIF(
            (regexp_match(poslanec, 'Volilna enota\s*([0-9]+)'))[1],
            ''
        ) AS volilna_enota

    FROM bronze_podatki
)

INSERT INTO silver.drzavni_zbor_poslanci (
    bronze_id,
    ime,
    id_osebe,
    mandat_id,
    delovna_telesa,
    mednarodna_dejavnost,
    datum_nastopa_funkcije,
    poslanska_skupina,
    volilna_enota,
    poslanska_pisarna,
    url_slike,
    profil_url,
    vir
)

SELECT
    bronze_id,
    ime,
    id_osebe,
    mandat_id,
    delovna_telesa,
    mednarodna_dejavnost,
    datum_nastopa_funkcije,
    poslanska_skupina,
    volilna_enota,
    poslanska_pisarna,
    url_slike,
    url,
    vir
FROM ocisceni_podatki
WHERE
    ime IS NOT NULL
    AND id_osebe IS NOT NULL

ON CONFLICT (id_osebe, mandat_id)

DO UPDATE SET
    bronze_id = EXCLUDED.bronze_id,
    ime = EXCLUDED.ime,
    delovna_telesa = EXCLUDED.delovna_telesa,
    mednarodna_dejavnost = EXCLUDED.mednarodna_dejavnost,
    datum_nastopa_funkcije = EXCLUDED.datum_nastopa_funkcije,
    poslanska_skupina = EXCLUDED.poslanska_skupina,
    volilna_enota = EXCLUDED.volilna_enota,
    poslanska_pisarna = EXCLUDED.poslanska_pisarna,
    url_slike = EXCLUDED.url_slike,
    profil_url = EXCLUDED.profil_url,
    vir = EXCLUDED.vir;

CREATE INDEX IF NOT EXISTS idx_dz_poslanci_ime
    ON silver.drzavni_zbor_poslanci (ime);

CREATE INDEX IF NOT EXISTS idx_dz_poslanci_id_osebe
    ON silver.drzavni_zbor_poslanci (id_osebe);
