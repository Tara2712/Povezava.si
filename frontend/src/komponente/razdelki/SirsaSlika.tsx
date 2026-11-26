import PregledVizual from "../vizualizacije/PregledVizual";
import "./SirsaSlika.css";

function SirsaSlika() {
  return (
    <section className="big-picture-section" id="platforma">
      <div className="section-container big-picture-grid">
        <div className="big-picture-visual">
          <PregledVizual />
          <div className="floating-note">
            <span className="floating-note-icon">✳</span>
            <div>
              <strong>Celovit pregled</strong>
              <small>Podatki na enem mestu</small>
            </div>
          </div>
        </div>

        <div className="big-picture-content">
          <span className="eyebrow">POVEZANI PODATKI</span>
          <h2>
            Poglejte širšo
            <br />
            <span>sliko.</span>
          </h2>
          <p>
            Posamezen podatek pove le del zgodbe. Ko jih povežemo, dobimo boljši
            vpogled v odnose med podjetji, osebami in poslovnim okoljem.
          </p>

          <div className="numbered-points">
            <div>
              <span>01</span>
              <p>
                <strong>Hitro iskanje</strong> – poiščite osebe in podjetja.
              </p>
            </div>
            <div>
              <span>02</span>
              <p>
                <strong>Pregled povezav</strong> – odkrijte neposredne in
                posredne odnose.
              </p>
            </div>
            <div>
              <span>03</span>
              <p>
                <strong>Vizualna predstavitev</strong> – razumite podatke skozi
                omrežje.
              </p>
            </div>
            <div>
              <span>04</span>
              <p>
                <strong>Več virov</strong> – informacije združene v enem okolju.
              </p>
            </div>
          </div>

          <a className="text-link" href="/app">
            Preizkusite platformo <span>↗</span>
          </a>
        </div>
      </div>
    </section>
  );
}

export default SirsaSlika;
