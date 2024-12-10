#Atributos para Twitter
from twikit import Client, errors
from configparser import ConfigParser

#Funciones extra
import os
import asyncio

#Logueo en X (Twitter)
config = ConfigParser()
config.read('config.ini')

#Credenciales
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

#Localización
latitud = config['LOCATION']['latitude']
longitud = config['LOCATION']['longitude']
radio = config['LOCATION']['radius']

client = Client(language='es')

async def login_client(username, email, password, max_retries = 3):
    #Acceso a las credenciales desde cookies
    cookies_file = 'cookies.json'
    retries = 0

    while retries < max_retries:
        try:
            if os.path.exists(cookies_file):
                client.load_cookies('cookies.json')
                print("Cookies cargadas con éxito")
                return client

            print("Cookies no encontradas. Iniciando sesión ...")
            await client.login(auth_info_1=username, auth_info_2=email, password=password)
            client.save_cookies('cookies.json')
            print(f"Archivo {cookies_file} creado")
        
        #Fallo en cookies "caducadas"
        except errors.Unauthorized as e:
            print(f"Error de autenticación (401): {e}")
            if os.path.exists(cookies_file):
                os.remove(cookies_file)
                print(f"Archivo {cookies_file} eliminado. Reintentando inicio de sesión")
            retries += 1

        except Exception as e:
            print(f"Error inesperado: {e}")
            break

    print("Fallos en autenticación")
    raise RuntimeError("No se pudo iniciar sesión después de varios intentos")

asyncio.run(login_client(username, email, password))