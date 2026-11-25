CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.xml_viri (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    vir_key TEXT NOT NULL,
    vir_naziv TEXT NOT NULL,
    vir_url TEXT NOT NULL,
    licenca TEXT NOT NULL,

    sha256 CHAR(64) NOT NULL,
    pridobljeno_ob TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    content_type TEXT NOT NULL DEFAULT 'application/xml',
    xml_original BYTEA NOT NULL,

    CONSTRAINT uq_xml_viri_vir_hash
        UNIQUE (vir_key, sha256)
);