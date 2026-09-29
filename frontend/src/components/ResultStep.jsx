import { fmtINR, cap } from "../services/format";
import { REGIONS } from "../services/regions";
import { CopyIcon, EditIcon, RefreshIcon } from "./Icons";

const CONFIDENCE_COPY = {
  high: "Based on standardized pricing for this repair and clear answers about the condition.",
  moderate: "Based on typical pricing for this repair — some details could shift the final price.",
  low: "This repair type is harder to price remotely, or some answers were uncertain.",
};

export default function ResultStep({
  loading,
  error,
  estimate,
  region,
  setRegion,
  deviceValueInput,
  setDeviceValueInput,
  onRetry,
  onModify,
  onStartNew,
  onShare,
}) {
  return (
    <main className="step-main">
      <p className="step-eyebrow">Your estimate</p>

      {loading && (
        <div className="state-banner loading">
          <span className="spinner" />
          Calculating estimate...
        </div>
      )}

      {!loading && error && (
        <>
          <div className="state-banner error">{error}</div>
          <div className="result-actions">
            <button className="action-btn" onClick={onRetry}>
              <RefreshIcon />
              Try again
            </button>
            <button className="action-btn" onClick={onModify}>
              <EditIcon />
              Modify answers
            </button>
          </div>
        </>
      )}

      {!loading && !error && estimate && (
        <>
          <div className="result-hero">
            <div className={`confidence-badge ${estimate.confidence}`}>
              <span className="dot" />
              {cap(estimate.confidence)} confidence
            </div>
            <p className="result-device">{estimate.device}</p>
            <p className="result-issue">{estimate.repairs.join(", ")}</p>
            <div className="price-range mono">
              {fmtINR(estimate.minimum)} – {fmtINR(estimate.maximum)}
            </div>
            <p className="price-caption">
              Estimated repair cost
              {estimate.region ? ` · ${REGIONS.find((r) => r.id === estimate.region)?.label || estimate.region} pricing` : ""}
            </p>
            <div className="result-meta-row">
              <div className="result-meta-item">
                <p className="result-meta-label">Repair time</p>
                <p className="result-meta-value">{estimate.repair_time}</p>
              </div>
              <div className="result-meta-item">
                <p className="result-meta-label">Likely repair</p>
                <p className="result-meta-value">{estimate.likely_repair}</p>
              </div>
            </div>
          </div>

          <div className="section-card">
            <h3>Cost breakdown</h3>
            <table className="breakdown-table">
              <tbody>
                <tr>
                  <td>Replacement part(s)</td>
                  <td>
                    {fmtINR(estimate.breakdown.parts_min)}–{fmtINR(estimate.breakdown.parts_max)}
                  </td>
                </tr>
                <tr>
                  <td>Labor</td>
                  <td>
                    {fmtINR(estimate.breakdown.labor_min)}–{fmtINR(estimate.breakdown.labor_max)}
                  </td>
                </tr>
                <tr className="total">
                  <td>Estimated total</td>
                  <td>
                    {fmtINR(estimate.minimum)}–{fmtINR(estimate.maximum)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="section-card">
            <h3>Why this confidence level</h3>
            <p className="confidence-explain">{CONFIDENCE_COPY[estimate.confidence]}</p>
            {estimate.repair_items
              .filter((item) => item.note)
              .map((item) => (
                <p className="confidence-explain" key={item.repair_id}>
                  • {item.note}
                </p>
              ))}
          </div>

          <div className="section-card">
            <h3>Repair vs. device value</h3>
            {estimate.repair_vs_value_pct !== null && estimate.repair_vs_value_pct !== undefined ? (
              <>
                <div className="value-compare-pct">{estimate.repair_vs_value_pct}%</div>
                <div className="value-compare-bar">
                  <div
                    className="value-compare-fill"
                    style={{ width: `${Math.min(estimate.repair_vs_value_pct, 100)}%` }}
                  />
                </div>
                <div className="value-compare-labels">
                  <span>Repair: {fmtINR((estimate.minimum + estimate.maximum) / 2)}</span>
                  <span>Device value: {fmtINR(estimate.device_value_estimate)}</span>
                </div>
                <p className="confidence-explain" style={{ marginTop: 10 }}>
                  Repair cost is approximately {estimate.repair_vs_value_pct}% of the estimated current device
                  value.
                </p>
              </>
            ) : (
              <p className="confidence-explain">Add an approximate device value to compare it with the repair cost.</p>
            )}
            <div className="value-input-row">
              <label htmlFor="deviceValueInput">Device value (₹)</label>
              <input
                id="deviceValueInput"
                type="number"
                inputMode="numeric"
                placeholder="e.g. 20000"
                value={deviceValueInput}
                onChange={(e) => setDeviceValueInput(e.target.value)}
              />
            </div>
          </div>

          <div className="section-card">
            <h3>Region</h3>
            <div className="location-row">
              {REGIONS.map((r) => (
                <button key={r.id} className={`chip ${region === r.id ? "active" : ""}`} onClick={() => setRegion(r.id)}>
                  {r.label}
                </button>
              ))}
            </div>
            <p className="confidence-explain">City is optional — pricing is India-wide unless you narrow it down.</p>
          </div>

          <div className="disclaimer">
            <strong>Estimate only.</strong> {estimate.disclaimer}
          </div>

          <div className="result-actions">
            <button className="action-btn" onClick={onShare}>
              <CopyIcon />
              Share
            </button>
            <button className="action-btn" onClick={onModify}>
              <EditIcon />
              Modify answers
            </button>
            <button className="action-btn" onClick={onStartNew}>
              <RefreshIcon />
              Start new
            </button>
          </div>
        </>
      )}
    </main>
  );
}
