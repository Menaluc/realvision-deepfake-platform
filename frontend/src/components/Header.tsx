import { EyeIcon } from "./icons";

export function Header() {
    return (
        <div className="header-row">
            <div className="brand">
                <EyeIcon />
                <span className="wordmark">Real<span className="accent">Vision</span></span>
            </div>
            <a href="/" className="home-pill">Home</a>
        </div>
    );
}
