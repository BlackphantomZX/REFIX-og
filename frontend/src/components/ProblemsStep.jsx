import { CheckIcon } from "./Icons";

export default function ProblemsStep({ repairs, device, selectedProblems, onToggleProblem }) {
  return (
    <main className="step-main">
      <p className="step-eyebrow">
        {device.brand} {device.model}
      </p>
      <h1 className="step-title">What's wrong with it?</h1>
      <p className="step-sub">Select everything that applies — you can pick more than one.</p>
      <div className="multi-hint">Selected: {selectedProblems.length || "none yet"}</div>

      <div>
        {repairs.map((r) => (
          <button
            key={r.id}
            className={`row-btn ${selectedProblems.includes(r.id) ? "selected" : ""}`}
            onClick={() => onToggleProblem(r.id)}
          >
            <span className="row-main">
              <span className="row-title">{r.name}</span>
              <span className="row-meta">{r.examples}</span>
            </span>
            <span className="row-check">
              <CheckIcon />
            </span>
          </button>
        ))}
      </div>
    </main>
  );
}
