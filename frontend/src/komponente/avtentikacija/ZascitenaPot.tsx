import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAvtentikacija } from "./AvtentikacijaKontekst";

interface ZascitenaPotProps {
  children: ReactElement;
}

function ZascitenaPot({ children }: ZascitenaPotProps) {
  const { uporabnik, nalaganje } = useAvtentikacija();

  if (nalaganje) return null;
  if (!uporabnik) return <Navigate to="/prijava" replace />;

  return children;
}

export default ZascitenaPot;
