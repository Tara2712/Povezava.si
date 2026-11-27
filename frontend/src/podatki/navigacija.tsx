export interface NavigacijskaPovezava {
  href: string;
  oznaka: string;
}

export const NAVIGACIJSKE_POVEZAVE: NavigacijskaPovezava[] = [
  { href: "#prednosti", oznaka: "Prednosti" },
  { href: "#platforma", oznaka: "Platforma" },
  { href: "/prijava", oznaka: "Ustvari povezavo" },
  { href: "/prijava", oznaka: "Poišči povezavo" },
  
];
