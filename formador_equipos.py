# -*- coding: utf-8 -*-
"""
Formador de equipos FourSight.

Lee una encuesta de 32 preguntas (Si/No) desde un Excel, calcula el perfil
creativo dominante de cada estudiante (Clarificador, Ideador, Desarrollador,
Implementador o Integrador) y luego forma equipos balanceados que mezclen
perfiles distintos para cubrir todo el proceso creativo.

Genera dos outputs (consola + Excel):
  1) Composición de equipos con la diversidad de perfiles.
  2) Perfil por persona con los 4 puntajes.
"""

import random
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from openpyxl import Workbook


# ---------------------------------------------------------------------------
# CONFIGURACIÓN (ajustable arriba, sin tocar la lógica)
# ---------------------------------------------------------------------------

# Ruta del Excel de entrada y hoja a leer
RUTA_EXCEL_ENTRADA = Path("archivo.xlsx")
HOJA_ENTRADA = "Sheet1"

# Excel de salida
RUTA_EXCEL_SALIDA = Path("resultado_equipos.xlsx")

# Umbral para clasificar como Integrador: si (max - min) de los 4 puntajes
# es menor o igual a este valor, el perfil queda como Integrador.
UMBRAL_INTEGRADOR = 1

# Tamaños de equipos deseados. La suma debe coincidir con el número de
# estudiantes. Cambiar libremente al agregar/quitar personas.
# Actualmente: 2 equipos de 4 y 4 equipos de 3 → 20 estudiantes.
TAMANOS_EQUIPOS = [4, 4, 3, 3, 3, 3]

# Umbral mínimo de puntaje para considerar que una persona "cubre" un rol
# FourSight en su equipo. Ajustable (3..8). Con 5 se acepta a personas cuyo
# rol es su preferencia secundaria fuerte, no solo la dominante.
UMBRAL_COBERTURA = 5

# Semilla para hacer determinista cualquier decisión aleatoria.
SEMILLA = 42

# Mapeo columna (base 0) → perfil. Coincide con la estructura del Excel.
COLUMNAS_POR_PERFIL = {
    "Desarrollador": list(range(5, 13)),   # cols 5..12
    "Implementador": list(range(13, 21)),  # cols 13..20
    "Clarificador": list(range(21, 29)),   # cols 21..28
    "Ideador":      list(range(29, 37)),   # cols 29..36
}

# Fragmentos de texto que deben aparecer en el encabezado de la primera
# pregunta de cada bloque. Sirven para validar el mapeo contra el Excel real.
VALIDACION_ENCABEZADOS = {
    "Desarrollador": ("probar y revisar mis ideas antes de generar la solución final", 5),
    "Implementador": ("tomar los pasos necesarios para accionar una idea",             13),
    "Clarificador":  ("clarificar la naturaleza exacta del problema",                  21),
    "Ideador":       ("abordo los problemas de manera creativa",                       29),
}

# Orden canónico para mostrar puntajes.
ORDEN_PERFILES = ["Clarificador", "Ideador", "Desarrollador", "Implementador"]

# Columna con el nombre del estudiante.
COL_NOMBRE = 4


# ---------------------------------------------------------------------------
# UTILIDADES
# ---------------------------------------------------------------------------

def _normalizar_texto(texto: str) -> str:
    """Baja a minúsculas, quita tildes y espacios extras para comparar textos."""
    if texto is None:
        return ""
    t = str(texto).strip().lower()
    # Quitar acentos: "sí" → "si", "análisis" → "analisis"
    t = "".join(
        c for c in unicodedata.normalize("NFD", t)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(t.split())


def normalizar_si(valor) -> int:
    """
    Convierte una respuesta de la encuesta a 1 (afirmativa) o 0 (negativa).
    Acepta variantes como 'Si', 'Sí', 'SI', ' si ', 'sí ', etc.
    Valores vacíos o no reconocidos se tratan como 0.
    """
    t = _normalizar_texto(valor)
    if t in {"si", "s", "yes", "y", "1", "true", "verdadero"}:
        return 1
    return 0


# ---------------------------------------------------------------------------
# CARGA Y VALIDACIÓN
# ---------------------------------------------------------------------------

def cargar_datos(ruta: Path, hoja: str) -> pd.DataFrame:
    """Carga el Excel y valida que el archivo exista."""
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de entrada: {ruta.resolve()}"
        )
    try:
        df = pd.read_excel(ruta, sheet_name=hoja, header=0)
    except ValueError as e:
        raise ValueError(
            f"No se pudo leer la hoja '{hoja}' del Excel: {e}"
        )
    if df.empty:
        raise ValueError("El Excel no contiene filas de datos.")
    return df


def validar_mapeo_columnas(df: pd.DataFrame) -> None:
    """
    Compara los encabezados reales con las preguntas de referencia.
    Si algún encabezado no casa con el índice esperado, avisa por consola
    en lugar de asumir el mapeo.
    """
    encabezados = list(df.columns)
    hay_error = False

    print("Validando mapeo de columnas contra encabezados del Excel...")
    for perfil, (fragmento, idx_esperado) in VALIDACION_ENCABEZADOS.items():
        if idx_esperado >= len(encabezados):
            print(f"  [ERROR] {perfil}: no existe la columna {idx_esperado} en el Excel.")
            hay_error = True
            continue
        real = _normalizar_texto(encabezados[idx_esperado])
        esperado = _normalizar_texto(fragmento)
        if esperado in real:
            print(f"  [OK] {perfil}: col {idx_esperado} casa con '{fragmento}'.")
        else:
            print(
                f"  [ADVERTENCIA] {perfil}: la columna {idx_esperado} tiene el "
                f"encabezado '{encabezados[idx_esperado]}' y NO contiene "
                f"'{fragmento}'."
            )
            hay_error = True

    if hay_error:
        print(
            "\nEl mapeo de columnas no coincide con lo esperado. "
            "Revisa el Excel antes de continuar.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("Mapeo validado correctamente.\n")


# ---------------------------------------------------------------------------
# CÁLCULO DE PERFILES
# ---------------------------------------------------------------------------

def calcular_puntajes(fila) -> dict:
    """
    Cuenta los 'Si' de cada bloque de 8 preguntas y devuelve un dict
    {perfil: puntaje 0..8}.
    """
    puntajes = {}
    for perfil, columnas in COLUMNAS_POR_PERFIL.items():
        puntaje = sum(normalizar_si(fila.iloc[c]) for c in columnas)
        puntajes[perfil] = puntaje
    return puntajes


def determinar_perfil(puntajes: dict) -> str:
    """
    Determina el perfil dominante del estudiante:
      - Si (max - min) <= UMBRAL_INTEGRADOR → 'Integrador'.
      - Si un solo perfil tiene el puntaje máximo → ese perfil.
      - Si hay empate en el máximo → 'PerfilA/PerfilB' (unidos por /),
        en el orden canónico de ORDEN_PERFILES.
    """
    max_p = max(puntajes.values())
    min_p = min(puntajes.values())

    if (max_p - min_p) <= UMBRAL_INTEGRADOR:
        return "Integrador"

    empatados = [p for p in ORDEN_PERFILES if puntajes[p] == max_p]
    if len(empatados) == 1:
        return empatados[0]
    # Empate: se conservan los dos nombres unidos (sin romper el empate).
    return "/".join(empatados)


def procesar_estudiantes(df: pd.DataFrame) -> list:
    """
    Recorre cada fila del DataFrame y arma una lista de diccionarios
    con los datos necesarios para el resto del programa.
    """
    estudiantes = []
    for _, fila in df.iterrows():
        nombre = fila.iloc[COL_NOMBRE]
        if pd.isna(nombre) or str(nombre).strip() == "":
            # Ignoramos filas sin nombre (respuestas vacías).
            continue
        puntajes = calcular_puntajes(fila)
        perfil = determinar_perfil(puntajes)
        estudiantes.append({
            "nombre": str(nombre).strip(),
            "puntajes": puntajes,
            "perfil": perfil,
        })
    return estudiantes


# ---------------------------------------------------------------------------
# FORMACIÓN DE EQUIPOS
# ---------------------------------------------------------------------------

def _roles_cubiertos(equipo: list, umbral: int) -> set:
    """Roles FourSight cubiertos por el equipo al umbral dado."""
    cubiertos = set()
    for est in equipo:
        for rol in ORDEN_PERFILES:
            if est["puntajes"][rol] >= umbral:
                cubiertos.add(rol)
    return cubiertos


def formar_equipos(estudiantes: list, tamanos: list,
                   umbral: int = UMBRAL_COBERTURA) -> list:
    """
    Reparte a los estudiantes en equipos usando un draft greedy orientado a
    COBERTURA de los 4 roles FourSight (Clarificador, Ideador, Desarrollador,
    Implementador).

    Un rol se considera "cubierto" en un equipo si al menos un miembro tiene
    puntaje >= `umbral` en ese rol (usando el vector completo, no solo el
    perfil dominante).

    Algoritmo:
      - Equipos vacíos, con espacio según `tamanos`.
      - Mientras queden personas libres y equipos con espacio, se evalúa cada
        par (persona libre, equipo con espacio) y se elige el mejor por la
        clave (en orden):
          1) mayor `nuevos` = roles aún no cubiertos por el equipo que la
             persona pasaría a cubrir (score >= umbral).
          2) mayor suma de puntajes de la persona en los roles todavía NO
             cubiertos por el equipo.
          3) mayor puntaje total de la persona.
          4) menor índice de equipo, menor índice de persona (determinismo).
      - Solo se consideran equipos con espacio > 0.
    """
    if sum(tamanos) != len(estudiantes):
        raise ValueError(
            f"La suma de TAMANOS_EQUIPOS ({sum(tamanos)}) no coincide con "
            f"el número de estudiantes ({len(estudiantes)}). "
            f"Ajusta TAMANOS_EQUIPOS."
        )

    random.seed(SEMILLA)
    n_equipos = len(tamanos)
    equipos = [[] for _ in range(n_equipos)]
    espacio = list(tamanos)

    # Orden fijo de las personas libres (por nombre) para determinismo.
    libres = sorted(range(len(estudiantes)),
                    key=lambda i: estudiantes[i]["nombre"])
    libres = list(libres)

    # Cache de roles cubiertos por equipo (se recalcula al asignar).
    cubiertos_por_eq = [set() for _ in range(n_equipos)]

    while libres:
        equipos_con_espacio = [i for i in range(n_equipos) if espacio[i] > 0]
        if not equipos_con_espacio:
            break

        mejor_clave = None
        mejor_par = None  # (idx_equipo, idx_persona_en_libres)

        for eq_i in equipos_con_espacio:
            cubiertos = cubiertos_por_eq[eq_i]
            faltantes = [r for r in ORDEN_PERFILES if r not in cubiertos]
            for pos, est_i in enumerate(libres):
                p = estudiantes[est_i]["puntajes"]
                nuevos = sum(1 for r in faltantes if p[r] >= umbral)
                suma_faltantes = sum(p[r] for r in faltantes)
                total = sum(p.values())
                # Mayor mejor en las 3 primeras; luego menor índice de equipo
                # y menor índice de persona en `libres`.
                clave = (nuevos, suma_faltantes, total, -eq_i, -pos)
                if mejor_clave is None or clave > mejor_clave:
                    mejor_clave = clave
                    mejor_par = (eq_i, pos)

        eq_i, pos = mejor_par
        est = estudiantes[libres.pop(pos)]
        equipos[eq_i].append(est)
        espacio[eq_i] -= 1
        # Actualizar cache de cubiertos con los aportes de la nueva persona.
        for rol in ORDEN_PERFILES:
            if est["puntajes"][rol] >= umbral:
                cubiertos_por_eq[eq_i].add(rol)

    return equipos


def resumen_cobertura(equipo: list, umbral: int = UMBRAL_COBERTURA) -> dict:
    """
    Devuelve un dict con la cobertura de un equipo:
      {
        "umbral": umbral usado,
        "cubiertos": set de roles cubiertos al umbral,
        "faltantes": lista de roles no cubiertos al umbral,
        "parciales": {rol: umbral_efectivo} para roles no cubiertos al umbral
                     pero sí a un umbral menor (mejor esfuerzo del equipo).
      }
    """
    cubiertos = _roles_cubiertos(equipo, umbral)
    faltantes = [r for r in ORDEN_PERFILES if r not in cubiertos]
    parciales = {}
    for rol in faltantes:
        # Máximo puntaje del equipo en ese rol → sirve como umbral efectivo.
        mejor = max((e["puntajes"][rol] for e in equipo), default=0)
        if mejor > 0:
            parciales[rol] = mejor
    return {
        "umbral": umbral,
        "cubiertos": cubiertos,
        "faltantes": faltantes,
        "parciales": parciales,
    }


# ---------------------------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------------------------

def imprimir_equipos(equipos: list, umbral: int = UMBRAL_COBERTURA) -> None:
    """Output 1: composición de equipos con indicador de cobertura."""
    print("=" * 78)
    print(f"OUTPUT 1 — COMPOSICIÓN DE EQUIPOS  (umbral de cobertura = {umbral})")
    print("=" * 78)
    ancho = max(
        (len(e["nombre"]) for eq in equipos for e in eq),
        default=20,
    )
    for i, equipo in enumerate(equipos, start=1):
        res = resumen_cobertura(equipo, umbral)
        cubiertos = res["cubiertos"]
        faltantes = res["faltantes"]
        parciales = res["parciales"]

        estado = f"cobertura: {len(cubiertos)}/4"
        if faltantes:
            trozos = []
            for rol in faltantes:
                if rol in parciales:
                    trozos.append(f"{rol} (parcial, máx {parciales[rol]})")
                else:
                    trozos.append(f"{rol} (sin nadie)")
            estado += "  — falta: " + ", ".join(trozos)
        else:
            estado += "  ✓ los 4 roles cubiertos"

        print(f"\nEquipo {i} ({len(equipo)} personas) — {estado}")
        # Encabezado de puntajes para leer quién cubre cada rol.
        print(
            f"  {'':<{ancho}}    {'Clar':>4} {'Idea':>4} "
            f"{'Desa':>4} {'Impl':>4}   Perfil"
        )
        for est in equipo:
            p = est["puntajes"]
            print(
                f"  - {est['nombre']:<{ancho}}  "
                f"{p['Clarificador']:>4} {p['Ideador']:>4} "
                f"{p['Desarrollador']:>4} {p['Implementador']:>4}   "
                f"{est['perfil']}"
            )
    print()


def imprimir_perfiles(estudiantes: list) -> None:
    """Output 2: perfil y puntajes por persona (ordenado por nombre)."""
    print("=" * 70)
    print("OUTPUT 2 — PERFIL POR PERSONA")
    print("=" * 70)
    ordenados = sorted(estudiantes, key=lambda x: x["nombre"])
    ancho_n = max(len(e["nombre"]) for e in ordenados)
    ancho_p = max(len(e["perfil"]) for e in ordenados)
    encabezado = (
        f"{'Nombre':<{ancho_n}}  {'Perfil':<{ancho_p}}  "
        f"{'Clar':>4} {'Idea':>4} {'Desa':>4} {'Impl':>4}"
    )
    print(encabezado)
    print("-" * len(encabezado))
    for e in ordenados:
        p = e["puntajes"]
        print(
            f"{e['nombre']:<{ancho_n}}  {e['perfil']:<{ancho_p}}  "
            f"{p['Clarificador']:>4} {p['Ideador']:>4} "
            f"{p['Desarrollador']:>4} {p['Implementador']:>4}"
        )
    print()


def exportar_excel(equipos: list, estudiantes: list, ruta: Path,
                   umbral: int = UMBRAL_COBERTURA) -> None:
    """Exporta ambos outputs a un Excel con hojas 'Equipos' y 'Perfiles'."""
    wb = Workbook()

    # Hoja Equipos ---------------------------------------------------------
    hoja_eq = wb.active
    hoja_eq.title = "Equipos"
    hoja_eq.append([
        "Equipo", "Tamaño", "Cobertura", "Roles cubiertos", "Roles faltantes",
        "Nombre", "Perfil",
        "Clarificador", "Ideador", "Desarrollador", "Implementador",
    ])
    for i, equipo in enumerate(equipos, start=1):
        res = resumen_cobertura(equipo, umbral)
        cubiertos = [r for r in ORDEN_PERFILES if r in res["cubiertos"]]
        faltantes_txt = []
        for rol in res["faltantes"]:
            if rol in res["parciales"]:
                faltantes_txt.append(f"{rol} (parcial, máx {res['parciales'][rol]})")
            else:
                faltantes_txt.append(f"{rol} (sin nadie)")
        for est in equipo:
            p = est["puntajes"]
            hoja_eq.append([
                f"Equipo {i}",
                len(equipo),
                f"{len(cubiertos)}/4",
                ", ".join(cubiertos),
                ", ".join(faltantes_txt),
                est["nombre"],
                est["perfil"],
                p["Clarificador"], p["Ideador"],
                p["Desarrollador"], p["Implementador"],
            ])

    # Hoja Perfiles --------------------------------------------------------
    hoja_pf = wb.create_sheet("Perfiles")
    hoja_pf.append([
        "Nombre", "Perfil dominante",
        "Clarificador", "Ideador", "Desarrollador", "Implementador",
    ])
    for e in sorted(estudiantes, key=lambda x: x["nombre"]):
        p = e["puntajes"]
        hoja_pf.append([
            e["nombre"], e["perfil"],
            p["Clarificador"], p["Ideador"],
            p["Desarrollador"], p["Implementador"],
        ])

    wb.save(ruta)
    print(f"Resultados exportados a: {ruta.resolve()}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        df = cargar_datos(RUTA_EXCEL_ENTRADA, HOJA_ENTRADA)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    validar_mapeo_columnas(df)

    estudiantes = procesar_estudiantes(df)
    if not estudiantes:
        print("[ERROR] No hay estudiantes con nombre válido en el Excel.",
              file=sys.stderr)
        sys.exit(1)

    print(f"Estudiantes procesados: {len(estudiantes)}\n")

    try:
        equipos = formar_equipos(estudiantes, TAMANOS_EQUIPOS, UMBRAL_COBERTURA)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    imprimir_equipos(equipos, UMBRAL_COBERTURA)
    imprimir_perfiles(estudiantes)
    exportar_excel(equipos, estudiantes, RUTA_EXCEL_SALIDA, UMBRAL_COBERTURA)


if __name__ == "__main__":
    main()
