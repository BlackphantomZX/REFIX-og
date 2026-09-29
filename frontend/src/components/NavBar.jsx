import { ChevronLeftIcon } from "./Icons";

export default function NavBar({ onBack, onContinue, continueLabel = "Continue", canContinue = true, showBack = false }) {
  return (
    <div className="navbar">
      <div className="navbar-inner">
        {showBack && (
          <button className="btn btn-ghost" onClick={onBack} aria-label="Go back">
            <ChevronLeftIcon />
          </button>
        )}
        <button className="btn btn-primary" onClick={onContinue} disabled={!canContinue}>
          {continueLabel}
        </button>
      </div>
    </div>
  );
}
