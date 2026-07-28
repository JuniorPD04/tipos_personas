"""Excel parsing, FourSight scoring and classification.

Classification engine ported from the "Claudia" prototype
(clasificar_foursight.py): raw yes-counts per type are converted to
z-scores relative to the whole uploaded cohort, so a student's profile is
judged against how the rest of the group answered rather than a fixed
percentage cutoff. Ties in the raw count are broken by z-score among the
tied types; the winner only sticks if it's clearly ahead of the next-best
z-score (UMBRAL_DOMINANCIA), otherwise the person is an Integrador.
"""
import io
import statistics
from datetime import datetime, date

import pandas as pd

from .questions import METADATA_COLUMNS, TYPE_NAMES, normalize

# Columns before the 32 question columns: Id, Hora de inicio,
# Hora de finalización, Correo electrónico, Nombre.
N_COLS_META = 5

# Question columns are matched by position, not by their text, in 8-question
# blocks that appear in this order left to right in the exported Excel.
PREGUNTAS_POR_BLOQUE = 8
ORDEN_BLOQUES = ["C", "D", "A", "B"]
N_PREGUNTAS = PREGUNTAS_POR_BLOQUE * len(ORDEN_BLOQUES)  # 32

# Minimum gap between the winning z-score and the next-best one for a type
# to be considered clearly dominant; below this the profile is Integrador.
UMBRAL_DOMINANCIA = 0.25

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

    n_columnas_esperadas = N_COLS_META + N_PREGUNTAS
    if len(df.columns) < n_columnas_esperadas:
        raise InvalidWorkbookError(
            f"Se esperaban al menos {n_columnas_esperadas} columnas "
            f"({N_COLS_META} de identificación + {N_PREGUNTAS} de preguntas), "
            f"pero el archivo solo tiene {len(df.columns)} columnas."
        )

    columns = list(df.columns)
    metadata_columns = columns[:N_COLS_META]
    question_cols_raw = columns[N_COLS_META : N_COLS_META + N_PREGUNTAS]
    unmatched_columns = [str(c) for c in columns[N_COLS_META + N_PREGUNTAS :]]

    # question type is decided purely by position within the 32-column block
    question_columns: dict[str, str] = {}
    for i, col in enumerate(question_cols_raw):
        question_columns[col] = ORDEN_BLOQUES[i // PREGUNTAS_POR_BLOQUE]

    # name/email columns are still located by header text among the metadata
    # columns, since their exact position can vary slightly between exports
    name_col = next(
        (c for c in metadata_columns if normalize(c) == "nombre"), None
    )
    email_col = next(
        (c for c in metadata_columns if normalize(c) == "correo electronico"), None
    )

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
        "metadata_columns": [str(c) for c in metadata_columns],
        "question_columns": question_columns,
        "unmatched_columns": unmatched_columns,
        "questions_detected": len(question_columns),
        "rows": rows,
    }


def classify_rows(rows: list[dict], question_columns: dict[str, str]) -> list[dict]:
    types = ["A", "B", "C", "D"]

    # how many matched columns feed each type (should be 8/8/8/8 on a clean file)
    max_per_type = {t: 0 for t in types}
    for col_type in question_columns.values():
        max_per_type[col_type] += 1

    raw_scores = []
    for row in rows:
        scores = {t: 0 for t in types}
        for col, col_type in question_columns.items():
            if _is_yes(row["answers"].get(col)):
                scores[col_type] += 1
        raw_scores.append(scores)

    # mean/pop-stdev of each type's raw score across the whole cohort; a
    # single respondent (or a type with zero variance) yields z = 0 since
    # there's no spread to compare against.
    medias = {t: statistics.mean(s[t] for s in raw_scores) for t in types}
    desviaciones = {t: statistics.pstdev(s[t] for s in raw_scores) for t in types}

    def z_score(t: str, value: int) -> float:
        desv = desviaciones[t]
        return 0.0 if desv == 0 else (value - medias[t]) / desv

    results = []
    for row, scores in zip(rows, raw_scores):
        percentages = {
            t: round((scores[t] / max_per_type[t]) * 100, 1) if max_per_type[t] else 0.0
            for t in types
        }
        z_scores = {t: round(z_score(t, scores[t]), 2) for t in types}

        maximo_crudo = max(scores.values())
        tied_raw_types = sorted(t for t in types if scores[t] == maximo_crudo)

        if len(tied_raw_types) == 1:
            ganador = tied_raw_types[0]
            decision_method = f"Sin empate en crudo. Tipo {ganador} domina con puntaje {maximo_crudo}."
        else:
            candidatos_ordenados = sorted(tied_raw_types, key=lambda t: z_scores[t], reverse=True)
            ganador = candidatos_ordenados[0]
            cadena_z = " > ".join(f"{t}={z_scores[t]:.2f}" for t in candidatos_ordenados)
            decision_method = (
                f"Empate en crudo entre {', '.join(tied_raw_types)} ({maximo_crudo} c/u). "
                f"Desempatado por z-score: {cadena_z}. Prima {ganador}."
            )

        z_ganador = z_scores[ganador]
        z_resto = max(z_scores[t] for t in types if t != ganador)
        diferencia = z_ganador - z_resto

        if diferencia >= UMBRAL_DOMINANCIA:
            classification = ganador
            is_integrador = False
            primary_types = [ganador]
        else:
            classification = "I"
            is_integrador = True
            primary_types = []
            decision_method += (
                f" Ganador preliminar {ganador} (z={z_ganador:.2f}) no se despega lo "
                f"suficiente del resto (siguiente z={z_resto:.2f}, diferencia<{UMBRAL_DOMINANCIA}) "
                f"-> Integrador."
            )

        results.append(
            {
                "row_index": row["row_index"],
                "nombre": row["nombre"],
                "correo": row["correo"],
                "scores": scores,
                "max_per_type": max_per_type,
                "percentages": percentages,
                "is_integrador": is_integrador,
                "primary_types": primary_types,
                "classification": classification,
                "classification_label": TYPE_NAMES[classification],
                "z_scores": z_scores,
                "tied_raw_types": tied_raw_types,
                "decision_method": decision_method,
            }
        )

    return results
