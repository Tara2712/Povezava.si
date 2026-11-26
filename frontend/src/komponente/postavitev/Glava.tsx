import Logotip from "./Logotip";
import { NAVIGACIJSKE_POVEZAVE } from "../../podatki/navigacija";
import "./Glava.css";
import { Link } from "react-router-dom";

function Glava() {
  return (
    <header className="site-header">
      <Logotip ariaOznaka="Povezava.si domov" />

      <nav className="main-nav">
        {NAVIGACIJSKE_POVEZAVE.map((povezava) => (
          <a href={povezava.href} key={povezava.href}>
            {povezava.oznaka}
          </a>
        ))}
      </nav>

      <Link className="header-cta" to="/prijava">
        Raziščite povezave <span>↗</span>
      </Link>
    </header>
  );
}

export default Glava;
