"""Shared metadata for the FourSight engine: type labels and header
normalization used to locate the Id/Correo/Nombre columns in the uploaded
Excel (the 32 question columns are located by position, see scoring.py).
"""
import unicodedata

TYPE_NAMES = {
    "A": "Clarificador",
    "B": "Ideador",
    "C": "Desarrollador",
    "D": "Implementador",
    "I": "Integrador",
}

# raw header text (normalized) -> canonical metadata key
METADATA_COLUMNS = {
    "id": "id",
    "hora de inicio": "hora_inicio",
    "hora de finalizacion": "hora_fin",
    "correo electronico": "correo",
    "nombre": "nombre",
}


def normalize(text: str) -> str:
    """lowercase, strip accents/whitespace/trailing punctuation for robust matching"""
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    text = text.rstrip(".")
    return text
