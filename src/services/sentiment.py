#Modelo para sentimiento
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
import os

#Uso del modelo BERT
MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
ROBERTA_SUPPORTED_LANGUAGES = ('ar', 'en', 'fr', 'de', 'hi', 'it', 'sp', 'pt')
ROBERTA_SUPPORTED_LANGUAGES = [lang.lower() for lang in ROBERTA_SUPPORTED_LANGUAGES]

model = AutoModelForSequenceClassification.from_pretrained(MODEL)
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)

if not os.path.exists(MODEL):
    #Traer todo el entrenamiento del modelo
    model.save_pretrained(MODEL)
    tokenizer.save_pretrained(MODEL)
    print(f"Carpeta de entrenamiento {MODEL} creado")
else:
    print(f"La carpeta {MODEL} ya existe")