from flask import Flask, render_template, request, flash, redirect, url_for
import pandas as pd
import numpy as np
import plotly.express as px
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash("No se seleccionó ningún archivo.")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash("No se seleccionó ningún archivo.")
        return redirect(url_for('index'))

    # Guardar el archivo temporalmente
    file_path = os.path.join("temp", file.filename)
    file.save(file_path)

    # Procesar el archivo con pandas
    try:
        df = pd.read_excel(file_path) if file.filename.endswith('.xlsx') else pd.read_csv(file_path)
    except Exception as e:
        flash(f"Error al cargar el archivo: {e}")
        return redirect(url_for('index'))

    required_columns = ["x", "y"]
    for col in required_columns:
        if col not in df.columns:
            flash(f"La columna '{col}' no está presente en el archivo.")
            return redirect(url_for('index'))

    x = df['x']
    y = df['y']

    # Crear la gráfica interactiva con Plotly
    fig = px.scatter(x=x, y=y, labels={'x': 'Publicidad (minutos)', 'y': 'Ventas (unidades)'}, title='Relación entre Publicidad y Ventas')

    # Calcular el coeficiente de determinación R^2
    line_fit = np.polyfit(x, y, 1)
    y_pred = np.polyval(line_fit, x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Interpretación de la tendencia de la recta
    slope = line_fit[0]
    if slope > 0:
        trend = "positiva"
        interpretation = "A medida que aumenta la publicidad (minutos), las ventas (unidades) tienden a aumentar."
    elif slope < 0:
        trend = "negativa"
        interpretation = "A medida que aumenta la publicidad (minutos), las ventas (unidades) tienden a disminuir."
    else:
        trend = "nula"
        interpretation = "No hay una relación clara entre la publicidad (minutos) y las ventas (unidades)."

    # Convertir la figura a JSON para usarla en el HTML
    graph_json = fig.to_json()

    # Eliminar el archivo temporal
    os.remove(file_path)

    return render_template('index.html', graph_json=graph_json, r_squared=r_squared, trend=trend, interpretation=interpretation)

if __name__ == '__main__':
    if not os.path.exists("temp"):
        os.makedirs("temp")
    app.run(debug=True)