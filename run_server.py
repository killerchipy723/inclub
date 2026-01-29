from waitress import serve
from app import app   # ← tu archivo principal

serve(
    app,
    host="0.0.0.0",     # Permite acceso desde otros dispositivos de la red
    port=6900,          # Puerto de tu API
    threads=8           # Maneja múltiples usuarios
)
