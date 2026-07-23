import Dropzone from "./Dropzone";

export default function UploadView({ onFile, loading, error }) {
  return (
    <section className="upload-section">
      <div className="upload-copy">
        <h2>Carga las respuestas del cuestionario</h2>
        <p className="section-sub">
          Sube el Excel exportado con las 32 preguntas Sí/No de FourSight. Antes de calcular nada te mostramos una
          vista previa para que confirmes que es el archivo correcto.
        </p>
      </div>
      <Dropzone onFile={onFile} disabled={loading} />
      {loading && <p className="upload-status mono">Leyendo archivo…</p>}
      {error && <p className="preview-error">{error}</p>}
    </section>
  );
}
