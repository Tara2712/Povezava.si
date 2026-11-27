import { createContext, useContext } from "react";
import type { User } from "firebase/auth";

export interface AvtentikacijaVrednost {
  uporabnik: User | null;
  nalaganje: boolean;
}

export const AvtentikacijaKontekst = createContext<AvtentikacijaVrednost>({
  uporabnik: null,
  nalaganje: true,
});

export function useAvtentikacija() {
  return useContext(AvtentikacijaKontekst);
}
