import { PREDNOSTI } from "../../podatki/prednosti";
import "./Prednosti.css";

function Prednosti() {
  return (
    <section className="benefits-section section-container" id="prednosti">
      <div className="section-heading">
        <span className="eyebrow">PREDNOSTI PLATFORME</span>
        <h2>
          Vse pomembne povezave.
          <br />
          <span>Na enem mestu.</span>
        </h2>
        <p>
          Namesto pregledovanja številnih evidenc omogočamo enostavnejši dostop
          do informacij, ki pomagajo razumeti poslovne odnose.
        </p>
      </div>

      <div className="benefits-grid">
        {PREDNOSTI.map((prednost) => (
          <article className="benefit-card" key={prednost.stevilka}>
            <div className="benefit-card-top">
              <span className="benefit-icon">{prednost.ikona}</span>
              <span className="benefit-number">{prednost.stevilka}</span>
            </div>
            <h3>{prednost.naslov}</h3>
            <p>{prednost.opis}</p>
            <span className="card-arrow">↗</span>
          </article>
        ))}
      </div>
    </section>
  );
}

export default Prednosti;
