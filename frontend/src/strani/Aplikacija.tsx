import { useNavigate } from "react-router-dom";
import { useAvtentikacija } from "../komponente/avtentikacija/AvtentikacijaKontekst";
import { odjava } from "../storitve/avtentikacija";
import "./Avtentikacija.css";

function Aplikacija() {
  const navigiraj = useNavigate();
  const { uporabnik } = useAvtentikacija();

  async function klikOdjava() {
    navigiraj("/");
    odjava();
  }

  return (
    <main className="avtentikacija">
      <div className="avtentikacija-kartica">
        <h1>Pozdravljeni!</h1>
        <p className="avtentikacija-opis">
          Prijavljeni ste kot {uporabnik?.displayName || uporabnik?.email}.
        </p>

        <button
          className="button-primary avtentikacija-odjava"
          type="button"
          onClick={klikOdjava}
        >
          Odjava
        </button>
      </div>
    </main>
  );
}

export default Aplikacija;
