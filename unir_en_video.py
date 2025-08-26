import os
import re
import cv2
from datetime import datetime

# 📁 Carpeta con las imágenes
image_folder = "C://Users//calde//OneDrive - Pontificia Universidad Javeriana//Pictures//metro"
output_video = "timelapse.mp4"
fps = 30  # fotogramas por segundo

# 🧠 Expresión regular para extraer timestamp
pattern = re.compile(r"metroLocal_IPC_main_(\d{14})\.jpg")

# 📂 Lista de archivos con sus timestamps
images = []

for filename in os.listdir(image_folder):
    match = pattern.match(filename)
    if match:
        timestamp_str = match.group(1)
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
            images.append((timestamp, filename))
        except ValueError:
            print(f"❌ Formato inválido en {filename}")

# 📅 Ordenar las imágenes por timestamp
images.sort()

if not images:
    raise ValueError("No se encontraron imágenes con el formato esperado.")

# 🚨 Verificar huecos de más de 10 minutos
print("🔎 Verificando huecos mayores a 10 minutos entre imágenes...")

GAP_THRESHOLD_MINUTES = 10
for i in range(1, len(images)):
    delta = (images[i][0] - images[i - 1][0]).total_seconds() / 60.0
    if delta > GAP_THRESHOLD_MINUTES:
        print(f"🚨 Hueco detectado: {images[i-1][1]} ➡ {images[i][1]} ({delta:.1f} minutos)")

# 🖼️ Leer la primera imagen para obtener tamaño
first_image_path = os.path.join(image_folder, images[0][1])
frame = cv2.imread(first_image_path)
if frame is None:
    raise ValueError(f"No se pudo leer la imagen: {images[0][1]}")
height, width, _ = frame.shape

# 🎥 Crear el objeto de video con codificador compatible
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MPEG-4
video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# ⏩ Agregar cada imagen al video
for _, filename in images:
    path = os.path.join(image_folder, filename)
    frame = cv2.imread(path)
    if frame is None:
        print(f"⚠️ No se pudo leer {filename}")
        continue
    resized = cv2.resize(frame, (width, height))  # opcional
    video.write(resized)

video.release()
print(f"✅ Video generado: {output_video}")
