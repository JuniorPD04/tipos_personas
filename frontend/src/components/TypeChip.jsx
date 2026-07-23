import { TYPE_META } from "../constants";

export default function TypeChip({ type, size = "md" }) {
  const meta = TYPE_META[type];
  return (
    <span className={`type-chip type-chip-${size}`} style={{ "--chip-color": meta.color, "--chip-soft": meta.soft }}>
      {meta.label}
    </span>
  );
}
