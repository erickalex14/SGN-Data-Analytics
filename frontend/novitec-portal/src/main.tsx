import React from "react";
import ReactDOM from "react-dom/client";
import { AppProviders } from "@/app/providers/app-providers";
import { AppRouter } from "@/app/router";
import "@/styles/index.css";

// Punto de entrada principal del portal ejecutivo.
ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AppProviders>
      <AppRouter />
    </AppProviders>
  </React.StrictMode>,
);
