const STEP_LABELS = ["Device", "Problem", "Condition", "Estimate"];

export default function TopBar({ stepNumber, onReset }) {
  return (
    <div className="topbar">
      <div className="brand-row">
        <div className="brand">
          <span className="dot" />
          ReFix
        </div>
        {stepNumber > 1 ? (
          <button className="reset-link" onClick={onReset}>
            Start over
          </button>
        ) : (
          <span />
        )}
      </div>
      <div className="progress">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className={`seg ${i <= stepNumber ? "on" : ""}`} />
        ))}
      </div>
      <div className="progress-label">
        <span>Step {stepNumber} of 4</span>
        <span>{STEP_LABELS[stepNumber - 1]}</span>
      </div>
    </div>
  );
}
