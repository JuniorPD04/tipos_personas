"""Excel parsing, FourSight scoring and classification."""
import io
from datetime import datetime, date

import pandas as pd

from .questions import METADATA_COLUMNS, QUESTION_MAP, TYPE_NAMES, normalize

INTEGRADOR_THRESHOLD_PCT = 75.0  # all four preferences >= 75% affinity -> Integrador
YES_VALUES = {"si", "sí", "yes", "y", "1", "true", "x"}


def _is_yes(value) -> bool:
    if value is None:
        return False
    return normalize(str(value)) in YES_VALUES


def _json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if pd.isna(value):
        return None
    return value


class InvalidWorkbookError(ValueError):
    pass


def parse_excel(file_bytes: bytes) -> dict:
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
    except Exception as exc:  # noqa: BLE001 - surface as a clean validation error
        raise InvalidWorkbookError(f"No se pudo leer el archivo Excel: {exc}") from exc

    if df.empty:
        raise InvalidWorkbookError("El archivo no contiene filas de datos.")

    metadata_columns: dict[str, str] = {}
    question_columns: dict[str, str] = {}
    unmatched_columns: list[str] = []

    for col in df.columns:
        norm = normalize(col)
        if norm in METADATA_COLUMNS:
            metadata_columns[col] = METADATA_COLUMNS[norm]
        elif norm in QUESTION_MAP:
            question_columns[col] = QUESTION_MAP[norm]
        else:
            unmatched_columns.append(str(col))

    if not question_columns:
        raise InvalidWorkbookError(
            "No se reconoció ninguna de las 32 preguntas del cuestionario FourSight "
            "en las columnas del archivo."
        )

    name_col = next((c for c, k in metadata_columns.items() if k == "nombre"), None)
    email_col = next((c for c, k in metadata_columns.items() if k == "correo"), None)

    rows = []
    for idx, raw_row in df.iterrows():
        rows.append(
            {
                "row_index": int(idx),
                "nombre": str(raw_row[name_col]) if name_col else f"Fila {idx + 1}",
                "correo": str(raw_row[email_col]) if email_col else "",
                "answers": {col: _json_safe(raw_row[col]) for col in question_columns},
            }
        )

    return {
        "row_count": len(rows),
        "metadata_columns": list(metadata_columns.keys()),
        "question_columns": question_columns,
        "unmatched_columns": unmatched_columns,
        "questions_detected": len(question_columns),
        "rows": rows,
    }


def classify_rows(rows: list[dict], question_columns: dict[str, str]) -> list[dict]:
    # how many matched columns feed each type (should be 8/8/8/8 on a clean file)
    max_per_type = {"A": 0, "B": 0, "C": 0, "D": 0}
    for col_type in question_columns.values():
        max_per_type[col_type] += 1

    results = []
    for row in rows:
        scores = {"A": 0, "B": 0, "C": 0, "D": 0}
        for col, col_type in question_columns.items():
            if _is_yes(row["answers"].get(col)):
                scores[col_type] += 1

        percentages = {
            t: round((scores[t] / max_per_type[t]) * 100, 1) if max_per_type[t] else 0.0
            for t in scores
        }

        is_integrador = all(percentages[t] >= INTEGRADOR_THRESHOLD_PCT for t in scores)
        top_score = max(scores.values())
        primary_types = [t for t, s in scores.items() if s == top_score]

        if is_integrador:
            classification = "I"
            label = TYPE_NAMES["I"]
        elif len(primary_types) == 1:
            classification = primary_types[0]
            label = TYPE_NAMES[primary_types[0]]
        else:
            classification = "".join(sorted(primary_types))
            label = " / ".join(TYPE_NAMES[t] for t in sorted(primary_types))

        results.append(
            {
                "row_index": row["row_index"],
                "nombre": row["nombre"],
                "correo": row["correo"],
                "scores": scores,
                "max_per_type": max_per_type,
                "percentages": percentages,
                "is_integrador": is_integrador,
                "primary_types": sorted(primary_types),
                "classification": classification,
                "classification_label": label,
            }
        )

    return results
