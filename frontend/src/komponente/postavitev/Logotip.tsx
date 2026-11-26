import "./Logotip.css";

interface LogotipProps {
  dodatenRazred?: string;
  ariaOznaka?: string;
}

function Logotip({ dodatenRazred, ariaOznaka }: LogotipProps) {
  const razred = dodatenRazred ? `brand ${dodatenRazred}` : "brand";

  return (
    <a className={razred} href="#home" aria-label={ariaOznaka}>
      <span className="brand-symbol">
        <span />
        <span />
        <span />
      </span>
      <span>
        Povezava<span className="brand-dot">.si</span>
      </span>
    </a>
  );
}

export default Logotip;
