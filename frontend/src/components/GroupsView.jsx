import { useState } from "react";
import { TYPE_META } from "../constants";
import PersonDetailModal from "./PersonDetailModal";

function CompositionBar({ composition, size }) {
  return (
    <div className="composition-bar">
      {["A", "B", "C", "D", "I"].map((t) =>
        composition[t] > 0 ? (
          <div
            key={t}
            className="composition-segment"
            style={{ width: `${(composition[t] / size) * 100}%`, background: TYPE_META[t].color }}
            title={`${TYPE_META[t].label}: ${composition[t]}`}
          />
        ) : null
      )}
    </div>
  );
}

export default function GroupsView({ groups }) {
  const [selected, setSelected] = useState(null);

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>Grupos balanceados</h2>
          <p className="section-sub">
            {groups.length} grupos · cada uno mezcla perfiles distintos siempre que la clasificación lo permite
          </p>
        </div>
      </div>

      <div className="group-grid">
        {groups.map((group) => (
          <div className="group-card" key={group.id}>
            <div className="group-card-head">
              <h3>{group.nombre}</h3>
              <span className="mono group-size">{group.size} integrantes</span>
            </div>
            <CompositionBar composition={group.composition} size={group.size} />
            <ul className="group-members">
              {group.members.map((m) => {
                const type = m.is_integrador ? "I" : m.primary_types[0];
                return (
                  <li key={m.row_index}>
                    <button className="member-row" onClick={() => setSelected(m)}>
                      <span className="member-dot" style={{ background: TYPE_META[type].color }} />
                      <span className="member-name">{m.nombre}</span>
                      <span className="member-type mono">{TYPE_META[type].short}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      {selected && <PersonDetailModal person={selected} onClose={() => setSelected(null)} />}
    </section>
  );
}
