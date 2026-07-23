import { useRef, useState } from "react";

export default function Dropzone({ onFile, disabled }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  function handleFiles(files) {
    if (!files || !files.length) return;
    onFile(files[0]);
  }

  return (
    <div
      className={`dropzone ${dragging ? "dropzone-active" : ""} ${disabled ? "dropzone-disabled" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        if (!disabled) handleFiles(e.dataTransfer.files);
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (!disabled && (e.key === "Enter" || e.key === " ")) inputRef.current?.click();
      }}
    >
      <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
        <rect x="8" y="4" width="20" height="26" rx="1.5" fill="none" stroke="var(--ink)" strokeWidth="1.6" />
        <line x1="12" y1="11" x2="24" y2="11" stroke="var(--ink)" strokeWidth="1.4" />
        <line x1="12" y1="15" x2="24" y2="15" stroke="var(--ink)" strokeWidth="1.4" />
        <line x1="12" y1="19" x2="19" y2="19" stroke="var(--ink)" strokeWidth="1.4" />
        <circle cx="28" cy="28" r="9" fill="var(--paper)" stroke="var(--ink)" strokeWidth="1.6" />
        <line x1="28" y1="23.5" x2="28" y2="32.5" stroke="var(--ink)" strokeWidth="1.6" />
        <line x1="23.5" y1="28" x2="32.5" y2="28" stroke="var(--ink)" strokeWidth="1.6" />
      </svg>
      <p className="dropzone-title">Arrastra aquí el Excel de respuestas</p>
      <p className="dropzone-hint">.xlsx exportado del formulario · respuestas Sí / No · o haz clic para elegir el archivo</p>
      <input
        ref={inputRef}
        type="file"
        accept=".xlsx,.xls"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
