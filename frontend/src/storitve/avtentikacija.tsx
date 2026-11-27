import { FirebaseError } from "firebase/app";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  updateProfile,
} from "firebase/auth";
import { avtentikacija } from "../firebase";

export async function registracija(ime: string, eposta: string, geslo: string) {
  const rezultat = await createUserWithEmailAndPassword(avtentikacija, eposta, geslo);
  await updateProfile(rezultat.user, { displayName: ime });
  return rezultat.user;
}

export async function prijava(eposta: string, geslo: string) {
  const rezultat = await signInWithEmailAndPassword(avtentikacija, eposta, geslo);
  return rezultat.user;
}

export async function prijavaZGooglom() {
  const rezultat = await signInWithPopup(avtentikacija, new GoogleAuthProvider());
  return rezultat.user;
}

export function odjava() {
  return signOut(avtentikacija);
}

export function besediloNapake(napaka: unknown): string {
  if (napaka instanceof FirebaseError) {
    switch (napaka.code) {
      case "auth/invalid-credential":
      case "auth/user-not-found":
      case "auth/wrong-password":
        return "Napačna e-pošta ali geslo.";
      case "auth/invalid-email":
        return "E-poštni naslov ni veljaven.";
      case "auth/email-already-in-use":
        return "Račun s to e-pošto že obstaja.";
      case "auth/weak-password":
        return "Geslo je prekratko (najmanj 6 znakov).";
      case "auth/too-many-requests":
        return "Preveč poskusov. Poskusite znova čez nekaj minut.";
      case "auth/network-request-failed":
        return "Ni povezave z internetom.";
      case "auth/popup-closed-by-user":
      case "auth/cancelled-popup-request":
        return "Prijava je bila prekinjena.";
      case "auth/popup-blocked":
        return "Brskalnik je blokiral pojavno okno. Dovolite ga in poskusite znova.";
    }
  }
  return "Prišlo je do napake. Poskusite znova.";
}
