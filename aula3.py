from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import pyautogui
import threading

app = Flask(__name__)

# Inicializar a câmera
cam = cv2.VideoCapture(0)

# Inicializar o modelo FaceMesh do Mediapipe
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Obter a largura e altura da tela usando PyAutoGUI
screen_w, screen_h = pyautogui.size()

# Obter a largura e altura do frame da câmera
frame_h, frame_w = None, None

def process_camera_feed():
    global frame_h, frame_w
    while True:
        # Ler um frame da câmera
        _, frame = cam.read()
        
        # Inicializar frame_h e frame_w
        if frame_h is None or frame_w is None:
            frame_h, frame_w, _ = frame.shape

        # Espelhar o frame horizontalmente
        frame = cv2.flip(frame, 1)

        # Converter o frame de BGR para RGB (necessário pelo Mediapipe)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processar o frame RGB usando o modelo FaceMesh para detectar pontos faciais
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks

        if landmark_points:
            # Obter os pontos faciais do primeiro rosto detectado
            landmarks = landmark_points[0].landmark

            # Obter landmarks dos cantos dos olhos (por exemplo, 133 e 362 para o olho esquerdo)
            eye_landmarks = [landmarks[133], landmarks[362]]

            # Calcular a posição média dos landmarks dos olhos
            eye_x = int((eye_landmarks[0].x + eye_landmarks[1].x) * frame_w / 2)
            eye_y = int((eye_landmarks[0].y + eye_landmarks[1].y) * frame_h / 2)

            # Calcular a posição do cursor com base na posição dos olhos
            screen_x = screen_w * (eye_x / frame_w)
            screen_y = screen_h * (eye_y / frame_h)

            # Mover o cursor para a nova posição
            pyautogui.moveTo(screen_x, screen_y)

            # Obter landmarks correspondentes ao olho esquerdo (landmarks 145 e 159)
            left = [landmarks[145], landmarks[159]]

            # Verificar se o usuário pisca o olho esquerdo (diferença na coordenada y é pequena)
            if (left[0].y - left[1].y) < 0.004:
                pyautogui.click()
                pyautogui.sleep(1)

        # Codificar o frame para o formato JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            # Enviar o frame como bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(process_camera_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Iniciar a captura de vídeo em um thread separado
    video_thread = threading.Thread(target=process_camera_feed)
    video_thread.daemon = True
    video_thread.start()

    app.run(debug=True, threaded=True)
