import "./style/spremenljivke.css";
import "./style/osnova.css";
import "./style/gumbi.css";
import "./style/naslovi.css";
import "./style/navPovezave.css";

import Glava from "./komponente/postavitev/Glava";
import Noga from "./komponente/postavitev/Noga";
import Junak from "./komponente/razdelki/Junak";
import TrakVirov from "./komponente/razdelki/TrakVirov";
import Prednosti from "./komponente/razdelki/Prednosti";
import SirsaSlika from "./komponente/razdelki/SirsaSlika";

function App() {
  return (
    <main>
      <Glava />
      <Junak />
      <TrakVirov />
      <Prednosti />
      <SirsaSlika />
      <Noga />
    </main>
  );
}

export default App;
