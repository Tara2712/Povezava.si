import Logotip from "./Logotip";
import { NAVIGACIJSKE_POVEZAVE } from "../../podatki/navigacija";
import "./Noga.css";
import { Link } from "react-router-dom";

function Noga() {
  return (
    <footer className="site-footer">
      <div className="section-container footer-top">
        <Logotip dodatenRazred="footer-brand" />

        <p>
          Povezujemo javno dostopne podatke
          <br />
          v razumljivo celoto.
        </p>

        <nav className="footer-nav">
          {NAVIGACIJSKE_POVEZAVE.map((povezava) => (
            <a href={povezava.href} key={povezava.href}>
              {povezava.oznaka}
            </a>
          ))}
        </nav>

        <a className="footer-app-link" href="/app">
          Raziščite povezave ↗
        </a>
      </div>

      <div className="section-container footer-bottom">
        <span>© {new Date().getFullYear()} Povezava.si</span>
        <span>Projekt za preglednejše raziskovanje javnih podatkov.</span>
      </div>
    </footer>
  );
}

export default Noga;
