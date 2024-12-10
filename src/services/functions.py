from twikit import TooManyRequests

#Modularidad
from src.services.config_client import client
from src.services.sentiment import model, tokenizer, config

#Tratamiento de datos
import pandas as pd
import neattext.functions as nfx

#Funciones extra
import os
import chardet
import time
from datetime import datetime
from random import randint

#Evitando texto erróneo
def clean_text(text):
    try:
        #Codificación original del texto
        detected_encoding = chardet.detect(text.encode())['encoding']
        
        #Conversión necesaria a UTF-8
        if detected_encoding:
            text = text.encode(detected_encoding).decode('utf-8')
                
    except Exception as e:
        print(f"Error al procesar el texto: {text} - {e}")
    
    return text
#--------------------------------------------------------------------------------------------

#Scrappeo de tweets
async def get_tweets(t_params, tweets, mes):
    #Si se usa localización precisa
    location = ""

    #Búsqueda avanzada
    if ('loc' in t_params and t_params['loc']):
        loc = t_params['loc']
        location = f"lang:{loc['lang']} geocode:{loc['latitud']},{loc['longitud']},{loc['radio']} "

    QUERY = f"{t_params['query']} {location}until:{t_params['anio']}-{mes}-31 since:{t_params['anio']}-{mes}-01"

    if tweets is None:
        print(f'{datetime.now()} - Obteniendo tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(1, 3)
        print(f'{datetime.now()} - Obteniendo siguientes tweets en {wait_time} segundo(s)...')
        time.sleep(wait_time)
        tweets = await tweets.next()
    
    return tweets
#--------------------------------------------------------------------------------------------

#Calificación del texto (sentimiento)
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

#--------------------------------------------------------------------------------------------
def predict_sentiment(text: str) -> str:
    processed_text = preprocess(text)
    encoded_input = tokenizer(processed_text, return_tensors='pt')
    output = model(**encoded_input)
    index_of_sentiment = output.logits.argmax().item()
    sentiment = config.id2label[index_of_sentiment]

    return sentiment
#--------------------------------------------------------------------------------------------

#Extracción de tweets
async def scrapping_tweets(t_params, tweets_csv, t_values, mes):
    MINIMUN_TWEETS = t_values['MINIMUN_TWEETS']
    tweet_count = t_values['tweet_count']

    while tweet_count < MINIMUN_TWEETS:
        #Solicitudes con espera
        try:
            t_values['tweets'] = await get_tweets(t_params, t_values['tweets'], mes)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting unitl {rate_limit_reset}')
            wait_time = rate_limit_reset - datetime.now()
            time.sleep(wait_time.total_seconds())
            continue

        if not t_values['tweets']:
            print(f'{datetime.now()} - No más tweets')
            break

        for tweet in t_values['tweets']:
            #Guardar tweets solo Lima - Perú y sin ID repetido
            cond1 = any(w in tweet.user.location.lower() for w in ("lima", "perú", "peru"))
            cond2 = tweet.id not in tweets_csv['ID']
            
            #Formateo de fecha
            fecha = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
            cond3 = (fecha.year == int(t_params['anio']))

            if (cond1 and cond2 and cond3):
                tweet_count += 1

                #Llenado de diccionario
                tweets_csv['ID'].append(tweet.id)

                fecha = fecha.strftime("%Y-%m-%d %H:%M:%S")
                tweets_csv['Fecha'].append(fecha)

                tweets_csv['Usuario'].append(tweet.user.name)
                tweets_csv['Contenido'].append(tweet.text)
                tweets_csv['Localización'].append(tweet.user.location)

                url = 'https://x.com/' + tweet.user.screen_name + '/status/' + tweet.id
                tweets_csv['URL'].append(url)

                tweets_csv['Seguidores'].append(tweet.user.followers_count)
                tweets_csv['Retweets'].append(tweet.retweet_count)
                tweets_csv['Likes'].append(tweet.favorite_count)

                #Asignación de sentimiento
                sentiment = predict_sentiment(tweet.text)
                tweets_csv['Sentimiento'].append(sentiment)
                        
        print(f'{datetime.now()} - Obtenidos {tweet_count} tweets')
#--------------------------------------------------------------------------------------------

#Guardado del dataset
def create_dataset(tweets_csv):
    df = pd.DataFrame(tweets_csv)
    df.sort_values(by='Likes', inplace=True, ascending=False)

    # Quitar saltos de línea y espacios en blanco de las columnas de texto
    df['Contenido'] = df['Contenido'].str.replace('\n', ' ', regex=True).str.strip()
    df['Localización'] = df['Localización'].str.replace('\n', ' ', regex=True).str.strip()

    #Limpieza de textos
    df['Contenido'] = df['Contenido'].apply(nfx.remove_urls)
    df['Contenido'] = df['Contenido'].apply(nfx.remove_multiple_spaces)
    df['Contenido'] = df['Contenido'].apply(nfx.remove_emojis)
    #df['Contenido'] = df['Contenido'].apply(clean_text)
    df['Usuario'] = df['Usuario'].apply(clean_text)

    file_path = os.path.join('src', 'files', 'tweets_final.csv')
    df.to_csv(file_path, sep=';', index=False)