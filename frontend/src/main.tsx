import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
// Global styles first, so view styles cascade after them as in the original page
import "./styles/base.css";
import App from "./App";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <App />
    </StrictMode>
);
