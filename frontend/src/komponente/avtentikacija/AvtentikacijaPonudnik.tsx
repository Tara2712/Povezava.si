import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { onAuthStateChanged } from "firebase/auth";
import type { User } from "firebase/auth";
import { avtentikacija } from "../../firebase";
import { AvtentikacijaKontekst } from "./AvtentikacijaKontekst";

interface AvtentikacijaPonudnikProps {
  children: ReactNode;
}

function AvtentikacijaPonudnik({ children }: AvtentikacijaPonudnikProps) {
  const [uporabnik, setUporabnik] = useState<User | null>(null);
  const [nalaganje, setNalaganje] = useState(true);

  useEffect(() => {
    // Firebase javi, ko se uporabnik prijavi, odjavi ali ko se stran naloži
    const odjaviSe = onAuthStateChanged(avtentikacija, (trenutni) => {
      setUporabnik(trenutni);
      setNalaganje(false);
    });
    return odjaviSe;
  }, []);

  return (
    <AvtentikacijaKontekst.Provider value={{ uporabnik, nalaganje }}>
      {children}
    </AvtentikacijaKontekst.Provider>
  );
}

export default AvtentikacijaPonudnik;
