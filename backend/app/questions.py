"""Mapping between the 32 FourSight survey questions and the four thinking
preferences (A = Clarificador, B = Ideador, C = Desarrollador, D = Implementador).

Matching is done on normalized question text rather than column position, so the
engine keeps working even if the exported Excel reorders or slightly re-wraps
the question columns.
"""
import unicodedata

TYPE_NAMES = {
    "A": "Clarificador",
    "B": "Ideador",
    "C": "Desarrollador",
    "D": "Implementador",
    "I": "Integrador",
}

# raw question text -> preference letter
_RAW_QUESTIONS = {
    "A": [
        "Me gusta tomarme el tiempo para clarificar la naturaleza exacta del problema",
        "Me gusta analizar un problema desde diferentes ángulos",
        "Me gusta identificar los hechos más relevantes de un problema",
        "Disfruto identificar formas únicas de entender un problema",
        "Me gusta enfocarme en formular un enunciado que precise el problema",
        "Me gusta enfocarme en la información clave alrededor de la situación de reto",
        "Antes de avanzar me gusta tener un entendimiento clave del problema",
        "Disfruto reunir información para identificar las causas clave de un problema",
    ],
    "B": [
        "Generalmente abordo los problemas de manera creativa",
        "Se me facilita generar ideas inusuales para resolver problemas",
        "Me gusta generar muchas ideas",
        "Disfruto esforzar mi imaginación para producir muchas ideas",
        "Se me hace difícil ejecutar mis ideas",
        "Me gusta trabajar con ideas únicas",
        "Mi tendencia natural es generar muchísimas ideas para resolver problemas",
        "Disfruto usar metáforas y analogías para generar nuevas ideas para solucionar problemas",
    ],
    "C": [
        "Me gusta probar y revisar mis ideas antes de generar la solución final",
        "Me gusta analizar todo lo positivo y lo negativo de una solución potencial",
        "Antes de implementar una solución, me gusta desarrollar los pasos",
        "Me gusta generar criterios que se puedan utilizar para identificar la mejor opción",
        "Me gusta tomarme el tiempo para perfeccionar una idea",
        "Me gusta pensar en todas las cosas que necesito para implementar una idea",
        "Me gusta explorar las fortalezas y debilidades de una solución potencial",
        "Disfruto el análisis y esfuerzo que toma transformar un concepto en una idea accionable.",
    ],
    "D": [
        "Me gusta tomar los pasos necesarios para accionar una idea",
        "Normalmente no dedico mucho tiempo en definir el problema a solucionar",
        "Disfruto ver que las cosas sucedan",
        "Realmente disfruto implementar una idea",
        "Disfruto poner mis ideas en acción",
        "Tengo poca paciencia para refinar o pulir una idea",
        "Tiendo a buscar una solución rápida y ejecutarla",
        "Me desespera ver que las cosas no se están ejecutando",
    ],
}

# columns that are metadata, not survey questions (normalized text -> canonical key)
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


QUESTION_MAP = {}
for _type, _questions in _RAW_QUESTIONS.items():
    for _q in _questions:
        QUESTION_MAP[normalize(_q)] = _type

TOTAL_QUESTIONS_PER_TYPE = 8
