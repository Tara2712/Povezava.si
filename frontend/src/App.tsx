import { Routes, Route } from "react-router-dom";

import "./style/spremenljivke.css";
import "./style/osnova.css";
import "./style/gumbi.css";
import "./style/naslovi.css";
import "./style/navPovezave.css";

import Domov from "./strani/Domov";
import Prijava from "./strani/Prijava";
import Registracija from "./strani/Registracija";
import Aplikacija from "./strani/Aplikacija";
import ZascitenaPot from "./komponente/avtentikacija/ZascitenaPot";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Domov />} />
      <Route path="/prijava" element={<Prijava />} />
      <Route path="/registracija" element={<Registracija />} />
      <Route
        path="/app"
        element={
          <ZascitenaPot>
            <Aplikacija />
          </ZascitenaPot>
        }
      />
    </Routes>
  );
}

export default App;
