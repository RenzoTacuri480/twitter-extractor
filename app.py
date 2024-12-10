#Funciones extra
import os
import pandas as pd

#Generación de mapa de calor
from geopy.geocoders import Nominatim
import gmplot

#Uso de Flask para programa desplegable
from flask import Flask, request

#Modularidad
from src.services.functions import scrapping_tweets, create_dataset
from src.services.graphics import grafico_barras, grafico_pastel, panel_wordcloud
#--------------------------------------------------------------------------------------------

app = Flask(__name__)
#--------------------------------------------------------------------------------------------

#Diccionario de datos
tweets_csv = {'ID': [], 'Fecha': [], 'Usuario': [], 'Contenido': [], 'Localización': [], 'URL': [], 'Seguidores': [], 'Retweets': [], 'Likes': [], 'Sentimiento': []}
#--------------------------------------------------------------------------------------------

#Extracción completa y detallada
@app.route('/extract', methods=["POST"])
async def extraction_tweets():
    #Recibir parámetros
    t_params = {
        key: request.get_json().get(key) for key in ('query', 'anio')
    }
    loc_data = request.get_json().get('loc')

    #Si el usuario desea incluir locaclización precisa
    if loc_data:
        t_params['loc'] = {
            key: loc_data.get(key) for key in ('latitud', 'longitud', 'radio', 'lang')
        }
        print("Obtenidos parámetros de consulta")

    if not (t_params['query'] or t_params['anio']):
        return "Error en la consulta de búsqueda"
    
    #Solicitud de tweets y conteo
    t_values = {
        'MINIMUN_TWEETS': 100,
        'tweet_count': 0,
        'tweets': None
    }

    #Periodo de tiempo
    meses = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    #Búsuqeda completa y detallada
    for m in meses:
        await scrapping_tweets(t_params, tweets_csv, t_values, m)

        t_values['tweet_count'] = 0
        t_values['tweets'] = None
                
        print(f"-> Extraído del mes {m}")
    
    #Guardado en src/files/
    create_dataset(tweets_csv)

    return f"Extracción finalizada, se extrajeron {len(tweets_csv['ID'])} tweets"
#--------------------------------------------------------------------------------------------

#Elaboración de gráficos
@app.route('/graphs')
def create_graphs():
    df = pd.DataFrame(tweets_csv)

    #Objeto de análisis
    data_df = df.drop(['ID', 'Fecha', 'Usuario', 'Localización', 'URL', 'Seguidores', 'Retweets', 'Likes'], axis=1)

    grafico_barras(data_df)
    grafico_pastel(data_df)

    return "Gráficos creados con éxito"
#--------------------------------------------------------------------------------------------

#Wordcloud de palabras
@app.route('/wordcloud')
def create_wordclouds():
    df = pd.DataFrame(tweets_csv)

    #Objeto de análisis
    data_df = df.drop(['ID', 'Fecha', 'Usuario', 'Localización', 'URL', 'Seguidores', 'Retweets', 'Likes'], axis=1)

    sentiments = ["negative", "neutral", "positive"]

    for value in sentiments:
        panel_wordcloud(data_df, value)
    
    return "Wordclouds creados con éxito"
#--------------------------------------------------------------------------------------------

#Creación de mapa de calor
@app.route('/heatmap', methods=["POST"])
def create_heatmap():
    #Aprovechar coordenadas del JSON inicial
    t_params = request.get_json()
    loc_data = request.get_json().get('loc')
    zoom = 3 #Rango del mapa

    if loc_data:
        t_params['loc'] = {
            key: loc_data.get(key) for key in ('latitud', 'longitud')
        }
        zoom = 12
        print("Obtenidas coordenadas para el mapa")
    else:
        t_params['loc'] = {
            'latitud': 0, 'longitud': 0
        }
        print("Uso de coordenadas por defecto")

    geolocator = Nominatim(user_agent="BD-CR-APP")

    #Diccionario de coordenadas
    coordenadas = {'latitud': [], 'longitud': []}

    for user in enumerate(tweets_csv['Localización']):
        try:
            location = geolocator.geocode(user)

            #Recolección de ubicación
            if location:
                coordenadas['latitud'].append(location.latitude)
                coordenadas['longitud'].append(location.longitude)
        #Para un exceso de solicitudes
        except Exception as e:
            print(f"Excepción encontrada: {e}")
            pass
    
    #Centrar objeto GoogleMapPlotter para mostrar mapa
    gmap = gmplot.GoogleMapPlotter(t_params['loc']['latitud'], t_params['loc']['longitud'], zoom)

    #Insertar puntos en el mapa con lista de latitudes y longitudes
    gmap.heatmap(coordenadas['latitud'], coordenadas['longitud'], radius=20)

    file_map = os.path.join('src', 'files', 'tweets_heatmap.html')
    gmap.draw(file_map)

    return "Mapa de calor creado con exito"
#--------------------------------------------------------------------------------------------

#Ejecución final
if __name__ == '__main__':
    app.run(debug=True, port=5001)