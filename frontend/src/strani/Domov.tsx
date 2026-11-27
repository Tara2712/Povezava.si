import Glava from "../komponente/postavitev/Glava";
import Noga from "../komponente/postavitev/Noga";
import Junak from "../komponente/razdelki/Junak";
import TrakVirov from "../komponente/razdelki/TrakVirov";
import Prednosti from "../komponente/razdelki/Prednosti";
import SirsaSlika from "../komponente/razdelki/SirsaSlika";

function Domov() {
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

export default Domov;
