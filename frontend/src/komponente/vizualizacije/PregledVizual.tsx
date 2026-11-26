import "./PregledVizual.css";

function PregledVizual() {
  return (
    <div className="dashboard-visual">
      <div className="dashboard-top">
        <div>
          <span className="dashboard-eyebrow">PREGLED PODJETJA</span>
          <h3>Podjetje d.o.o.</h3>
        </div>
        <span className="dashboard-badge">Aktivno</span>
      </div>

      <div className="dashboard-metrics">
        <div>
          <span>Povezane osebe</span>
          <strong>12</strong>
          <small>Najdene povezave</small>
        </div>
        <div>
          <span>Povezana podjetja</span>
          <strong>8</strong>
          <small>Poslovni odnosi</small>
        </div>
      </div>

      <div className="dashboard-divider" />

      <div className="dashboard-chart-header">
        <strong>Pregled povezav</strong>
        <span>Vizualni prikaz</span>
      </div>

      <div className="mini-network">
        <div className="mini-lines">
          <span className="mini-line line-a" />
          <span className="mini-line line-b" />
          <span className="mini-line line-c" />
          <span className="mini-line line-d" />
        </div>
        <span className="mini-node mini-node-a">P</span>
        <span className="mini-node mini-node-b">O</span>
        <span className="mini-node mini-node-c">O</span>
        <span className="mini-node mini-node-d">P</span>
        <span className="mini-node mini-node-e">P</span>
      </div>

      <div className="dashboard-footer">
        <span>
          <i /> Podatki iz javnih virov
        </span>
        <span>Primer prikaza</span>
      </div>
    </div>
  );
}

export default PregledVizual;
