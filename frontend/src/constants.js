// Type metadata sourced from the FourSight capstone reference deck.
export const TYPE_ORDER = ["A", "B", "C", "D"];

export const TYPE_META = {
  A: {
    label: "Clarificador",
    short: "A",
    color: "var(--a)",
    soft: "var(--a-soft)",
    tagline: "Precisa el problema antes de avanzar",
    son: "Enfocados, metódicos, ordenados, deliberados, serios, organizados.",
    necesitan: "Orden, hechos, entendimiento de la historia, acceso a información, permiso para preguntar.",
    frustran: "Preguntan demasiado, llenan a la gente de datos, identifican obstáculos y áreas mal pensadas.",
    riesgo: "Puede pasar demasiado tiempo analizando el problema sin proceder.",
  },
  B: {
    label: "Ideador",
    short: "B",
    color: "var(--b)",
    soft: "var(--b-soft)",
    tagline: "Expande posibilidades e imaginación",
    son: "Juguetones, imaginativos, sociales, adaptables, flexibles, aventureros, independientes.",
    necesitan: "Espacio para jugar, estimulación constante, variedad y cambio.",
    frustran: "Llaman la atención, se impacientan si no entienden sus ideas, ofrecen ideas muy “alocadas”.",
    riesgo: "Puede pasar por alto los detalles.",
  },
  C: {
    label: "Desarrollador",
    short: "C",
    color: "var(--c)",
    soft: "var(--c-soft)",
    tagline: "Convierte conceptos en soluciones factibles",
    son: "Reflexivos, cuidadosos, pragmáticos, planeadores, pacientes, dedicados.",
    necesitan: "Oportunidad de considerar y evaluar opciones, tiempo para desarrollar ideas en soluciones útiles.",
    frustran: "Son muy particulares con los detalles, encuentran errores en ideas ajenas, se cierran a una sola forma de hacer las cosas.",
    riesgo: "Se puede atorar buscando “la solución perfecta”.",
  },
  D: {
    label: "Implementador",
    short: "D",
    color: "var(--d)",
    soft: "var(--d-soft)",
    tagline: "Ejecuta y concreta las ideas",
    son: "Persistentes, decisivos, determinados, asertivos, orientados a la acción.",
    necesitan: "Sentir que los demás se mueven a su ritmo, respuesta en tiempo a sus ideas, control.",
    frustran: "Presionan demasiado, expresan frustración si otros no van a su ritmo, sobrevenden ideas.",
    riesgo: "Puede lanzarse a la acción demasiado rápido.",
  },
  I: {
    label: "Integrador",
    short: "I",
    color: "var(--i)",
    soft: "var(--i-soft)",
    tagline: "Puntajes altos en las cuatro preferencias",
    son: "Tranquilos, flexibles, inclusivos, estabilizan influencias.",
    necesitan: "Cooperación, colaboración, energía de los demás, sentir que el equipo está comprometido con el reto.",
    frustran: "Indican lo que falta por hacer, son demasiado flexibles, se convierten en mediadores de paz.",
    riesgo: "Puede perder su propia voz tratando de complacer a todo el equipo.",
  },
};

export function classificationTypes(classification) {
  if (classification === "I") return ["I"];
  return classification.split("");
}
