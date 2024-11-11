from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flask_cors import CORS
import sys

app = Flask(__name__)
CORS(app)

# Cargar el modelo
with open('tiempos-vuelo.pkl', 'rb') as f:
    model = pickle.load(f)


# Cargar el modelo y el diccionario
model = pickle.load(open('tiempos-vuelo.pkl', 'rb'))
dictionary = pickle.load(open('tiempos-vuelo-dict.pkl', 'rb'))
df_raw = pd.DataFrame.from_dict(dictionary)

@app.route('/predict', methods=['POST'])
def predict():
    # Obtener los datos de la solicitud
    data = request.get_json()

    print(data, file=sys.stdout)

    # Transformar la fecha
    data['Fecha'] = pd.to_datetime(data['Fecha'])
    data['dia_nombre'] = data['Fecha'].day_name()
    data['dia_numero'] = data['Fecha'].day
    data['mes_numero'] = data['Fecha'].month
    #data['temporada_alta'] = 1# data['Fecha'].month.isin([12, 1, 2, 3]).astype(int)

    # Determinar la temporada alta
    data['temporada_alta'] = check_peak_season(data['Fecha'])

    # Eliminar la columna original 'Fecha'
    del data['Fecha']

    print(data, file=sys.stdout)

    # Crear un DataFrame con los datos de entrada
    input_data = pd.DataFrame([data])

    # Hacer la predicción
    prediction = model.predict(input_data)[0]

    hours = prediction // 60  # Truncating integer division
    minutes = prediction % 60
    #return str(prediction)
    resultado =  str(round(hours)).zfill(2) + ":" + str(round(minutes)).zfill(2)
    return jsonify({'duration': resultado})

    #duration = pd.to_datetime(prediction, format='%H%M')
   #return str(duration)
    #return jsonify({'Duración del vuelo': prediction})

@app.route("/")
def index():
    return 'La app esta funcionando'

# Determinar si el vuelo es de temporada alta
# temporada alta = 1 si Fecha está entre 15-Dic y 3-Mar, o 15-Jul y 31-Jul, o 11-Sep y 30-Sep, 0 si no.

def check_peak_season(date):
    # Convertimos la fecha a datetime y extraemos el mes y el día
    date = pd.to_datetime(date)
    month_day = (date.month, date.day)

    # Definimos los rangos de temporada alta solo con mes y día
    season_ranges = [
        ((12, 15), (12, 31)),  # 15 de diciembre a 31 de diciembre
        ((1, 1), (3, 3)),      # 1 de enero a 3 de marzo
        ((7, 15), (7, 31)),    # 15 de julio a 31 de julio
        ((9, 11), (9, 30))     # 11 de septiembre a 30 de septiembre
    ]

    # Verificamos si la fecha está en cualquiera de los rangos de temporada alta
    for start, end in season_ranges:
        if start <= month_day <= end:
            return 1  # Temporada alta
    return 0  # Fuera de temporada alta


if __name__ == '__main__':
    app.run()