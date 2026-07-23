from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .groups import build_groups
from .scoring import InvalidWorkbookError, classify_rows, parse_excel
from .storage import create_session, get_session, update_session

app = FastAPI(title="FourSight Team Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "El archivo debe ser un Excel (.xlsx o .xls).")

    content = await file.read()
    try:
        parsed = parse_excel(content)
    except InvalidWorkbookError as exc:
        raise HTTPException(400, str(exc)) from exc

    session_id = create_session(
        {
            "stage": "uploaded",
            "filename": file.filename,
            "rows": parsed["rows"],
            "question_columns": parsed["question_columns"],
            "unmatched_columns": parsed["unmatched_columns"],
        }
    )

    # short labels (A1..A8, B1..B8, ...) keep the preview table compact
    counters = {"A": 0, "B": 0, "C": 0, "D": 0}
    col_short = {}
    preview_columns = []
    for col, t in parsed["question_columns"].items():
        counters[t] += 1
        short = f"{t}{counters[t]}"
        col_short[col] = short
        preview_columns.append({"key": col, "short_label": short, "type": t})

    preview_rows = [
        {
            "row_index": r["row_index"],
            "nombre": r["nombre"],
            "correo": r["correo"],
            "answers": {col_short[col]: r["answers"].get(col) for col in parsed["question_columns"]},
        }
        for r in parsed["rows"]
    ]

    return {
        "session_id": session_id,
        "filename": file.filename,
        "row_count": parsed["row_count"],
        "questions_detected": parsed["questions_detected"],
        "unmatched_columns": parsed["unmatched_columns"],
        "preview_columns": preview_columns,
        "preview_rows": preview_rows,
    }


@app.post("/api/{session_id}/confirm")
async def confirm(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(404, "La sesión expiró o no existe. Vuelve a subir el archivo.")

    results = classify_rows(session["rows"], session["question_columns"])
    update_session(session_id, stage="classified", results=results)
    return {"session_id": session_id, "results": results}


@app.post("/api/{session_id}/groups")
async def create_groups(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(404, "La sesión expiró o no existe. Vuelve a subir el archivo.")

    results = session.get("results")
    if not results:
        raise HTTPException(400, "Primero confirma y clasifica los datos antes de crear grupos.")

    groups = build_groups(results)
    update_session(session_id, stage="grouped", groups=groups)
    return {"session_id": session_id, "groups": groups}
