import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { prijava, prijavaZGooglom, besediloNapake } from "../storitve/avtentikacija";
import "./Avtentikacija.css";

function Prijava() {
  const navigiraj = useNavigate();
  const [eposta, setEposta] = useState("");
  const [geslo, setGeslo] = useState("");
  const [napaka, setNapaka] = useState("");
  const [posiljanje, setPosiljanje] = useState(false);

  async function oddajObrazec(dogodek: FormEvent<HTMLFormElement>) {
    dogodek.preventDefault();
    setNapaka("");
    setPosiljanje(true);

    try {
      await prijava(eposta, geslo);
      navigiraj("/");
    } catch (n) {
      setNapaka(besediloNapake(n));
    } finally {
      setPosiljanje(false);
    }
  }

  async function klikGoogle() {
    setNapaka("");
    setPosiljanje(true);

    try {
      await prijavaZGooglom();
      navigiraj("/");
    } catch (n) {
      setNapaka(besediloNapake(n));
    } finally {
      setPosiljanje(false);
    }
  }

  return (
    <main className="avtentikacija">
      <div className="avtentikacija-kartica">
        <Link className="avtentikacija-nazaj" to="/">
          ← Nazaj
        </Link>

        <h1>Prijava</h1>
        <p className="avtentikacija-opis">Dobrodošli nazaj v Povezava.si.</p>

        <form className="avtentikacija-obrazec" onSubmit={oddajObrazec}>
          <label>
            E-pošta
            <input
              type="email"
              value={eposta}
              onChange={(e) => setEposta(e.target.value)}
              autoComplete="email"
              required
            />
          </label>

          <label>
            Geslo
            <input
              type="password"
              value={geslo}
              onChange={(e) => setGeslo(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>

          {napaka && <p className="avtentikacija-napaka">{napaka}</p>}

          <button className="button-primary" type="submit" disabled={posiljanje}>
            {posiljanje ? "Prijavljam ..." : "Prijava"}
          </button>
        </form>

        <div className="avtentikacija-locilo">
          <span>ali</span>
        </div>

        <button
          className="avtentikacija-google"
          type="button"
          onClick={klikGoogle}
          disabled={posiljanje}
        >
          Nadaljuj z Googlom
        </button>

        <p className="avtentikacija-povezava">
          Nimate računa? <Link to="/registracija">Registrirajte se</Link>
        </p>
      </div>
    </main>
  );
}

export default Prijava;
