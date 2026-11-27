import Logotip from "./Logotip";
import { NAVIGACIJSKE_POVEZAVE } from "../../podatki/navigacija";
import { useAvtentikacija } from "../avtentikacija/AvtentikacijaKontekst";
import "./Glava.css";
import { Link } from "react-router-dom";

function Glava() {
  const { uporabnik, nalaganje } = useAvtentikacija();

  return (
    <header className="site-header">
      <Logotip ariaOznaka="Povezava.si domov" />

      <nav className="main-nav">
        {NAVIGACIJSKE_POVEZAVE.map((povezava) =>
          povezava.href.startsWith("/") ? (
            <Link to={povezava.href} key={povezava.oznaka}>
              {povezava.oznaka}
            </Link>
          ) : (
            <a href={povezava.href} key={povezava.oznaka}>
              {povezava.oznaka}
            </a>
          )
        )}
      </nav>

      {!nalaganje &&
        (uporabnik ? (
          <Link className="nav-uporabnik" to="/app" aria-label="Moj profil">
            <svg viewBox="0 0 512 512" width="26" height="26" aria-hidden="true">
              <circle cx="256" cy="148" r="107" fill="currentColor" />
              <path
                d="M64 440C64 350 150 277 256 277C362 277 448 350 448 440a28 28 0 0 1-28 28H92a28 28 0 0 1-28-28Z"
                fill="currentColor"
              />
            </svg>
          </Link>
        ) : (
          <Link className="header-cta" to="/prijava">
            Raziščite povezave <span>↗</span>
          </Link>
        ))}
    </header>
  );
}

export default Glava;