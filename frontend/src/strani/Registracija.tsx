import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registracija, prijavaZGooglom, besediloNapake } from "../storitve/avtentikacija";
import "./Avtentikacija.css";

const NAJMANJSA_DOLZINA_GESLA = 6;

function Registracija() {
  const navigiraj = useNavigate();
  const [ime, setIme] = useState("");
  const [eposta, setEposta] = useState("");
  const [geslo, setGeslo] = useState("");
  const [ponovljenoGeslo, setPonovljenoGeslo] = useState("");
  const [napaka, setNapaka] = useState("");
  const [posiljanje, setPosiljanje] = useState(false);

  async function oddajObrazec(dogodek: FormEvent<HTMLFormElement>) {
    dogodek.preventDefault();
    setNapaka("");

    if (geslo.length < NAJMANJSA_DOLZINA_GESLA) {
      setNapaka(`Geslo mora imeti najmanj ${NAJMANJSA_DOLZINA_GESLA} znakov.`);
      return;
    }
    if (geslo !== ponovljenoGeslo) {
      setNapaka("Gesli se ne ujemata.");
      return;
    }

    setPosiljanje(true);
    try {
      await registracija(ime.trim(), eposta, geslo);
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

        <h1>Registracija</h1>
        <p className="avtentikacija-opis">
          Ustvarite račun in začnite raziskovati povezave.
        </p>

        <form className="avtentikacija-obrazec" onSubmit={oddajObrazec}>
          <label>
            Ime in priimek
            <input
              type="text"
              value={ime}
              onChange={(e) => setIme(e.target.value)}
              autoComplete="name"
              required
            />
          </label>

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
              autoComplete="new-password"
              required
            />
          </label>

          <label>
            Ponovite geslo
            <input
              type="password"
              value={ponovljenoGeslo}
              onChange={(e) => setPonovljenoGeslo(e.target.value)}
              autoComplete="new-password"
              required
            />
          </label>

          {napaka && <p className="avtentikacija-napaka">{napaka}</p>}

          <button className="button-primary" type="submit" disabled={posiljanje}>
            {posiljanje ? "Ustvarjam račun ..." : "Ustvari račun"}
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
          Že imate račun? <Link to="/prijava">Prijavite se</Link>
        </p>
      </div>
    </main>
  );
}

export default Registracija;
