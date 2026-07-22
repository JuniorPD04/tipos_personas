# -*- coding: utf-8 -*-
"""
Front Streamlit del formador de equipos FourSight.

Uso:
    streamlit run app.py
"""

import io
from pathlib import Path

import pandas as pd
import streamlit as st
from openpyxl import Workbook

import formador_equipos as fe


st.set_page_config(page_title="Formador de equipos FourSight", layout="wide")

st.title("Formador de equipos FourSight")
st.caption(
    "Sube la encuesta, ajusta el umbral de cobertura y el tamaño de los "
    "equipos. Cada equipo intentará cubrir los 4 roles: Clarificador, "
    "Ideador, Desarrollador e Implementador."
)


# ---------------------------------------------------------------------------
# SIDEBAR — parámetros
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Parámetros")

    umbral = st.slider(
        "Umbral de cobertura",
        min_value=3, max_value=8, value=fe.UMBRAL_COBERTURA,
        help=(
            "Una persona cubre un rol si su puntaje en ese rol es "
            "mayor o igual al umbral."
        ),
    )

    tamanos_txt = st.text_input(
        "Tamaños de equipos (separados por coma)",
        value=",".join(str(t) for t in fe.TAMANOS_EQUIPOS),
        help="La suma debe coincidir con el número de estudiantes.",
    )
    try:
        tamanos = [int(x.strip()) for x in tamanos_txt.split(",") if x.strip()]
    except ValueError:
        st.error("Los tamaños deben ser enteros separados por coma.")
        st.stop()

    st.divider()
    archivo = st.file_uploader(
        "Excel de encuesta (.xlsx)",
        type=["xlsx"],
        help=f"Si no subes nada, se usa {fe.RUTA_EXCEL_ENTRADA}.",
    )
    hoja = st.text_input("Hoja a leer", value=fe.HOJA_ENTRADA)


# ---------------------------------------------------------------------------
# CARGA
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _leer_excel(fuente, hoja: str) -> pd.DataFrame:
    return pd.read_excel(fuente, sheet_name=hoja, header=0)


if archivo is not None:
    fuente = archivo
    nombre_fuente = archivo.name
else:
    ruta = Path(fe.RUTA_EXCEL_ENTRADA)
    if not ruta.exists():
        st.warning(
            f"No se encontró {ruta.resolve()}. Sube un archivo desde la "
            "barra lateral."
        )
        st.stop()
    fuente = ruta
    nombre_fuente = str(ruta)

try:
    df = _leer_excel(fuente, hoja)
except Exception as e:
    st.error(f"No se pudo leer el Excel: {e}")
    st.stop()

st.caption(f"Fuente: `{nombre_fuente}` — hoja `{hoja}`")


# ---------------------------------------------------------------------------
# VALIDACIÓN DEL MAPEO
# ---------------------------------------------------------------------------

def _validar_mapeo(df: pd.DataFrame) -> list:
    problemas = []
    encabezados = list(df.columns)
    for perfil, (frag, idx) in fe.VALIDACION_ENCABEZADOS.items():
        if idx >= len(encabezados):
            problemas.append(f"{perfil}: falta la columna {idx}.")
            continue
        real = fe._normalizar_texto(encabezados[idx])
        if fe._normalizar_texto(frag) not in real:
            problemas.append(
                f"{perfil}: columna {idx} tiene '{encabezados[idx]}' y no "
                f"contiene '{frag}'."
            )
    return problemas


problemas = _validar_mapeo(df)
if problemas:
    st.error("Problemas en el mapeo de columnas:")
    for p in problemas:
        st.write(f"- {p}")
    st.stop()


# ---------------------------------------------------------------------------
# PROCESAMIENTO
# ---------------------------------------------------------------------------

estudiantes = fe.procesar_estudiantes(df)
if not estudiantes:
    st.error("No hay estudiantes con nombre válido en el Excel.")
    st.stop()

col_a, col_b, col_c = st.columns(3)
col_a.metric("Estudiantes", len(estudiantes))
col_b.metric("Equipos", len(tamanos))
col_c.metric("Suma tamaños", sum(tamanos))

if sum(tamanos) != len(estudiantes):
    st.error(
        f"La suma de tamaños ({sum(tamanos)}) no coincide con el número de "
        f"estudiantes ({len(estudiantes)}). Ajusta los tamaños."
    )
    st.stop()

equipos = fe.formar_equipos(estudiantes, tamanos, umbral)


# ---------------------------------------------------------------------------
# OUTPUT 1 — EQUIPOS
# ---------------------------------------------------------------------------

st.subheader("Equipos")

for i, equipo in enumerate(equipos, start=1):
    res = fe.resumen_cobertura(equipo, umbral)
    n_cubiertos = len(res["cubiertos"])
    faltantes = res["faltantes"]

    if not faltantes:
        titulo = f"Equipo {i} — {len(equipo)} personas — cobertura {n_cubiertos}/4 ✓"
    else:
        detalles = []
        for rol in faltantes:
            if rol in res["parciales"]:
                detalles.append(f"{rol} parcial (máx {res['parciales'][rol]})")
            else:
                detalles.append(f"{rol} sin nadie")
        titulo = (
            f"Equipo {i} — {len(equipo)} personas — cobertura "
            f"{n_cubiertos}/4 — falta: {', '.join(detalles)}"
        )

    with st.expander(titulo, expanded=True):
        filas = []
        for est in equipo:
            p = est["puntajes"]
            filas.append({
                "Nombre": est["nombre"],
                "Perfil": est["perfil"],
                "Clarificador": p["Clarificador"],
                "Ideador": p["Ideador"],
                "Desarrollador": p["Desarrollador"],
                "Implementador": p["Implementador"],
            })
        tabla = pd.DataFrame(filas)

        def _resaltar(col):
            rol = col.name
            if rol not in fe.ORDEN_PERFILES:
                return ["" for _ in col]
            return [
                "background-color: #d4edda" if v >= umbral else ""
                for v in col
            ]

        st.dataframe(
            tabla.style.apply(_resaltar, axis=0),
            hide_index=True,
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# OUTPUT 2 — PERFIL POR PERSONA
# ---------------------------------------------------------------------------

st.subheader("Perfil por persona")

filas_pf = []
for e in sorted(estudiantes, key=lambda x: x["nombre"]):
    p = e["puntajes"]
    filas_pf.append({
        "Nombre": e["nombre"],
        "Perfil": e["perfil"],
        "Clarificador": p["Clarificador"],
        "Ideador": p["Ideador"],
        "Desarrollador": p["Desarrollador"],
        "Implementador": p["Implementador"],
    })
st.dataframe(pd.DataFrame(filas_pf), hide_index=True, use_container_width=True)


# ---------------------------------------------------------------------------
# DESCARGA DEL EXCEL
# ---------------------------------------------------------------------------

def _excel_bytes(equipos, estudiantes, umbral) -> bytes:
    wb = Workbook()
    hoja_eq = wb.active
    hoja_eq.title = "Equipos"
    hoja_eq.append([
        "Equipo", "Tamaño", "Cobertura", "Roles cubiertos", "Roles faltantes",
        "Nombre", "Perfil",
        "Clarificador", "Ideador", "Desarrollador", "Implementador",
    ])
    for i, equipo in enumerate(equipos, start=1):
        res = fe.resumen_cobertura(equipo, umbral)
        cubiertos = [r for r in fe.ORDEN_PERFILES if r in res["cubiertos"]]
        faltantes_txt = []
        for rol in res["faltantes"]:
            if rol in res["parciales"]:
                faltantes_txt.append(
                    f"{rol} (parcial, máx {res['parciales'][rol]})"
                )
            else:
                faltantes_txt.append(f"{rol} (sin nadie)")
        for est in equipo:
            p = est["puntajes"]
            hoja_eq.append([
                f"Equipo {i}", len(equipo), f"{len(cubiertos)}/4",
                ", ".join(cubiertos), ", ".join(faltantes_txt),
                est["nombre"], est["perfil"],
                p["Clarificador"], p["Ideador"],
                p["Desarrollador"], p["Implementador"],
            ])

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

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


st.download_button(
    "Descargar resultado (Excel)",
    data=_excel_bytes(equipos, estudiantes, umbral),
    file_name="resultado_equipos.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
