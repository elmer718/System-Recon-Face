from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, url_for, session
import cv2
import base64
import numpy as np
from mtcnn.mtcnn import MTCNN
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- Decodificar la imagen --------------------------
def decode_image(image_data):
    encoded_data = image_data.split(',')[1]
    img_data = base64.b64decode(encoded_data)
    np_arr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

# ------------------ Función de similitud usando ORB --------------------
def orb_sim(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    similar_regions = [i for i in matches if i.distance < 70]
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)

# -------------------- Ruta de Login Facial -------------------------
@app.route('/login_face', methods=['POST'])
def login_face():
    if request.method == 'POST':
        image_data = request.form['image']
        frame = decode_image(image_data)

        username = request.form['user_id']
        saved_image_path = f"static/faces/{username}.jpg"
        
        if os.path.exists(saved_image_path):
            # Comparar rostros usando ORB
            saved_image = cv2.imread(saved_image_path, 0)
            login_image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            similarity = orb_sim(saved_image, login_image_gray)

            if similarity >= 0.95:
                # Obtener la fecha y hora actuales
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Guardar usuario en la sesión
                session['user'] = {'name': username,
                                   'image': saved_image_path,
                                   'last_login': current_time} 
                
                return redirect(url_for('dashboard'))
            else:
                return "Rostro no coincide. Intente de nuevo."
        else:
            flash('Usuario no encontrado')
            return render_template('login.html')

# ------------------ Ruta de Registro Facial ----------------------
@app.route('/register_face', methods=['POST'])
def register_face():
    if request.method == 'POST':
        image_data = request.form['image']
        frame = decode_image(image_data)
        
        # Detectar el rostro
        detector = MTCNN()
        results = detector.detect_faces(frame)
        if results:
            # Guardar imagen de registro
            username = request.form['user_id']
            save_path = f"static/faces/{username}.jpg"
            cv2.imwrite(save_path, frame)
            flash('Registro exitoso')
            return redirect(url_for('index'))
        else:
            flash('No se detectó ningún rostro. Intente de nuevo')
            return render_template('register.html')

# ------------------ Ruta del Dashboard --------------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user_data = session['user']
        return render_template('dashboard.html', user_data=user_data)
    else:
        return redirect(url_for('index'))

# ---------------- Ruta de Inicio --------------------
@app.route('/')
def index():
    return render_template('login.html')

# --------------- Ruta de Registro -------------------
@app.route('/register')
def register():
    return render_template('register.html')

#----------------- Ruta de Salida --------------------
@app.route('/logout')
def logout():
    session.pop('user', None)  # Elimina el usuario de la sesión
    return redirect(url_for('index'))  # Redirige al login después de cerrar sesión

if __name__ == '__main__':
    if not os.path.exists('faces'):
        os.makedirs('faces')
    app.run(debug=True)