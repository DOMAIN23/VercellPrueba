import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv('data/datos_entrenamiento.csv', sep=';', encoding='utf-8')


print("Columnas del archivo CSV:", df.columns)


if 'Desercion' not in df.columns:
    raise ValueError("El archivo debe contener la columna 'Desercion'.")
else:

    df['Tipo de Colegio'] = df['Tipo de Colegio'].map({'Público': 1, 'Privado': 0})


X = df[['Notas', 'Asistencia (%)', 'Ingresos Familiares (S/.)', 'Tipo de Colegio']]
y = df['Desercion']  


modelo = RandomForestClassifier()
modelo.fit(X, y)


joblib.dump(modelo, 'app/modelo_desercion.pkl')
le = LabelEncoder()
le.fit(df['Tipo de Colegio'])
joblib.dump(le, 'app/label_encoder.pkl')

print("Modelo entrenado y guardado correctamente.")
