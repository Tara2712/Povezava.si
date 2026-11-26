export interface Korak {
  stevilka: string;
  naslov: string;
  opis: string;
}

export const KORAKI: Korak[] = [
  {
    stevilka: "01",
    naslov: "Poiščite subjekt",
    opis: "Vnesite ime podjetja ali osebe in začnite raziskovati razpoložljive javne podatke.",
  },
  {
    stevilka: "02",
    naslov: "Raziščite povezave",
    opis: "Oglejte si povezane osebe, podjetja in druge subjekte v interaktivnem omrežju.",
  },
  {
    stevilka: "03",
    naslov: "Odkrijte širšo sliko",
    opis: "Povežite informacije iz različnih virov in pridobite boljši vpogled v poslovno okolje.",
  },
];
