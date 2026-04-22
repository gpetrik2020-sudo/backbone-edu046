import os
import json
import markdown as md_lib
from flask import Flask, render_template, abort, request, jsonify, redirect
from openai import OpenAI

app = Flask(__name__)

MD_DIR = 'textos_md_edu046'

CURSO = {
    "titulo": "Investigación de Mercados",
    "subtitulo": "EDU046 — Fundamentos epistemológicos y operativos",
}

TEMAS = [
    {"semana": "s1", "num": "01.1", "titulo": "El mercado como construcción operativa",
     "filename": "01.1.1_—_El_mercado_como_construccion_operativa_EDU046.md"},
    {"semana": "s1", "num": "01.2", "titulo": "Incertidumbre y decisión como estructura operativa",
     "filename": "01.2.1_Incertidumbre_y_decision_como_estructura_operativa_del_sistema_de_investigacion_de_mercados_EDU046.md"},
    {"semana": "s1", "num": "01.3", "titulo": "La investigación como sistema",
     "filename": "01.3.1_La_investigacion_como_sistema_EDU046.md"},
    {"semana": "s2", "num": "02.1", "titulo": "Quién define el problema: arquitectura de investigación",
     "filename": "02.1.1_Quien_define_el_problema_arquitectura_de_investigacion_EDU046.md"},
    {"semana": "s2", "num": "02.2", "titulo": "La construcción del problema",
     "filename": "02.2.1_La_construccion_del_problema_EDU046.md"},
    {"semana": "s2", "num": "02.3", "titulo": "El sesgo desde el planteamiento",
     "filename": "02.3.1_El_sesgo_desde_el_planteamiento_EDU046.md"},
    {"semana": "s3", "num": "03.1", "titulo": "De la experiencia a la variable",
     "filename": "03.1.1_De_la_experiencia_a_la_variable_EDU046.md"},
    {"semana": "s3", "num": "03.2", "titulo": "Instrumentos como sistemas",
     "filename": "03.2.1_Instrumentos_como_sistemas_EDU046.md"},
    {"semana": "s3", "num": "03.3", "titulo": "El dato como artefacto",
     "filename": "03.3.1_El_dato_como_artefacto_EDU046.md"},
    {"semana": "s4", "num": "04.1", "titulo": "Lo cualitativo: interpretación",
     "filename": "04.1.1_Lo_cualitativo_interpretacion_EDU046.md"},
    {"semana": "s4", "num": "04.2", "titulo": "Lo cuantitativo: formalización",
     "filename": "04.2.1_Lo_cuantitativo_formalizacion_EDU046.md"},
    {"semana": "s4", "num": "04.3", "titulo": "Triangulación: convergencia",
     "filename": "04.3.1_Triangulacion__convergencia_EDU046.md"},
    {"semana": "s5", "num": "05.1", "titulo": "El dato no habla: demanda interpretación",
     "filename": "05.1.1_El_dato_no_habla_sino_demanda_interpretacion_EDU046.md"},
    {"semana": "s5", "num": "05.2", "titulo": "Modelos: simplificar para decidir",
     "filename": "05.2.1_Modelos_simplificar_EDU046.md"},
    {"semana": "s5", "num": "05.3", "titulo": "Segmentación",
     "filename": "05.3.1_Segmentacion_EDU046.md"},
    {"semana": "s6", "num": "06.1", "titulo": "Decidir sin certeza",
     "filename": "06.1.1_Decidir_sin_certeza_EDU046.md"},
    {"semana": "s6", "num": "06.2", "titulo": "La investigación como tecnología",
     "filename": "06.2.1_La_investigacion_como_tecnologia_EDU046.md"},
    {"semana": "s6", "num": "06.3", "titulo": "Ética en la intervención",
     "filename": "06.3.1_Etica_en_la_intervencion_EDU046.md"},
]

SEMANAS = {
    "s1": "El mercado como sistema",
    "s2": "El problema de investigación",
    "s3": "Variables, instrumentos y datos",
    "s4": "Métodos y triangulación",
    "s5": "Análisis e interpretación",
    "s6": "Decisión, tecnología y ética",
}

EVALUACIONES = {
    "s1": {
        "titulo": "Evaluación Semana 1 — El mercado, la incertidumbre y la investigación",
        "preguntas": [
            "¿Por qué el mercado es una construcción operativa y no una entidad empírica?",
            "Explica qué papel juega la incertidumbre como materia prima del sistema de investigación.",
            "¿Cómo distingues entre un mercado como fenómeno y un mercado como dispositivo?",
            "¿Qué significa que la investigación de mercados sea un 'sistema' en sentido estricto?",
            "Describe la relación entre decisión e incertidumbre en el contexto de la investigación.",
            "¿Qué implica operativamente construir un mercado? Da un ejemplo concreto.",
            "¿Cuál es la diferencia entre reducir incertidumbre y eliminarla en la práctica?",
            "Explica cómo los actores que participan en un mercado contribuyen a su construcción.",
            "¿Qué elementos hacen que la investigación funcione como sistema y no como proceso lineal?",
            "¿Por qué es problemático asumir que los mercados 'existen' antes de ser investigados?",
        ],
    },
    "s2": {
        "titulo": "Evaluación Semana 2 — El problema de investigación",
        "preguntas": [
            "¿Quién tiene autoridad para definir el problema de investigación y qué implica esa decisión?",
            "Explica cómo la arquitectura de investigación determina qué preguntas son posibles.",
            "¿Qué es el 'sesgo de planteamiento' y cómo puede introducirse desde el inicio de un estudio?",
            "Describe el proceso de construcción de un problema de investigación válido.",
            "¿Cómo se diferencia un problema bien formulado de uno mal planteado?",
            "¿Por qué el problema no es un simple punto de partida sino una decisión arquitectónica?",
            "Explica la relación entre quién financia la investigación y cómo se construye el problema.",
            "¿Qué sesgos estructurales pueden afectar el planteamiento en investigación de mercados?",
            "¿Cómo puede un investigador detectar y corregir el sesgo en la definición del problema?",
            "¿Qué diferencia existe entre un problema operativo y uno de investigación epistemológicamente?",
        ],
    },
    "s3": {
        "titulo": "Evaluación Semana 3 — Variables, instrumentos y datos",
        "preguntas": [
            "¿Cómo se transforma una experiencia observable en una variable medible?",
            "Explica por qué los instrumentos de investigación no son neutrales sino que producen realidad.",
            "¿Qué significa que el dato sea un 'artefacto' y no un reflejo de la realidad?",
            "Describe el proceso de operacionalización: de la experiencia a la variable.",
            "¿Qué criterios definen si un instrumento de medición es válido para una investigación?",
            "¿Cómo afecta el diseño del instrumento a la calidad de los datos obtenidos?",
            "Explica la diferencia entre un dato bruto y un dato procesado epistemológicamente.",
            "¿Por qué la elección de variables implica ya una posición teórica?",
            "¿Qué riesgos epistemológicos tiene tratar los datos como si fueran hechos objetivos?",
            "Describe cómo el instrumento y el dato están mutuamente constituidos en una investigación.",
        ],
    },
    "s4": {
        "titulo": "Evaluación Semana 4 — Métodos y triangulación",
        "preguntas": [
            "¿Qué tipo de conocimiento produce la investigación cualitativa que no produce la cuantitativa?",
            "¿Cómo funciona la formalización en la investigación cuantitativa y qué supuestos implica?",
            "¿Qué significa triangular métodos y cuándo es epistemológicamente válido hacerlo?",
            "Explica la diferencia entre complementariedad y equivalencia en el uso de métodos mixtos.",
            "¿Cuáles son los límites de la interpretación en la investigación cualitativa?",
            "¿Qué riesgos tiene convertir fenómenos cualitativos en variables cuantitativas?",
            "Describe una situación en la que la triangulación metodológica sea indispensable.",
            "¿Por qué no toda convergencia de métodos implica mayor validez?",
            "¿Cómo afecta la perspectiva del investigador la interpretación de datos cualitativos?",
            "Explica qué aporta cada tipo de investigación al problema de la representatividad.",
        ],
    },
    "s5": {
        "titulo": "Evaluación Semana 5 — Análisis e interpretación",
        "preguntas": [
            "¿Por qué se afirma que el dato 'no habla' y necesita ser interpretado?",
            "Explica qué función cumple un modelo en la simplificación de la realidad.",
            "¿Qué criterios permiten distinguir una buena segmentación de una arbitraria?",
            "¿Cuál es el riesgo de confundir el modelo con la realidad que modela?",
            "Describe el proceso de interpretación desde la lectura de datos hasta la conclusión.",
            "¿Cómo influye el marco teórico en la interpretación de los resultados?",
            "¿Qué hace válida a una segmentación en términos operativos y estratégicos?",
            "Explica la diferencia entre describir patrones y explicar causas en el análisis de datos.",
            "¿Qué significa que un modelo sea una simplificación útil y no una representación exacta?",
            "¿Cómo puede la segmentación distorsionar la comprensión del mercado si se aplica mal?",
        ],
    },
    "s6": {
        "titulo": "Evaluación Semana 6 — Decisión, tecnología y ética",
        "preguntas": [
            "¿Qué implica tomar decisiones 'sin certeza' y cómo la investigación gestiona ese riesgo?",
            "Explica cómo la investigación de mercados funciona como tecnología de reducción de incertidumbre.",
            "¿Cuáles son las implicaciones éticas de intervenir en un mercado a partir de investigación?",
            "¿Qué responsabilidades tiene el investigador cuando sus resultados afectan a comunidades?",
            "¿Cómo se relacionan las dimensiones técnica y ética en el diseño de una investigación?",
            "Explica qué significa que la investigación sea una forma de intervención y no solo de observación.",
            "¿Qué criterios éticos deben guiar el uso de datos en investigación de mercados?",
            "¿Cómo puede la tecnología amplificar tanto las capacidades como los riesgos éticos?",
            "Describe una situación en la que una decisión basada en datos sea técnicamente correcta pero éticamente problemática.",
            "¿Por qué la ética en la investigación de mercados no es opcional sino estructural al proceso?",
        ],
    },
}

RAG = {
    "s1": {
        "1.1": "El mercado es una construcción operativa emergente de dispositivos, actores y transacciones, no una entidad empírica pre-existente.",
        "1.2": "La incertidumbre es la materia prima del sistema de investigación: no se elimina, se redistribuye.",
        "1.3": "La investigación de mercados es un sistema: sus componentes se retroalimentan y la salida depende de la arquitectura completa.",
    },
    "s2": {
        "2.1": "Definir el problema es una decisión arquitectónica que estructura todo lo que sigue — quién lo define determina qué puede encontrarse.",
        "2.2": "El problema se construye, no se descubre: implica seleccionar, enmarcar y reducir la complejidad desde una posición.",
        "2.3": "El sesgo puede introducirse desde el planteamiento: en la elección del problema, la perspectiva del cliente y los supuestos implícitos.",
    },
    "s3": {
        "3.1": "Operacionalizar es traducir experiencias en variables: ese proceso implica pérdidas y decisiones teóricas.",
        "3.2": "Los instrumentos producen el dato que miden: son dispositivos ontológicos, no espejos.",
        "3.3": "El dato es un artefacto construido, no un hecho bruto: lleva inscrita la teoría y el método que lo produjeron.",
    },
    "s4": {
        "4.1": "Lo cualitativo produce interpretación densa: significado, contexto, proceso.",
        "4.2": "Lo cuantitativo formaliza: convierte fenómenos en variables medibles con supuestos sobre su estructura.",
        "4.3": "Triangular no garantiza mayor verdad: la convergencia de métodos distintos puede confirmar un mismo sesgo.",
    },
    "s5": {
        "5.1": "El dato no habla: demanda un lector con un marco. La interpretación no es opcional, es constitutiva.",
        "5.2": "Un modelo es una simplificación útil. Su valor no está en representar la realidad sino en facilitar decisiones.",
        "5.3": "Segmentar es imponer distinciones al continuo del mercado. La segmentación válida es la que opera.",
    },
    "s6": {
        "6.1": "Decidir sin certeza es la condición normal. La investigación gestiona esa incertidumbre, no la resuelve.",
        "6.2": "La investigación como tecnología: transforma incertidumbre en información procesable para decisiones.",
        "6.3": "La ética no es un anexo: es constitutiva del proceso de investigación. Investigar es intervenir.",
    },
}


def get_semanas():
    grupos = {}
    for t in TEMAS:
        sid = t['semana']
        grupos.setdefault(sid, {'id': sid, 'titulo': SEMANAS.get(sid, sid), 'temas': []})
        grupos[sid]['temas'].append(t)
    return list(grupos.values())


def load_md(filename):
    path = os.path.join(MD_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) >= 3:
            raw = parts[2].lstrip('\n')
    return md_lib.markdown(raw, extensions=['extra', 'toc'])


@app.route('/')
def index():
    return render_template('index.html', curso=CURSO, semanas=get_semanas())


@app.route('/view/<path:filename>')
def view(filename):
    tema = next((t for t in TEMAS if t['filename'] == filename), None)
    if not tema:
        abort(404)
    content = load_md(filename)
    if content is None:
        abort(404)
    idx = TEMAS.index(tema)
    prev_ = TEMAS[idx - 1] if idx > 0 else None
    next_ = TEMAS[idx + 1] if idx < len(TEMAS) - 1 else None
    return render_template('visor.html', title=tema['titulo'], content=content,
                           prev=prev_, next=next_)


@app.route('/evaluacion/<semana_id>')
def evaluacion(semana_id):
    ev = EVALUACIONES.get(semana_id)
    if not ev:
        abort(404)
    return render_template('evaluacion.html', ev=ev, semana_id=semana_id)


@app.route('/calificar', methods=['POST'])
def calificar():
    data = request.get_json()
    semana_id  = data.get('semana_id', 's1')
    estudiante = data.get('estudiante', 'Estudiante')
    respuestas = data.get('respuestas', [])

    ev = EVALUACIONES.get(semana_id)
    if not ev:
        return jsonify({'error': 'Semana no encontrada'}), 404

    rag       = RAG.get(semana_id, {})
    preguntas = ev['preguntas']

    prompt = f"""Eres un evaluador académico experto en investigación de mercados constructivista.

RAG DEL CURSO (contexto semántico):
{json.dumps(rag, ensure_ascii=False)}

PREGUNTAS:
{json.dumps(preguntas, ensure_ascii=False)}

RESPUESTAS DEL ESTUDIANTE ({estudiante}):
{json.dumps(respuestas, ensure_ascii=False)}

Evalúa cada respuesta del 0 al 10.
Criterios: profundidad conceptual, uso del lenguaje del curso, coherencia, ejemplos concretos.

Responde ÚNICAMENTE en JSON válido con esta estructura exacta:
{{
  "estudiante": "{estudiante}",
  "resultados": [
    {{
      "pregunta": 1,
      "score": 0,
      "comentario": "comentario breve (máx 60 palabras)",
      "nivel": "insuficiente|básico|competente|destacado"
    }}
  ],
  "resumen": {{
    "total": 0,
    "promedio": 0.0,
    "fortalezas": "texto breve",
    "areas_mejora": "texto breve",
    "diagnostico": "diagnóstico de 2-3 oraciones del perfil conceptual"
  }}
}}"""

    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        scores = [r['score'] for r in result['resultados']]
        result['resumen']['total']    = sum(scores)
        result['resumen']['promedio'] = round(sum(scores) / len(scores), 1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/diagnostico')
def diagnostico():
    return redirect('https://evaluaciones-edu046.onrender.com')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
