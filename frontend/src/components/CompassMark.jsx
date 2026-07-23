// The four FourSight preferences as four quadrant dots -- reused as the app's
// mark, and later as the literal layout logic for the radar chart.
export default function CompassMark({ size = 28 }) {
  const r = size * 0.16;
  const gap = size * 0.09;
  const positions = [
    { cx: size / 2 - gap - r, cy: size / 2 - gap - r, color: "var(--a)" },
    { cx: size / 2 + gap + r, cy: size / 2 - gap - r, color: "var(--b)" },
    { cx: size / 2 - gap - r, cy: size / 2 + gap + r, color: "var(--d)" },
    { cx: size / 2 + gap + r, cy: size / 2 + gap + r, color: "var(--c)" },
  ];
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden="true">
      {positions.map((p, i) => (
        <circle key={i} cx={p.cx} cy={p.cy} r={r} fill={p.color} />
      ))}
    </svg>
  );
}
