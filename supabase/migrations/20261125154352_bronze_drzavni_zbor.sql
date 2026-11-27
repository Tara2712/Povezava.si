
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.drzavni_zbor_zajemi (
    id BIGSERIAL PRIMARY KEY,

    vir TEXT NOT NULL,
    url TEXT NOT NULL,
    tip_strani TEXT NOT NULL,

    zajeto_ob TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    naslov TEXT,
    vsebina_html TEXT NOT NULL,
    podatki JSONB NOT NULL DEFAULT '{}'::jsonb,

    sha256 TEXT NOT NULL,

    UNIQUE (url, sha256)
);
