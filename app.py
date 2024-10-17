import base64
import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime 

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Ruta donde se almacenarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Simulación de usuarios en la base de datos
usuarios = {
    "1234": {"name": "Juan Pérez", "id": "1234", "last_login": "", "image": ""},
    "5678": {"name": "María López", "id": "5678", "last_login": "", "image": ""}
}

# Página de inicio de sesión
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        image_data = request.form['image']
        
        # Verificar si el usuario existe
        if user_id in usuarios:
            # Decodificar la imagen base64
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)

            # Guardar la imagen en el servidor
            image_filename = f"{user_id}.png"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
                
            # Obtener la fecha y hora actuales
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            session['user'] = usuarios[user_id]
            session['user']['image'] = image_path
            session['user']['last_login'] = current_time
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_data = session['user']
        return render_template('dashboard.html', user_data=user_data)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
