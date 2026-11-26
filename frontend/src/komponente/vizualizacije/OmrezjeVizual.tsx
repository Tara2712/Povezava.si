import "./OmrezjeVizual.css";

function OmrezjeVizual() {
  return (
    <div className="network-visual">
      <div className="network-glow" />

      <div className="network-label network-label-top">
        <span className="status-dot" />
        Vizualizacija povezav
      </div>

      <svg
        className="network-lines"
        viewBox="0 0 640 440"
        fill="none"
        aria-hidden="true"
      >
        <path d="M320 210 L150 105 L75 235 L195 345 L320 210" />
        <path d="M320 210 L490 95 L565 220 L450 355 L320 210" />
        <path d="M150 105 L320 65 L490 95" />
        <path d="M195 345 L320 390 L450 355" />
        <path d="M75 235 L320 210 L565 220" />
        <path d="M150 105 L195 345" />
        <path d="M490 95 L450 355" />
      </svg>

      <div className="network-node node-company">
        <span className="node-icon">P</span>
        <div>
          <strong>Podjetje d.o.o.</strong>
          <small>Podjetje</small>
        </div>
      </div>

      <div className="network-node node-person">
        <span className="node-icon">O</span>
        <div>
          <strong>Janez Novak</strong>
          <small>Oseba</small>
        </div>
      </div>

      <div className="network-node node-person-two">
        <span className="node-icon">M</span>
        <div>
          <strong>Marko Kovač</strong>
          <small>Oseba</small>
        </div>
      </div>

      <div className="network-node node-company-two">
        <span className="node-icon">S</span>
        <div>
          <strong>Drugo podjetje</strong>
          <small>Podjetje</small>
        </div>
      </div>

      <div className="network-node node-small node-small-one">
        <span />
      </div>
      <div className="network-node node-small node-small-two">
        <span />
      </div>

      <div className="network-center">
        <div className="center-ring">
          <span>PV</span>
        </div>
        <strong>Povezava.si</strong>
        <small>Podatki, ki povezujejo</small>
      </div>

      <div className="network-stat">
        <span className="stat-indicator" />
        <div>
          <strong>Omrežje povezav</strong>
          <small>Interaktivni pregled</small>
        </div>
      </div>
    </div>
  );
}

export default OmrezjeVizual;
