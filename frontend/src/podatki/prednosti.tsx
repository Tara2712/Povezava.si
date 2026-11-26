export interface Prednost {
  stevilka: string;
  ikona: string;
  naslov: string;
  opis: string;
}

export const PREDNOSTI: Prednost[] = [
  {
    stevilka: "01",
    ikona: "⌕",
    naslov: "Iskanje podjetij in oseb",
    opis: "Hitro poiščite podjetja, osebe in pomembne informacije iz javno dostopnih podatkovnih virov.",
  },
  {
    stevilka: "02",
    ikona: "◎",
    naslov: "Odkrivanje povezav",
    opis: "Raziskujte poslovne in osebne povezave ter odkrijte odnose, ki jih v običajnih evidencah težko opazite.",
  },
  {
    stevilka: "03",
    ikona: "⌘",
    naslov: "Vizualizacija omrežij",
    opis: "Zapletene odnose predstavite s preglednimi grafi, ki omogočajo lažje razumevanje podatkov.",
  },
  {
    stevilka: "04",
    ikona: "↗",
    naslov: "Podatki na enem mestu",
    opis: "Informacije iz različnih javnih virov združite v enotno in razumljivo uporabniško izkušnjo.",
  },
];
