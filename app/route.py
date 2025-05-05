from flask import Flask, request, render_template, redirect, url_for
import os
import pandas as pd
import joblib
import chardet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

def init_routes(app):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    model_path = os.path.join(current_dir, 'models', 'modelo_desercion.pkl')
    le_path = os.path.join(current_dir, 'models', 'label_encoder.pkl')

    modelo = joblib.load(model_path)
    le = joblib.load(le_path)

    # Ruta de login
    @app.route('/', methods=['GET', 'POST'])
    def login():
        return render_template('login.html')

    # Ruta para Profesor (Redirige a principal.html)
    @app.route('/entrar_profesor', methods=['GET'])
    def entrar_profesor():
        return redirect(url_for('principal'))

    # Ruta para Estudiante (Redirige a estudiantes.html)
    @app.route('/entrar_estudiante', methods=['GET'])
    def entrar_estudiante():
        return render_template('estudiantes.html')

    # Ruta intermedia para profesor (menú principal)
    @app.route('/principal', methods=['GET'])
    def principal():
        return render_template('principal.html')

    # Ruta para procesar archivo CSV en index.html
    @app.route('/index', methods=['GET', 'POST'])
    def index():
        data = []
        columns = []
        report = ''
        alertas = []

        if request.method == 'POST':
            archivo = request.files.get('archivo')

            if archivo and archivo.filename.endswith('.csv'):
                path = os.path.join(app.config['UPLOAD_FOLDER'], 'archivo_usuario.csv')
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                archivo.save(path)

                try:
                    with open(path, 'rb') as f:
                        result = chardet.detect(f.read())
                        encoding = result['encoding']

                    df_usuario = pd.read_csv(path, sep=';', encoding=encoding)

                    columnas_necesarias = ['Notas', 'Asistencia (%)', 'Ingresos Familiares (S/.)', 'Tipo de Colegio']
                    if not all(col in df_usuario.columns for col in columnas_necesarias):
                        raise ValueError("El archivo debe contener las columnas necesarias.")

                    # Convertir valores
                    df_usuario['Tipo de Colegio'] = df_usuario['Tipo de Colegio'].str.lower().map({'público': 1, 'privado': 0})

                    if df_usuario['Tipo de Colegio'].isnull().any():
                        raise ValueError("Valores no válidos en 'Tipo de Colegio'. Usa 'Público' o 'Privado'.")

                    X = df_usuario[['Notas', 'Asistencia (%)', 'Ingresos Familiares (S/.)', 'Tipo de Colegio']]
                    predicciones = modelo.predict(X)

                    df_usuario['Predicción Deserción'] = predicciones
                    df_usuario['Tipo de Colegio'] = df_usuario['Tipo de Colegio'].map({1: 'Público', 0: 'Privado'})

                    # Generar alertas
                    for idx, row in df_usuario.iterrows():
                        if row['Predicción Deserción'] == 1:
                            id_estudiante = idx + 1
                            mensaje = f"⚠️ Alerta: El estudiante con ID {id_estudiante} tiene riesgo de deserción. ¡Actúa con anticipación!"
                            alertas.append(mensaje)

                    columns = df_usuario.columns.tolist()
                    data = df_usuario.to_dict(orient='records')

                except Exception as e:
                    report = f"Ocurrió un error al procesar el archivo: {str(e)}"
            else:
                report = "Por favor sube un archivo CSV válido."

        return render_template('index.html', data=data, columns=columns, report=report, alertas=alertas)
