import pandas as pd

def process_data(filepath):
    #Lectura del dataset
    data = pd.read_csv(filepath)

    data.rename(columns = {'Nacionality':'Nationality', 'Age at enrollment':'Age'}, inplace = True)
    data.isnull().sum()/len(data)*100

    #Conversión de variable objetivo
    data['Target'] = data['Target'].map({
        'Dropout': 0,
        'Enrolled': 1,
        'Graduate': 2
    })

    return data
#--------------------------------------------------------------------------------------------

def copy_data(data):
    new_data = data.copy()
    new_data = new_data.drop(columns=['Nationality', 'Mother\'s qualification',
                                        'Father\'s qualification', 'Educational special needs',
                                        'International', 'Curricular units 1st sem (without evaluations)',
                                        'Unemployment rate', 'Inflation rate'], axis=1)
    return new_data