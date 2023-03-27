import streamlit as st 
import pandas as pd 
import openai 
import os 

# Configuramos el diseño de la página 
st.set_page_config(layout="wide") 

# Agregamos una columna a la izquierda para la API y los criterios 
columna_api, columna_criterios, columna_ensayos = st.beta_columns([1, 1, 3]) 

# Pedimos al usuario que ingrese su API key 
api_key = columna_api.text_input("Ingresa tu API key de OpenAI:") 
if api_key: 
    openai.api_key = api_key 

# Pedimos al usuario que ingrese los criterios de evaluación 
criterios = [] 
while True: 
    criterio = columna_criterios.text_input("Ingresa un criterio de evaluación:") 
    descripcion = columna_criterios.text_input("Ingresa una descripción del criterio:") 
    if not criterio or not descripcion: 
        break 
    criterios.append({"Criterio": criterio, "Descripción": descripcion}) 

# Agregamos un título al principio 
st.title('Evaluador de ensayos') 

# Agregamos información de instrucciones 
st.write('Suba un archivo .XLSX con los ensayos de sus alumnos.') 

# Pedimos al usuario que suba el archivo Excel 
archivo = st.file_uploader('Cargar archivo Excel', type=['xlsx']) 
if archivo: 
    # Leemos el archivo con pandas 
    data = pd.read_excel(archivo) 

    # Pedimos al usuario que seleccione las columnas con el título y el ensayo 
    columnas = data.columns 
    columna_titulo = columna_ensayos.selectbox('Selecciona la columna que contiene los títulos:', columnas) 
    columna_ensayo = columna_ensayos.selectbox('Selecciona la columna que contiene los ensayos:', columnas) 

    # Agregamos un botón para iniciar la evaluación 
    if st.button('Evaluar'): 
        # Obtenemos los títulos y los ensayos del archivo 
        titulos = data[columna_titulo].tolist() 
        ensayos = data[columna_ensayo].tolist() 

        # Utilizamos la API de GPT-3 para calificar cada ensayo 
        resultados = [] 
        for i, ensayo in enumerate(ensayos): 
            prompt = f"Califica el ensayo titulado '{titulos[i]}'. Sé exigente al evaluar, quita puntos por mala ortografía. " 
            prompt += f"{ensayo}. " 
            for criterio in criterios: 
                prompt += f"{criterio['Criterio']}: {criterio['Descripción']}. " 
            response = openai.Completion.create( 
                engine="text-davinci-003", 
                prompt=prompt, 
                temperature=0, 
                max_tokens=512, 
                n=1, 
                stop=None, 
                timeout=5 
            ) 
            justificacion = response.choices[0].text.strip() 

            # Agregamos sugerencias de mejora a la justificación 
            response = openai.Completion.create( 
                engine="text-davinci-003", 
                prompt=f"Sugiere mejoras para el ensayo titulado '{titulos[i]}'. Ensayo: {ensayo}", 
                temperature=0, 
                max_tokens=512, 
                n=1, 
                stop=None, 
                timeout=5, 
            ) 
            sugerencias = response.choices[0].text.strip() 

            # Agregamos la calificación y las sugerencias de mejora a la tabla 
            resultados.append({ 
                'Ensayo': titulos[i], 
                'Justificación': justificacion, 
                'Sugerencias de mejora': sugerencias, 
            }) 

        # Mostramos los resultados en una tabla en un pop up 
        if len(resultados) > 0: 
            tabla_resultados = pd.DataFrame(resultados) 
            tabla_html = tabla_resultados.to_html(index=False) 
            st.write(f'<h2>Resultados:</h2>{tabla_html}', unsafe_allow_html=True, target='new') 
        else: 
            st.write("No se encontraron resultados")
