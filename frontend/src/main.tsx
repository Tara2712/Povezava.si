import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { BrowserRouter } from "react-router-dom";
import AvtentikacijaPonudnik from "./komponente/avtentikacija/AvtentikacijaPonudnik";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AvtentikacijaPonudnik>
        <App />
      </AvtentikacijaPonudnik> 
    </BrowserRouter>
  </StrictMode>,
)
