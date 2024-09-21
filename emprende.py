import streamlit as st
import requests
import json

# Configuración de la API Key
api_key = st.secrets["together_api_key"]

# Función para interactuar con la API de Together y generar gastos estimados
def call_together_api_for_expenses(idea):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": f"Genera una estimación de gastos mensuales (alquiler, sueldos, marketing, otros) para un emprendimiento con la siguiente idea: {idea}"}],
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Inicializa los datos
if 'capital_inicial' not in st.session_state:
    st.session_state['capital_inicial'] = 0
    st.session_state['gastos'] = []
    st.session_state['ingresos'] = []
    st.session_state['capital_actual'] = 0
    st.session_state['mes_actual'] = 1
    st.session_state['gastos_estimados'] = {}

# Título de la aplicación
st.title("Simulador de Emprendimiento")

# Paso 1: Introducir el capital inicial y la idea de emprendimiento
st.header("Paso 1: Inicia tu emprendimiento")

capital_inicial = st.number_input("Introduce tu capital inicial:", min_value=0, step=1000)
idea_emprendimiento = st.text_input("Describe tu idea de emprendimiento:")

if st.button("Iniciar Emprendimiento"):
    st.session_state['capital_inicial'] = capital_inicial
    st.session_state['capital_actual'] = capital_inicial
    st.session_state['idea_emprendimiento'] = idea_emprendimiento

    # Llamada a la API de Together para obtener estimaciones de gastos
    response = call_together_api_for_expenses(idea_emprendimiento)
    estimated_expenses = response['choices'][0]['message']['content']
    
    # Convertir el resultado en un diccionario de gastos
    st.session_state['gastos_estimados'] = {
        'alquiler': 1000,
        'sueldos': 2000,
        'marketing': 500,
        'otros': 300
    }

    # Puedes ajustar esta conversión según la respuesta generada por la API
    # Actualmente, se ha simulado una respuesta
    st.success(f"Emprendimiento iniciado con {capital_inicial} de capital.")

# Mostrar gastos estimados generados por la API
if 'gastos_estimados' in st.session_state:
    st.subheader("Gastos estimados basados en tu idea:")
    gastos = st.session_state['gastos_estimados']
    st.write(f"Alquiler estimado: {gastos['alquiler']}")
    st.write(f"Sueldos estimados: {gastos['sueldos']}")
    st.write(f"Gastos en marketing estimados: {gastos['marketing']}")
    st.write(f"Otros gastos estimados: {gastos['otros']}")

# Paso 2: Agregar ingresos mensuales
st.header(f"Paso 2: Simula el Mes {st.session_state['mes_actual']}")

# Ingresos
ingreso = st.number_input("Introduce tus ingresos este mes:", min_value=0, step=100)

# Gastos estimados automáticos
gasto_alquiler = st.session_state['gastos_estimados'].get('alquiler', 0)
gasto_sueldos = st.session_state['gastos_estimados'].get('sueldos', 0)
gasto_marketing = st.session_state['gastos_estimados'].get('marketing', 0)
gasto_otros = st.session_state['gastos_estimados'].get('otros', 0)

# Calcular total de gastos
gasto_total = gasto_alquiler + gasto_sueldos + gasto_marketing + gasto_otros

if st.button("Actualizar Mes"):
    st.session_state['ingresos'].append(ingreso)
    st.session_state['gastos'].append({
        'mes': st.session_state['mes_actual'],
        'alquiler': gasto_alquiler,
        'sueldos': gasto_sueldos,
        'marketing': gasto_marketing,
        'otros': gasto_otros,
        'total': gasto_total
    })
    st.session_state['capital_actual'] += (ingreso - gasto_total)
    st.session_state['mes_actual'] += 1

    # Mostrar resultados
    st.success(f"Capital actualizado: {st.session_state['capital_actual']}")

# Paso 3: Mostrar resultados
st.header("Resumen del Emprendimiento")
st.write(f"Capital inicial: {st.session_state['capital_inicial']}")
st.write(f"Capital actual: {st.session_state['capital_actual']}")
st.write(f"Total ingresos: {sum(st.session_state['ingresos'])}")
st.write(f"Total gastos hasta el momento: {sum(g['total'] for g in st.session_state['gastos'])}")

# Mostrar gastos detallados por mes
st.subheader("Gastos detallados por mes:")
for gasto in st.session_state['gastos']:
    st.write(f"Mes {gasto['mes']}: Alquiler: {gasto['alquiler']}, Sueldos: {gasto['sueldos']}, Marketing: {gasto['marketing']}, Otros: {gasto['otros']}, Total: {gasto['total']}")

if st.session_state['capital_actual'] <= 0:
    st.error("¡Has quebrado! El capital actual es 0 o negativo.")
