import time
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# Leer el archivo Excel
df = pd.read_excel('Base_datos.xlsx', sheet_name='Bruto')

df['Posc'] = df['Posc'].replace({'PO': 'Portero', 'DF': 'Defensa', 'CC': 'Centrocampista', 'DL': 'Delantero'})

# Obtener las características numéricas para el cálculo de similitud
caracteristicas_numericas = df.select_dtypes(include=[float])

# Calcular la similitud coseno entre los jugadores basada en características numéricas
similitud = cosine_similarity(caracteristicas_numericas)

def obtener_jugadores_similares(jugador, n=5, rango_edad=None, posicion=None):
    # Obtener el índice del jugador seleccionado en el DataFrame
    indice_jugador = df.index[df['Jugador'] == jugador].tolist()[0]

    # Obtener los índices de los jugadores más similares en el DataFrame (excluyendo al propio jugador)
    similitudes_jugadores = similitud[indice_jugador]
    indices_similares = similitudes_jugadores.argsort()[::-1][1:]  # Orden descendente, excluyendo el propio jugador

    # Aplicar filtro de edad si se proporciona un rango
    if rango_edad:
        df_filtrado = df[df['Edad'].between(*rango_edad)]
        indices_similares = [indice for indice in indices_similares if indice in df_filtrado.index]
    else:
        df_filtrado = df

    # Aplicar filtro de posición si se proporciona una posición
    if posicion:
        df_filtrado = df_filtrado[df_filtrado['Posc'] == posicion]
        indices_similares = [indice for indice in indices_similares if indice in df_filtrado.index]

    # Verificar si la lista de jugadores similares está vacía
    if len(indices_similares) == 0:
        return pd.DataFrame({'Mensaje': ['No se encontraron jugadores similares']})

    # Obtener los nombres y las puntuaciones de similitud de los jugadores similares
    jugadores_similares = pd.DataFrame()
    jugadores_similares['Jugador'] = df_filtrado.loc[indices_similares]['Jugador']
    jugadores_similares['Posición'] = df_filtrado.loc[indices_similares, 'Posc']
    jugadores_similares['Edad'] = df_filtrado.loc[indices_similares, 'Edad']
    jugadores_similares['Equipo'] = df_filtrado.loc[indices_similares, 'Equipo']
    jugadores_similares['Similitud'] = similitudes_jugadores[indices_similares].round(3)

    # Agregar una columna de ranking
    jugadores_similares['Ranking'] = range(1, len(jugadores_similares) + 1)

    return jugadores_similares.head(n)

# Configurar la interfaz de Streamlit
st.set_page_config(page_title='Jugadores Similares', layout='wide')

# Cabecera
st.title('Jugadores Similares')
st.markdown("## **[Creado por: @pedrosaezarenas](https://www.twitter.com/pedrosaezarenas)**")

# Filtro de jugador en la barra lateral
jugadores = df['Jugador'].tolist()
jugador_seleccionado = st.sidebar.selectbox('Selecciona un jugador:', jugadores)

n_jugadores_similares = st.sidebar.slider('Número de jugadores similares:', 1, 10, 5)

edad_minima = int(df['Edad'].min())
edad_maxima = int(df['Edad'].max())
rango_edad = st.sidebar.slider('Rango de edad:', min_value=edad_minima, max_value=edad_maxima, value=(edad_minima, edad_maxima))

posiciones = ['Ninguna', 'Portero', 'Defensa', 'Centrocampista', 'Delantero']
posicion_seleccionada = st.sidebar.selectbox('Selecciona una posición:', posiciones, index=0)

if posicion_seleccionada == 'Ninguna':
    posicion_seleccionada = None

jugadores_similares = obtener_jugadores_similares(jugador_seleccionado, n_jugadores_similares, rango_edad, posicion_seleccionada)

# Mostrar la información básica del jugador seleccionado
jugador_info = df[df['Jugador'] == jugador_seleccionado][['Jugador', 'Edad', 'Equipo', 'Liga']].iloc[0]
st.sidebar.markdown('---')
st.sidebar.subheader('Información del jugador:')
st.sidebar.markdown(f"**Nombre:** {jugador_info['Jugador']}")
st.sidebar.markdown(f"**Edad:** {jugador_info['Edad']}")
st.sidebar.markdown(f"**Equipo:** {jugador_info['Equipo']}")
st.sidebar.markdown(f"**Liga:** {jugador_info['Liga']}")

# Mostrar los jugadores similares en una tabla
if 'Mensaje' in jugadores_similares.columns:
    st.subheader(f'Jugadores similares a {jugador_seleccionado}:')
    st.text(jugadores_similares['Mensaje'].iloc[0])
else:
    tabla_jugadores_similares = jugadores_similares[['Ranking', 'Jugador', 'Posición', 'Edad', 'Equipo', 'Similitud']].reset_index(drop=True)
    tabla_jugadores_similares_string = tabla_jugadores_similares.to_string(index=False)
    st.subheader(f'Jugadores similares a {jugador_seleccionado}:')
    st.text(tabla_jugadores_similares_string)

# Pie de página
st.markdown('---')
st.text("Pedro Sáez, Ingeniero Informático - Análisis con Big Data y técnicas de IA en el Fútbol")

# Leyenda sobre la similitud
st.markdown('---')
st.subheader('¿Cómo funciona la similitud?')
st.markdown('La similitud en esta aplicación se calcula utilizando una medida llamada *similitud coseno*. '
            'Esta medida compara las características numéricas de los jugadores y calcula la similitud '
            'entre ellos. Cuanto más cercano sea el valor de similitud a 1, más similares serán los '
            'jugadores en términos de sus características numéricas.')

st.markdown('El cálculo de similitud se basa en un conjunto de características numéricas de los jugadores, '
            'como su edad, estadísticas de juego, rendimiento, etc. Utilizando estas características, se '
            'construye una representación numérica de cada jugador. Luego, se calcula la similitud coseno '
            'entre los jugadores, lo que nos permite encontrar los jugadores más similares a uno dado.')

st.markdown('La aplicación permite seleccionar un jugador y encontrar los jugadores más similares en términos '
            'de características numéricas, considerando filtros opcionales como rango de edad y posición. '
            'Esto puede ser útil para identificar jugadores con perfiles similares o comparar jugadores en '
            'diferentes aspectos.')

st.markdown('Recuerda que la similitud se basa únicamente en características numéricas y no tiene en cuenta '
            'otros aspectos como habilidades técnicas, estilo de juego, etc. Es importante considerar estos '
            'factores adicionales al analizar la similitud entre jugadores.')

# Sección de sugerencias o errores
st.markdown('---')
st.subheader('Sugerencias o Errores')
st.markdown('Si tienes alguna sugerencia para mejorar esta aplicación o has encontrado algún error, '
            'por favor, no dudes en contactarme. Puedes enviarme un correo electrónico a '
            '[elingenierodelbigdata@gmail.com](mailto:elingenierodelbigdata@gmail.com) con tus comentarios.')

st.markdown('¡Gracias por tu colaboración!')
