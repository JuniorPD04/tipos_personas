import { TYPE_META, TYPE_ORDER, classificationTypes } from "../constants";
import Modal from "./Modal";
import RadarChart from "./RadarChart";
import TypeChip from "./TypeChip";

export default function PersonDetailModal({ person, onClose }) {
  const primaryTypes = person.is_integrador ? ["I"] : classificationTypes(person.classification);

  return (
    <Modal title={person.nombre} onClose={onClose} width={620}>
      <p className="person-email mono" style={{ marginBottom: 20 }}>
        {person.correo}
      </p>

      <div className="detail-layout">
        <RadarChart scores={person.percentages} size={168} integrador={person.is_integrador} />

        <div className="score-list">
          {TYPE_ORDER.map((t) => (
            <div className="score-row" key={t}>
              <span className="score-row-label" style={{ color: TYPE_META[t].color }}>
                {TYPE_META[t].label}
              </span>
              <div className="score-bar-track">
                <div
                  className="score-bar-fill"
                  style={{ width: `${person.percentages[t]}%`, background: TYPE_META[t].color }}
                />
              </div>
              <span className="score-row-value mono">
                {person.scores[t]}/{person.max_per_type[t]}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="detail-chips">
        {person.is_integrador ? (
          <TypeChip type="I" />
        ) : (
          primaryTypes.map((t) => <TypeChip key={t} type={t} />)
        )}
      </div>

      <div className="detail-traits">
        {primaryTypes.map((t) => (
          <div className="trait-block" key={t} style={{ borderColor: TYPE_META[t].color }}>
            <h4 style={{ color: TYPE_META[t].color }}>{TYPE_META[t].label}</h4>
            <p className="trait-tagline">{TYPE_META[t].tagline}</p>
            <dl>
              <dt>Son</dt>
              <dd>{TYPE_META[t].son}</dd>
              <dt>Necesitan</dt>
              <dd>{TYPE_META[t].necesitan}</dd>
              <dt>Pueden frustrar a otros</dt>
              <dd>{TYPE_META[t].frustran}</dd>
              <dt>Riesgo</dt>
              <dd>{TYPE_META[t].riesgo}</dd>
            </dl>
          </div>
        ))}
      </div>
    </Modal>
  );
}
