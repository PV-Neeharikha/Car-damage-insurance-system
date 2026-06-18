import { useLocation, Link } from "react-router-dom";
import "./ResultsPage.css";

function ResultsPage() {

  const location = useLocation();
  const results = location.state?.results;
  const sides = Object.entries(results).filter(([side]) => side !== "policy_type");
  const totalDamages = sides.reduce((sum, [, data]) => sum + data.damage_details.length,0);
  const severeCount = sides.reduce((sum, [, data]) => sum + data.damage_details.filter(item => item.severity === "severe").length,0);
  const moderateCount = sides.reduce((sum, [, data]) => sum +data.damage_details.filter(item => item.severity === "moderate").length,0);
  const minorCount = sides.reduce((sum, [, data]) => sum + data.damage_details.filter(item => item.severity === "minor").length,0);
  const handleDownload = async () => {
      const response = await fetch(
        "http://127.0.0.1:5000/download-report"
      );

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");

      link.href = url;
      link.download = "Damage_Report.pdf";

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
};
  if (!results) {
    return <h1>No Results Found</h1>;
  }

  return (
  <div className="results-page">

    <div className="summary-card">
        <div className="hero-section">

            <div>

                <h1 className="hero-title">
                    AI Vehicle Damage Assessment
                </h1>

                <p className="hero-subtitle">
                    Insurance-Oriented Multi-View Vehicle Inspection System
                </p>

            </div>

            <div className="policy-badge">

                {results.policy_type
                    ?.replace("_", " ")
                    .toUpperCase()}

            </div>

        </div>

        <div className="stats-row">

            <div className="stat-card">
                <h2>{sides.length}</h2>
                <span>Views</span>
            </div>

            <div className="stat-card">
                <h2>{totalDamages}</h2>
                <span>Damages</span>
            </div>

            <div className="stat-card">
                <h2>{severeCount}</h2>
                <span>Severe</span>
            </div>

            <div className="stat-card">
                <h2>{moderateCount}</h2>
                <span>Moderate</span>
            </div>

            <div className="stat-card">
                <h2>{minorCount}</h2>
                <span>Minor</span>
            </div>

        </div>
    </div>

    {Object.entries(results).map(([side, data]) => {

      if (side === "policy_type") return null;

      return (

        <div className="view-card" key={side}>

          <h2 className="view-title">
            {side} VIEW
          </h2>

          <div className="view-content">

            <div className="image-section">

              <img
                src={`http://127.0.0.1:5000/static/${data.image}`}
                alt={side}
              />

            </div>

            <div className="damage-section">

              {data.damage_details.map((item, index) => (

                <div
                  className="damage-card"
                  key={index}
                >

                  <div className="damage-title">
                    {item.display_name || item.damage}
                  </div>

                  <div className="damage-meta">
                        <span className={`severity-badge ${item.severity}`}>{item.severity.toUpperCase()}</span>
                        <span className="confidence">{(item.confidence * 100).toFixed(0)}%</span>
                    </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    })}
    <div className="button-container">

      <button className="action-btn primary-btn" onClick={handleDownload}>Download Report</button>

      <Link to="/">
        <button className="action-btn">
          Analyze Another Vehicle
        </button>
      </Link>

    </div>

  </div>
);
}

export default ResultsPage;