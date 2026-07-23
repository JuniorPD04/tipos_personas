const STEPS = [
  { key: "upload", label: "Cargar archivo" },
  { key: "classification", label: "Clasificación" },
  { key: "groups", label: "Grupos" },
];

export default function Stepper({ stage, unlocked, onSelect }) {
  const activeIndex = STEPS.findIndex((s) => s.key === stage);

  return (
    <nav className="stepper" aria-label="Progreso">
      {STEPS.map((step, i) => {
        const isUnlocked = unlocked.includes(step.key);
        const isActive = step.key === stage;
        return (
          <button
            key={step.key}
            className={`step ${isActive ? "step-active" : ""} ${isUnlocked ? "" : "step-locked"}`}
            onClick={() => isUnlocked && onSelect(step.key)}
            disabled={!isUnlocked}
          >
            <span className="step-index mono">{String(i + 1).padStart(2, "0")}</span>
            <span className="step-label">{step.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
