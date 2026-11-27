import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const konfiguracija = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

if (!konfiguracija.apiKey) {
  console.error(
    "Manjka Firebase konfiguracija. Preverite datoteko frontend/.env in ponovno zaženite npm run dev."
  );
}

const aplikacija = initializeApp(konfiguracija);

export const avtentikacija = getAuth(aplikacija);
