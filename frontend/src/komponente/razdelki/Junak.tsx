import OmrezjeVizual from "../vizualizacije/OmrezjeVizual";
import "./Junak.css";

function Junak() {
  return (
    <section className="hero section-container" id="home">
      <div className="hero-content">
        <h1>
          Odkrijte povezave.
          <br />
          <span>Ustvarite svoje povezave.</span>
        </h1>

        <p className="hero-description">
          Povezava.si združuje javno dostopne podatke o podjetjih in osebah ter
          jih spreminja v pregledno mrežo informacij in povezav.
        </p>

        <div className="hero-actions">
          <a className="button-primary" href="/app">
            Raziščite povezave <span>↗</span>
          </a>
        </div>

        <div className="hero-note">
          <span className="hero-note-icon">✓</span>
          Temelji na javno dostopnih podatkih
        </div>
      </div>

      <div className="hero-visual">
        <OmrezjeVizual />
      </div>
    </section>
  );
}

export default Junak;
