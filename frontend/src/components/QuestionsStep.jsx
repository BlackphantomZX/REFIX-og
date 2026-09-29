export default function QuestionsStep({ repair, device, answers, onAnswer, problemIndex, totalProblems }) {
  const currentAnswers = answers[repair.id] || {};

  return (
    <main className="step-main">
      <p className="step-eyebrow">
        {device.brand} {device.model}
      </p>
      <h1 className="step-title">A little more about the {repair.name.toLowerCase()}</h1>
      <p className="step-sub">
        This helps narrow down the likely repair and how confident we can be in the price.
      </p>
      {totalProblems > 1 && (
        <span className="subproblem-tag">
          Issue {problemIndex + 1} of {totalProblems}
        </span>
      )}

      <div>
        {repair.questions.map((q) => (
          <div className="question-block" key={q.key}>
            <p className="q-label">{q.label}</p>
            <div className="option-grid">
              {q.options.map((o) => (
                <button
                  key={o.value}
                  className={`option-pill ${currentAnswers[q.key] === o.value ? "selected" : ""}`}
                  onClick={() => onAnswer(repair.id, q.key, o.value)}
                >
                  <span>{o.label}</span>
                  {o.sub ? <span className="sub">{o.sub}</span> : null}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
