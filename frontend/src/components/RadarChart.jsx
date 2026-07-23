import { TYPE_META } from "../constants";

// Axes follow the real FourSight process order clockwise from the top:
// Clarificador -> Ideador -> Desarrollador -> Implementador -> (back to Clarificador)
const AXES = [
  { key: "A", angle: -90 },
  { key: "B", angle: 0 },
  { key: "C", angle: 90 },
  { key: "D", angle: 180 },
];

function point(cx, cy, radius, angleDeg) {
  const rad = (angleDeg * Math.PI) / 180;
  return [cx + radius * Math.cos(rad), cy + radius * Math.sin(rad)];
}

export default function RadarChart({ scores, size = 120, integrador = false }) {
  const cx = size / 2;
  const cy = size / 2;
  const R = size * 0.36;

  const shapePoints = AXES.map(({ key, angle }) => {
    const value = Math.max(scores[key], 4); // floor so 0% still renders a visible vertex
    const [x, y] = point(cx, cy, (value / 100) * R, angle);
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
      {[0.5, 1].map((frac) => (
        <circle key={frac} cx={cx} cy={cy} r={R * frac} fill="none" stroke="var(--line)" strokeWidth="1" />
      ))}
      {AXES.map(({ key, angle }) => {
        const [x, y] = point(cx, cy, R, angle);
        return <line key={key} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--line)" strokeWidth="1" />;
      })}
      <polygon
        points={shapePoints}
        fill={integrador ? "var(--i)" : "var(--ink)"}
        fillOpacity="0.12"
        stroke={integrador ? "var(--i)" : "var(--ink)"}
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      {AXES.map(({ key, angle }) => {
        const value = Math.max(scores[key], 4);
        const [x, y] = point(cx, cy, (value / 100) * R, angle);
        return <circle key={key} cx={x} cy={y} r="3" fill={TYPE_META[key].color} />;
      })}
    </svg>
  );
}
