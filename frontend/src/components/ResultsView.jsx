import { useState } from "react";
import { TYPE_META } from "../constants";
import PersonCard from "./PersonCard";
import PersonDetailModal from "./PersonDetailModal";

function summarize(results) {
  const counts = { A: 0, B: 0, C: 0, D: 0, I: 0 };
  for (const p of results) {
    counts[p.is_integrador ? "I" : p.primary_types[0]] += 1;
  }
  return counts;
}

export default function ResultsView({ results, onCreateGroups, creatingGroups, error }) {
  const [selected, setSelected] = useState(null);
  const counts = summarize(results);

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>Clasificación por afinidad</h2>
          <p className="section-sub">{results.length} personas · haz clic en una tarjeta para ver el detalle completo</p>
        </div>
        <button className="btn btn-primary" onClick={onCreateGroups} disabled={creatingGroups}>
          {creatingGroups ? "Formando grupos…" : "Crear grupos"}
        </button>
      </div>

      {error && <p className="preview-error">{error}</p>}

      <div className="summary-strip">
        {["A", "B", "C", "D", "I"].map((t) => (
          <div key={t} className="summary-chip">
            <span className="summary-dot" style={{ background: TYPE_META[t].color }} />
            <span>{TYPE_META[t].label}</span>
            <span className="mono summary-count">{counts[t]}</span>
          </div>
        ))}
      </div>

      <div className="person-grid">
        {results.map((p) => (
          <PersonCard key={p.row_index} person={p} onOpen={setSelected} />
        ))}
      </div>

      {selected && <PersonDetailModal person={selected} onClose={() => setSelected(null)} />}
    </section>
  );
}
