import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from wordcloud import STOPWORDS
import os

#Palabras que no aportan valor
stopwords_es = set(STOPWORDS).union({
    'de', 'que', 'y', 'en', 'la', 'el', 'los', 'las', 'con', 'por', 'para', 
    'una', 'un', 'es', 'al', 'lo', 'como', 'más', 'a', 'se', 'del', 'o', 'esta'
    'sin', 'sus', 'le', 'ha', 'este', 'su', 'no', 'muy', 'me', 'si', 'pero', 
    'ya', 'todo', 'también', 'fue', 'entre', 'sobre', 'ser', 'hay', 'cuando',
    'son', 'estos', 'nos', 'ni', 'que', 'algo', 'hasta', 'está', 'qué', 'día',
    'han', 'va', 'e', 'S', 'http', 'https', 'esa', 'ese', 'eso', 't', 'co'
})
#--------------------------------------------------------------------------------------------

def grafico_barras(data_df):
    plt.figure(figsize=(5,5))
    sns.countplot(x='Sentimiento',data=data_df)
    output_folder = os.path.join('src', 'images', 'grafico_barras.png')
    plt.savefig(output_folder, dpi=300, bbox_inches='tight')
#--------------------------------------------------------------------------------------------

def grafico_pastel(data_df):
    plt.figure(figsize=(7,7))
    colors = ("yellowgreen", "gold", "red")
    wp = {'linewidth':2, 'edgecolor':"black"}

    #Fuente de datos
    tags = data_df['Sentimiento'].value_counts()

    explode = (0.1,0.1,0.1)
    tags.plot(kind='pie', autopct='%1.1f%%', shadow=True, colors = colors,
            startangle=90, wedgeprops = wp, explode = explode, label='')

    plt.title("Distribucion de sentimientos")
    output_folder = os.path.join('src', 'images', 'grafico_pastel.png')
    plt.savefig(output_folder, dpi=300, bbox_inches='tight')
#--------------------------------------------------------------------------------------------

def panel_wordcloud(data_df, sentiment):
    #Para todos los sentimientos
    words_tweets=data_df[data_df['Sentimiento']==sentiment]
    words_tweets.head() #Muestra parte de lo tomado

    if len(words_tweets)!=0:
        text = ' '.join([word for word in words_tweets['Contenido']])
        plt.figure(figsize=(20,15), facecolor='None')

        wordcloud = WordCloud(max_words=500, width=1600, height=800, stopwords=stopwords_es).generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title(f"Palabras mas frecuentes en tweets ({sentiment})", fontsize=19)

        output_folder = os.path.join('src', 'images', f'wordcloud_{sentiment}.png')
        plt.savefig(output_folder, dpi=300, bbox_inches='tight')
    else:
        print("No hay datos para analizar")