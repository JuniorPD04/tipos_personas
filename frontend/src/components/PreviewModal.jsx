import { TYPE_META } from "../constants";
import Modal from "./Modal";

function isYes(value) {
  return typeof value === "string" && value.trim().toLowerCase().startsWith("s");
}

export default function PreviewModal({ data, onConfirm, onCancel, confirming, error }) {
  return (
    <Modal title="Confirmar datos a procesar" onClose={onCancel} width={880}>
      <div className="preview-summary">
        <div>
          <span className="preview-summary-value mono">{data.row_count}</span>
          <span className="preview-summary-label">respuestas</span>
        </div>
        <div>
          <span className="preview-summary-value mono">{data.questions_detected}/32</span>
          <span className="preview-summary-label">preguntas reconocidas</span>
        </div>
        <div className="preview-summary-file">
          <span className="preview-summary-label">Archivo</span>
          <span className="mono">{data.filename}</span>
        </div>
      </div>

      {data.unmatched_columns.length > 0 && (
        <p className="preview-warning">
          No se reconocieron {data.unmatched_columns.length} columna(s): {data.unmatched_columns.join(", ")}. Se
          ignorarán en el cálculo.
        </p>
      )}

      {error && <p className="preview-error">{error}</p>}

      <div className="preview-table-wrap">
        <table className="preview-table">
          <thead>
            <tr>
              <th className="sticky-col">Nombre</th>
              <th>Correo</th>
              {data.preview_columns.map((col) => (
                <th key={col.key} style={{ background: TYPE_META[col.type].soft, color: TYPE_META[col.type].color }}>
                  {col.short_label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.preview_rows.map((row) => (
              <tr key={row.row_index}>
                <td className="sticky-col">{row.nombre}</td>
                <td className="mono">{row.correo}</td>
                {data.preview_columns.map((col) => {
                  const value = row.answers[col.short_label];
                  return (
                    <td key={col.key} className={isYes(value) ? "answer-yes" : "answer-no"}>
                      {value}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="modal-actions">
        <button className="btn btn-ghost" onClick={onCancel} disabled={confirming}>
          Cancelar
        </button>
        <button className="btn btn-primary" onClick={onConfirm} disabled={confirming}>
          {confirming ? "Clasificando…" : "Confirmar y clasificar"}
        </button>
      </div>
    </Modal>
  );
}
