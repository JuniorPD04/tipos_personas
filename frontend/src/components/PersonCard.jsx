import { TYPE_META, classificationTypes } from "../constants";
import RadarChart from "./RadarChart";
import TypeChip from "./TypeChip";

function initials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join("")
    .toUpperCase();
}

export default function PersonCard({ person, onOpen }) {
  const types = classificationTypes(person.classification);
  const avatarColor = person.is_integrador ? TYPE_META.I.color : TYPE_META[types[0]].color;

  return (
    <button className="person-card" onClick={() => onOpen(person)}>
      <div className="person-card-top">
        <div className="avatar" style={{ "--avatar-color": avatarColor }}>
          {initials(person.nombre)}
        </div>
        <div className="person-card-id">
          <p className="person-name">{person.nombre}</p>
          <p className="person-email mono">{person.correo}</p>
        </div>
      </div>
      <RadarChart scores={person.percentages} size={104} integrador={person.is_integrador} />
      <div className="person-card-chips">
        {person.is_integrador ? (
          <TypeChip type="I" size="sm" />
        ) : (
          types.map((t) => <TypeChip key={t} type={t} size="sm" />)
        )}
      </div>
    </button>
  );
}
