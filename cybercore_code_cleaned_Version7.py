# -*- coding: utf-8 -*-
"""
wro_simple_line_counter.py
- Sistema simplificado de conteo de líneas (12 líneas = 3 vueltas)
- SIN magnetómetro - solo detección de líneas de color
- Pausa de 3 segundos después de detectar la línea 12
- Filtros de detección menos estrictos (90% menos)
- Valores RGB predeterminados: Naranja (255,102,0) y Azul (0,51,255)
"""

import cv2
import numpy as np
import threading
import time
import argparse
import json
import os

# GPIO
try:
    from gpiozero import Motor, Servo, PWMOutputDevice, DigitalOutputDevice, Button
    # Intentar usar pigpio para mejor PWM en servos
    try:
        from gpiozero.pins.pigpio import PiGPIOFactory
        factory = PiGPIOFactory()
    except Exception:
        factory = None
except Exception as e:
    print("Error importando gpiozero:", e)
    print("Instala gpiozero (y pigpio si quieres mejor control de servos).")
    raise

# Pines GPIO para el motor L298N
MOTOR_ENB = 13  # Enable B (PWM)
MOTOR_IN3 = 26  # Dirección 1
MOTOR_IN4 = 19  # Dirección 2
SERVO_PIN = 18  # Pin del servo
HALL_SENSOR_PIN = 17  # Pin del sensor Hall KY-003 para RPM
BUTTON_PIN = 3  # Pin del botón START/RESET (GPIO3 - era SDA del magnetómetro)

# -----------------------
# Config
# -----------------------
CAM_INDEX = 0      # Cámara para detección de líneas (abajo centro)
CAM_INDEX_2 = 2    # Cámara para detección de paredes (arriba izquierda)
CAM_INDEX_3 = 4    # Cámara 3 (arriba derecha)
FRAME_W = 640
FRAME_H = 360

# ROI para detección de líneas (Cámara 1)
C_RECT = (int(FRAME_W*0.25), int(FRAME_H*0.65), int(FRAME_W*0.5), int(FRAME_H*0.25))
x_c, y_c, w_c, h_c = C_RECT

# ROI horizontal para detección de paredes en CAM2 - AL LADO DERECHO (pegado al borde)
CAM2_ROI = (FRAME_W - 300, FRAME_H - 170, 300, 80)  # x, y, ancho, alto - derecha

# ROI horizontal para detección de paredes en CAM3 - AL LADO IZQUIERDO (pegado al borde)
CAM3_ROI = (0, FRAME_H - 170, 300, 80)  # izquierda

# ROIs adicionales debajo - más largos
CAM2_ROI_BAJO = (FRAME_W - 400, FRAME_H - 80, 400, 80)  # debajo derecha - mucho más largo
CAM3_ROI_BAJO = (0, FRAME_H - 80, 400, 80)  # debajo izquierda - mucho más largo

# Valores HSV fijos para detección de colores - Configuración predeterminada
# RGB Azul: (0, 51, 255) -> HSV aproximado: H=220, S=255, V=255
# RGB Naranja: (255, 102, 0) -> HSV aproximado: H=24, S=255, V=255
BLUE_LO = np.array([100, 80, 80])    # Filtro menos estricto: S=80, V=80
BLUE_HI = np.array([140, 255, 255])  # Rango H más amplio: 100-140
ORANGE_LO = np.array([0, 80, 80])    # Filtro menos estricto: S=80, V=80
ORANGE_HI = np.array([30, 255, 255]) # Rango H más amplio: 0-30
BLACK_THRESHOLD = 100

STEER_LIMIT = 400
STEER_LIMIT_RIGHT = 320  # Límite reducido hacia la derecha
WALL_GAIN = 10.0  # Reducido para reacción más suave a las paredes
VELOCIDAD_FIJA = 120  # Velocidad moderada (120/255 = ~47% PWM)

# Ajuste: mapear velocidad a 0..1 para gpiozero Motor
MAX_PWM = 255.0

# Configuración del sistema de navegación CON CONTEO POR LÍNEAS DETECTADAS
LINEAS_TOTALES = 12  # Total: 12 líneas detectadas = 3 vueltas (4 líneas por vuelta)
TIEMPO_PAUSA_FINAL = 3.0  # Pausa de 3 segundos después de la última línea

# Configuración del control de RPM con sensor Hall
TARGET_RPM = 50  # RPM objetivo reducido
RPM_TOLERANCE = 10  # Tolerancia ±10 RPM
PULSE_FORWARD_MS = 150  # Duración pulso adelante (ms)
PULSE_BRAKE_MS = 30    # Duración pulso freno (ms)
PULSE_INTERVAL = 0.05  # Intervalo entre pulsos (50ms)
HALL_MAGNETS = 2       # Número de imanes en la rueda

# Configuración de detección de líneas continuas - FILTROS RELAJADOS (90% menos estricto)
LINE_MIN_WIDTH = 8     # Ancho mínimo reducido: 80 -> 8 píxeles (90% menos)
LINE_MIN_PIXELS = 15   # Píxeles mínimos reducidos: 150 -> 15 píxeles (90% menos)

# Frames para resetear última línea detectada
FRAMES_PARA_RESETEAR = 30  # Resetear después de 1 segundo sin líneas (30 frames @ 30fps)

# -----------------------
# Utils
# -----------------------
def mask_color_hsv(bgr, lo, hi):
    """Detección HSV pura SIN filtros morfológicos"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, lo, hi)
    return m

CONFIG_PATH = os.path.expanduser("~/.wro_color_config.json")

def save_color_config(path, blue_lo, blue_hi, orange_lo, orange_hi, cameras_swapped=False, b_range=None, o_range=None, camera_mapping=None):
    """Guarda configuración de colores"""
    data = {
        'blue_lo': [int(x) for x in blue_lo.tolist()],
        'blue_hi': [int(x) for x in blue_hi.tolist()],
        'orange_lo': [int(x) for x in orange_lo.tolist()],
        'orange_hi': [int(x) for x in orange_hi.tolist()],
        'cameras_swapped': cameras_swapped
    }
    if b_range is not None:
        data['b_range'] = int(b_range)
    if o_range is not None:
        data['o_range'] = int(o_range)
    if camera_mapping is not None:
        data['camera_mapping'] = {int(k): int(v) for k, v in camera_mapping.items()}

    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved color config to {path}")
    except Exception as e:
        print("Failed saving color config:", e)

def load_color_config(path, blue_lo, blue_hi, orange_lo, orange_hi):
    """Carga configuración de colores"""
    if not os.path.exists(path):
        return False, False, None, None, None, None, None, None, None
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        blue_lo[:] = np.array(data.get('blue_lo', blue_lo.tolist()))
        blue_hi[:] = np.array(data.get('blue_hi', blue_hi.tolist()))
        orange_lo[:] = np.array(data.get('orange_lo', orange_lo.tolist()))
        orange_hi[:] = np.array(data.get('orange_hi', orange_hi.tolist()))
        cameras_swapped = data.get('cameras_swapped', False)

        b_light_saved = data.get('b_light', None)
        b_mid_saved = data.get('b_mid', None)
        b_dark_saved = data.get('b_dark', None)
        o_light_saved = data.get('o_light', None)
        o_mid_saved = data.get('o_mid', None)
        o_dark_saved = data.get('o_dark', None)

        camera_mapping_saved = data.get('camera_mapping', None)
        if camera_mapping_saved is not None:
            camera_mapping_saved = {int(k): int(v) for k, v in camera_mapping_saved.items()}

        print(f"Loaded color config from {path}")
        return True, cameras_swapped, b_light_saved, b_mid_saved, b_dark_saved, o_light_saved, o_mid_saved, o_dark_saved, camera_mapping_saved
    except Exception as e:
        print("Failed loading color config:", e)
        return False, False, None, None, None, None, None, None, None

class ConsoleInputThread(threading.Thread):
    def __init__(self, blue_lo, blue_hi, orange_lo, orange_hi):
        super().__init__(daemon=True)
        self.blue_lo = blue_lo
        self.blue_hi = blue_hi
        self.orange_lo = orange_lo
        self.orange_hi = orange_hi
        self.running = True

    def run(self):
        print("Console controls: b+/b- o+/o- bh+/bh- bl+/bl- oh+/oh- ol+/ol- save status quit")
        while self.running:
            try:
                cmd = input().strip()
            except Exception:
                break
            if not cmd:
                continue
            if cmd == 'quit':
                print('Quit requested from console')
                os._exit(0)
            elif cmd == 'save':
                save_color_config(CONFIG_PATH, self.blue_lo, self.blue_hi, self.orange_lo, self.orange_hi)
            elif cmd == 'status':
                print('blue_lo', self.blue_lo.tolist(), 'blue_hi', self.blue_hi.tolist())
                print('orange_lo', self.orange_lo.tolist(), 'orange_hi', self.orange_hi.tolist())

    def stop(self):
        self.running = False

def create_color_adjust_window(blue_lo, blue_hi, orange_lo, orange_hi):
    """Crea ventana de ajuste de colores con valores iniciales"""
    cv2.namedWindow("Adjust Colors", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("B_H_lo", "Adjust Colors", int(blue_lo[0]), 179, lambda v: None)
    cv2.createTrackbar("B_S_lo", "Adjust Colors", int(blue_lo[1]), 255, lambda v: None)
    cv2.createTrackbar("B_V_lo", "Adjust Colors", int(blue_lo[2]), 255, lambda v: None)
    cv2.createTrackbar("B_H_hi", "Adjust Colors", int(blue_hi[0]), 179, lambda v: None)
    cv2.createTrackbar("B_S_hi", "Adjust Colors", int(blue_hi[1]), 255, lambda v: None)
    cv2.createTrackbar("B_V_hi", "Adjust Colors", int(blue_hi[2]), 255, lambda v: None)
    cv2.createTrackbar("O_H_lo", "Adjust Colors", int(orange_lo[0]), 179, lambda v: None)
    cv2.createTrackbar("O_S_lo", "Adjust Colors", int(orange_lo[1]), 255, lambda v: None)
    cv2.createTrackbar("O_V_lo", "Adjust Colors", int(orange_lo[2]), 255, lambda v: None)
    cv2.createTrackbar("O_H_hi", "Adjust Colors", int(orange_hi[0]), 179, lambda v: None)
    cv2.createTrackbar("O_S_hi", "Adjust Colors", int(orange_hi[1]), 255, lambda v: None)
    cv2.createTrackbar("O_V_hi", "Adjust Colors", int(orange_hi[2]), 255, lambda v: None)

def mask_black_gray(bgr, thresh=BLACK_THRESHOLD):
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mean_val = np.mean(gray)
    dynamic_thresh = min(thresh, int(mean_val * 0.8))
    _, m = cv2.threshold(gray, dynamic_thresh, 255, cv2.THRESH_BINARY_INV)
    mask_white = cv2.inRange(gray, 200, 255)
    m = cv2.bitwise_and(m, cv2.bitwise_not(mask_white))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, kernel, iterations=1)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, kernel, iterations=1)
    return m

def invasion_ratio(mask):
    area = mask.shape[0] * mask.shape[1]
    if area == 0:
        return 0.0
    inv = cv2.countNonZero(mask) / float(area)
    return inv

# -----------------------
# Capture thread
# -----------------------
class CaptureThread(threading.Thread):
    def __init__(self, index=0, w=FRAME_W, h=FRAME_H):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.lock = threading.Lock()
        self.frame = None
        self.running = True

    def run(self):
        time.sleep(0.2)
        while self.running:
            ret, f = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.frame = f.copy()
        self.cap.release()

    def read(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.running = False

# -----------------------
# Main logic
# -----------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true", help="Mostrar ventanas")
    args = parser.parse_args()

    # Inicializar valores de colores
    blue_lo = BLUE_LO.copy()
    blue_hi = BLUE_HI.copy()
    orange_lo = ORANGE_LO.copy()
    orange_hi = ORANGE_HI.copy()

    # Variable para controlar intercambio de cámaras
    cameras_swapped = False

    # Variables para ajuste de brillo de cámaras
    brightness_cam1 = 0
    brightness_cam2 = 0

    # Variables para el sistema de intercambio de cámaras
    camera_selected = None
    camera_mapping = {1: 0, 2: 1, 3: 2}

    # Cargar configuración guardada
    try:
        loaded, cameras_swapped, b_light_saved, b_mid_saved, b_dark_saved, o_light_saved, o_mid_saved, o_dark_saved, camera_mapping_saved = load_color_config(CONFIG_PATH, blue_lo, blue_hi, orange_lo, orange_hi)
        if loaded:
            print("✓ Configuración de colores cargada desde archivo guardado")
            if camera_mapping_saved is not None:
                camera_mapping = camera_mapping_saved
                print(f"✓ Mapeo de cámaras restaurado: {camera_mapping}")
    except Exception as e:
        print(f"  No se pudo cargar configuración: {e}")

    # Crear ventana de ajuste de rango
    try:
        cv2.namedWindow("Adjust Range", cv2.WINDOW_NORMAL)
        blue_range_default = int((BLUE_HI[0] - BLUE_LO[0]) / 2)
        orange_range_default = int((ORANGE_HI[0] - ORANGE_LO[0]) / 2)

        blue_light = b_light_saved if b_light_saved is not None else blue_range_default
        blue_mid = b_mid_saved if b_mid_saved is not None else blue_range_default
        blue_dark = b_dark_saved if b_dark_saved is not None else blue_range_default
        orange_light = o_light_saved if o_light_saved is not None else orange_range_default
        orange_mid = o_mid_saved if o_mid_saved is not None else orange_range_default
        orange_dark = o_dark_saved if o_dark_saved is not None else orange_range_default

        cv2.createTrackbar("B_light", "Adjust Range", blue_light, 90, lambda v: None)
        cv2.createTrackbar("B_mid", "Adjust Range", blue_mid, 90, lambda v: None)
        cv2.createTrackbar("B_dark", "Adjust Range", blue_dark, 90, lambda v: None)
        cv2.createTrackbar("O_light", "Adjust Range", orange_light, 90, lambda v: None)
        cv2.createTrackbar("O_mid", "Adjust Range", orange_mid, 90, lambda v: None)
        cv2.createTrackbar("O_dark", "Adjust Range", orange_dark, 90, lambda v: None)
        cv2.createTrackbar("B_S_min", "Adjust Range", BLUE_LO[1], 255, lambda v: None)
        cv2.createTrackbar("B_S_max", "Adjust Range", BLUE_HI[1], 255, lambda v: None)
        cv2.createTrackbar("O_S_min", "Adjust Range", ORANGE_LO[1], 255, lambda v: None)
        cv2.createTrackbar("O_S_max", "Adjust Range", ORANGE_HI[1], 255, lambda v: None)

        print("✓ Ventana 'Adjust Range' creada")
    except Exception as e:
        print(f"No se pudo crear ventana de ajuste: {e}")

    # Mostrar valores HSV fijos al inicio
    print("\n" + "="*50)
    print("🎨 VALORES HSV BASE (ajustables por claridad)")
    print("="*50)
    print(f"🔵 BLUE:   H={BLUE_LO[0]}-{BLUE_HI[0]} S={BLUE_LO[1]}-{BLUE_HI[1]} V={BLUE_LO[2]}-{BLUE_HI[2]}")
    print(f"🟠 ORANGE: H={ORANGE_LO[0]}-{ORANGE_HI[0]} S={ORANGE_LO[1]}-{ORANGE_HI[1]} V={ORANGE_LO[2]}-{ORANGE_HI[2]}")
    print("="*50)
    print("✅ Filtros 90% MENOS estrictos - Detección más permisiva")
    print("🎛️  Ajusta rangos en 'Adjust Range'")
    print("="*50)
    print("\n🎮 CONTROLES:")
    print("  ESC: Salir")
    print("  Q/W: Brillo CAM1 (±5)")
    print("  E/R: Brillo CAM2 (±5)")
    print("\n📸 INTERCAMBIO DE CÁMARAS:")
    print("  1/2/3: Primera tecla = selecciona cámara")
    print("  1/2/3: Segunda tecla = intercambia con esa cámara")
    print("  Ejemplo: '1' luego '2' intercambia CAM1 ↔ CAM2")
    print(f"  Mapeo actual: {camera_mapping}")
    print("="*50 + "\n")

    # Inicializar cámaras
    print("\n=== Inicializando cámaras ===")
    cap = CaptureThread(CAM_INDEX, FRAME_W, FRAME_H)
    cap.start()
    print(f"✓ Cámara 1 (líneas): /dev/video{CAM_INDEX}")

    cap2 = CaptureThread(CAM_INDEX_2, FRAME_W, FRAME_H)
    cap2.start()
    print(f"✓ Cámara 2 (pared izq): /dev/video{CAM_INDEX_2}")

    cap3 = CaptureThread(CAM_INDEX_3, FRAME_W, FRAME_H)
    cap3.start()
    print(f"✓ Cámara 3 (pared der): /dev/video{CAM_INDEX_3}")

    time.sleep(0.5)

    input_thread = ConsoleInputThread(blue_lo, blue_hi, orange_lo, orange_hi)
    try:
        input_thread.start()
    except Exception:
        pass

    # --- Inicializar motor y servo en la Raspberry Pi ---
    try:
        class MotorL298N:
            def __init__(self, enable_pin, in1_pin, in2_pin, hall_pin):
                self.enable = DigitalOutputDevice(enable_pin)
                self.in1 = DigitalOutputDevice(in1_pin)
                self.in2 = DigitalOutputDevice(in2_pin)

                self.hall_sensor = Button(hall_pin, pull_up=True, bounce_time=0.01)
                self.pulse_count = 0
                self.last_rpm_time = time.time()
                self.current_rpm = 0

                self.target_rpm = TARGET_RPM
                self.last_pulse_time = time.time()
                self.is_running = False

                self.hall_sensor.when_pressed = self._on_hall_pulse
                self.enable.on()
                print(f"  ⚡ Motor con control de RPM inicializado")

            def _on_hall_pulse(self):
                self.pulse_count += 1

            def calculate_rpm(self):
                current_time = time.time()
                elapsed = current_time - self.last_rpm_time

                if elapsed >= 0.5:
                    rpm = (self.pulse_count / HALL_MAGNETS) / (elapsed / 60.0)
                    self.current_rpm = rpm
                    self.pulse_count = 0
                    self.last_rpm_time = current_time

                return self.current_rpm

            def pulse_forward(self, duration_ms):
                self.in1.on()
                self.in2.off()
                time.sleep(duration_ms / 1000.0)
                self.in1.off()
                self.in2.off()

            def control_speed(self):
                if not self.is_running:
                    return

                current_rpm = self.calculate_rpm()
                error = self.target_rpm - current_rpm

                current_time = time.time()

                if current_time - self.last_pulse_time < PULSE_INTERVAL:
                    return

                if error > RPM_TOLERANCE:
                    self.pulse_forward(PULSE_FORWARD_MS)
                    self.last_pulse_time = current_time
                elif error < -RPM_TOLERANCE:
                    time.sleep(PULSE_INTERVAL * 2)
                    self.last_pulse_time = current_time
                else:
                    self.pulse_forward(PULSE_FORWARD_MS // 2)
                    self.last_pulse_time = current_time

            def forward(self, speed=1.0):
                self.enable.on()
                self.is_running = True
                self.control_speed()

            def backward(self, speed=1.0):
                self.enable.on()
                self.is_running = False
                self.in1.off()
                self.in2.on()

            def stop(self):
                self.is_running = False
                self.in1.on()
                self.in2.on()
                time.sleep(0.05)
                self.in1.off()
                self.in2.off()

            def close(self):
                self.stop()
                self.enable.off()
                self.enable.close()
                self.in1.close()
                self.in2.close()

        motor = MotorL298N(MOTOR_ENB, MOTOR_IN3, MOTOR_IN4, HALL_SENSOR_PIN)

        if factory is not None:
            servo = Servo(SERVO_PIN, pin_factory=factory)
        else:
            servo = Servo(SERVO_PIN)

        print("GPIO motor y servo inicializados.")
    except Exception as e:
        print("Error inicializando motor/servo:", e)
        motor = None
        servo = None

    # ==================================================
    # CONFIGURAR BOTÓN START/RESET (SIN RESISTENCIA PULL-UP/DOWN)
    # ==================================================
    robot_activo = False  # Estado del robot: False = detenido, True = activo
    
    def on_button_pressed():
        nonlocal robot_activo, contador_lineas, estado_giro, linea_inicial
        nonlocal tiempo_ultima_linea, en_pausa_final, ultima_linea_procesada, frames_sin_linea
        
        if not robot_activo:
            # INICIAR EL ROBOT
            robot_activo = True
            print("\n" + "="*60)
            print("🟢 BOTÓN PRESIONADO - ROBOT INICIADO")
            print("="*60 + "\n")
        else:
            # REINICIAR EL ROBOT (resetear todo)
            robot_activo = False
            contador_lineas = 0
            estado_giro = None
            linea_inicial = None
            tiempo_ultima_linea = None
            en_pausa_final = False
            ultima_linea_procesada = None
            frames_sin_linea = 0
            
            # Detener motor y servo
            if motor is not None:
                motor.stop()
            if servo is not None:
                servo.value = 0
            
            print("\n" + "="*60)
            print("🔴 BOTÓN PRESIONADO - ROBOT REINICIADO")
            print("   Presiona el botón nuevamente para iniciar")
            print("="*60 + "\n")
    
    try:
        # Configurar botón SIN resistencia pull-up/down (flotante)
        # El pin estará en estado alto (3.3V) normalmente
        start_button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)
        start_button.when_pressed = on_button_pressed
        print(f"\n✅ Botón START/RESET configurado en GPIO{BUTTON_PIN}")
        print("   Sin resistencia - usando pull-up interno")
        print("   Conectar botón entre GPIO3 y GND\n")
    except Exception as e:
        print(f"⚠️  Error configurando botón: {e}")
        print("   El robot iniciará automáticamente sin botón\n")
        robot_activo = True  # Iniciar automáticamente si no hay botón
        start_button = None

    print("Iniciando loop. Presionar ESC para salir.")
    print("\n=== CONTROLES ===")
    print("🔘 BOTÓN START/RESET:")
    print("   - Primera presión: INICIA el robot")
    print("   - Segunda presión: REINICIA todo (vuelve al estado inicial)")
    print("\nAjuste de brillo:")
    print("  CAM1 (líneas): 'q' - / 'w' +")
    print("  CAM2 (paredes): 'e' - / 'r' +")

    # ==================================================
    # SISTEMA DE CONTEO DE LÍNEAS (SIN MAGNETÓMETRO)
    # ==================================================
    print("\n🔢 SISTEMA DE CONTEO DE LÍNEAS ACTIVO")
    print(f"   Meta: {LINEAS_TOTALES} líneas = 3 vueltas")
    print(f"   Pausa final: {TIEMPO_PAUSA_FINAL} segundos")
    print("\n⏸️  ROBOT DETENIDO - Presiona el botón para iniciar\n")

    estado_giro = None
    linea_inicial = None

    # ===== SISTEMA DE CONTEO DE LÍNEAS DETECTADAS =====
    contador_lineas = 0  # Contador de LÍNEAS detectadas
    tiempo_ultima_linea = None  # Timestamp de la última línea detectada
    en_pausa_final = False  # Flag para indicar que está en pausa de 3 segundos

    try:
        frame_count = 0
        ultimo_color_detectado = None
        ultima_linea_procesada = None
        frames_sin_linea = 0

        while True:
            frame_count += 1

            # ==================================================
            # VERIFICAR SI EL ROBOT ESTÁ ACTIVO
            # ==================================================
            if not robot_activo:
                # Robot detenido - solo mostrar video sin procesar
                frames_raw = [cap.read(), cap2.read(), cap3.read()]
                
                if any(f is None for f in frames_raw):
                    time.sleep(0.01)
                    continue
                
                # Aplicar mapeo de cámaras
                frame_cam1 = frames_raw[camera_mapping[1]].copy()
                frame_cam2 = frames_raw[camera_mapping[2]].copy()
                frame_cam3 = frames_raw[camera_mapping[3]].copy()
                
                try:
                    frame_cam1 = cv2.rotate(frame_cam1, cv2.ROTATE_180)
                    frame_cam2 = cv2.rotate(frame_cam2, cv2.ROTATE_180)
                except Exception:
                    pass
                
                disp = frame_cam1.copy()
                disp2 = frame_cam2.copy()
                disp3 = frame_cam3.copy()
                
                # Mostrar mensaje de ROBOT DETENIDO
                center_x = FRAME_W // 2
                center_y = FRAME_H // 2
                
                overlay = disp.copy()
                cv2.rectangle(overlay, (center_x - 250, center_y - 80),
                             (center_x + 250, center_y + 80), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.8, disp, 0.2, 0, disp)
                
                cv2.rectangle(disp, (center_x - 250, center_y - 80),
                             (center_x + 250, center_y + 80), (0, 0, 255), 3)
                
                cv2.putText(disp, "ROBOT DETENIDO",
                           (center_x - 180, center_y - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
                cv2.putText(disp, "Presiona el boton para iniciar",
                           (center_x - 220, center_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(disp, "o presiona ESC para salir",
                           (center_x - 180, center_y + 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
                
                # Combinar las 3 cámaras
                top_row = np.hstack([cv2.resize(disp2, (320, 180)), cv2.resize(disp3, (320, 180))])
                bottom_row = cv2.resize(disp, (640, 180))
                combined_frame = np.vstack([top_row, bottom_row])
                cv2.imshow("frame", combined_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                
                continue  # Saltar todo el procesamiento

            # ==================================================
            # ROBOT ACTIVO - PROCESAMIENTO NORMAL
            # ==================================================

            # Verificar si está en pausa final
            if en_pausa_final:
                tiempo_actual = time.time()
                tiempo_transcurrido = tiempo_actual - tiempo_ultima_linea
                
                if tiempo_transcurrido >= TIEMPO_PAUSA_FINAL:
                    print(f"\n{'🏁'*30}")
                    print(f"🏁 ¡PAUSA DE {TIEMPO_PAUSA_FINAL} SEGUNDOS COMPLETADA!")
                    print(f"🏁 DETENIENDO ROBOT")
                    print(f"{'🏁'*30}\n")
                    if motor is not None:
                        motor.stop()
                    if servo is not None:
                        servo.value = 0
                    break
                else:
                    tiempo_restante = TIEMPO_PAUSA_FINAL - tiempo_transcurrido
                    if frame_count % 10 == 0:
                        print(f"⏸️  Pausado - Tiempo restante: {tiempo_restante:.1f}s")
                    time.sleep(0.1)
                    continue

            # Leer frames de las 3 cámaras físicas
            frames_raw = [cap.read(), cap2.read(), cap3.read()]

            if any(f is None for f in frames_raw):
                time.sleep(0.01)
                continue

            # Aplicar mapeo de cámaras
            frame_cam1 = frames_raw[camera_mapping[1]].copy()
            frame_cam2 = frames_raw[camera_mapping[2]].copy()
            frame_cam3 = frames_raw[camera_mapping[3]].copy()

            try:
                frame_cam1 = cv2.rotate(frame_cam1, cv2.ROTATE_180)
                frame_cam2 = cv2.rotate(frame_cam2, cv2.ROTATE_180)
            except Exception:
                pass

            # Aplicar ajuste de brillo
            if brightness_cam1 != 0:
                frame_cam1 = cv2.convertScaleAbs(frame_cam1, alpha=1.0, beta=brightness_cam1)
            if brightness_cam2 != 0:
                frame_cam2 = cv2.convertScaleAbs(frame_cam2, alpha=1.0, beta=brightness_cam2)

            frame = frame_cam1.copy()
            frame2 = frame_cam2.copy()
            frame3 = frame_cam3.copy()

            disp = frame.copy()
            disp2 = frame2.copy()
            disp3 = frame3.copy()

            # Extraer ROI de líneas
            roi_c = frame[y_c:y_c+h_c, x_c:x_c+w_c]

            # Leer rangos de la ventana de ajuste
            try:
                b_light = cv2.getTrackbarPos("B_light", "Adjust Range")
                b_mid = cv2.getTrackbarPos("B_mid", "Adjust Range")
                b_dark = cv2.getTrackbarPos("B_dark", "Adjust Range")
                o_light = cv2.getTrackbarPos("O_light", "Adjust Range")
                o_mid = cv2.getTrackbarPos("O_mid", "Adjust Range")
                o_dark = cv2.getTrackbarPos("O_dark", "Adjust Range")

                b_s_min = cv2.getTrackbarPos("B_S_min", "Adjust Range")
                b_s_max = cv2.getTrackbarPos("B_S_max", "Adjust Range")
                o_s_min = cv2.getTrackbarPos("O_S_min", "Adjust Range")
                o_s_max = cv2.getTrackbarPos("O_S_max", "Adjust Range")

                blue_center_h = int((BLUE_LO[0] + BLUE_HI[0]) / 2)
                orange_center_h = int((ORANGE_LO[0] + ORANGE_HI[0]) / 2)

                # Crear máscaras para AZUL claro, medio y oscuro
                masks_blue = []

                if b_light > 0:
                    blue_lo_light = np.array([max(0, blue_center_h - b_light), b_s_min, 180])
                    blue_hi_light = np.array([min(179, blue_center_h + b_light), b_s_max, 255])
                    masks_blue.append(mask_color_hsv(roi_c, blue_lo_light, blue_hi_light))

                if b_mid > 0:
                    blue_lo_mid = np.array([max(0, blue_center_h - b_mid), b_s_min, 100])
                    blue_hi_mid = np.array([min(179, blue_center_h + b_mid), b_s_max, 179])
                    masks_blue.append(mask_color_hsv(roi_c, blue_lo_mid, blue_hi_mid))

                if b_dark > 0:
                    blue_lo_dark = np.array([max(0, blue_center_h - b_dark), b_s_min, BLUE_LO[2]])
                    blue_hi_dark = np.array([min(179, blue_center_h + b_dark), b_s_max, 99])
                    masks_blue.append(mask_color_hsv(roi_c, blue_lo_dark, blue_hi_dark))

                if masks_blue:
                    roi_mask_blue = masks_blue[0]
                    for m in masks_blue[1:]:
                        roi_mask_blue = cv2.bitwise_or(roi_mask_blue, m)
                else:
                    roi_mask_blue = mask_color_hsv(roi_c, BLUE_LO, BLUE_HI)

                # Crear máscaras para NARANJA claro, medio y oscuro
                masks_orange = []

                if o_light > 0:
                    orange_lo_light = np.array([max(0, orange_center_h - o_light), o_s_min, 200])
                    orange_hi_light = np.array([min(179, orange_center_h + o_light), o_s_max, 255])
                    masks_orange.append(mask_color_hsv(roi_c, orange_lo_light, orange_hi_light))

                if o_mid > 0:
                    orange_lo_mid = np.array([max(0, orange_center_h - o_mid), o_s_min, 150])
                    orange_hi_mid = np.array([min(179, orange_center_h + o_mid), o_s_max, 199])
                    masks_orange.append(mask_color_hsv(roi_c, orange_lo_mid, orange_hi_mid))

                if o_dark > 0:
                    orange_lo_dark = np.array([max(0, orange_center_h - o_dark), o_s_min, ORANGE_LO[2]])
                    orange_hi_dark = np.array([min(179, orange_center_h + o_dark), o_s_max, 149])
                    masks_orange.append(mask_color_hsv(roi_c, orange_lo_dark, orange_hi_dark))

                if masks_orange:
                    roi_mask_orange = masks_orange[0]
                    for m in masks_orange[1:]:
                        roi_mask_orange = cv2.bitwise_or(roi_mask_orange, m)
                else:
                    roi_mask_orange = mask_color_hsv(roi_c, ORANGE_LO, ORANGE_HI)

            except Exception as e:
                print(f"Error en trackbars: {e}")
                roi_mask_blue = mask_color_hsv(roi_c, BLUE_LO, BLUE_HI)
                roi_mask_orange = mask_color_hsv(roi_c, ORANGE_LO, ORANGE_HI)

            # ROI horizontal en frame2 y frame3
            roi_cam2 = frame2[CAM2_ROI[1]:CAM2_ROI[1]+CAM2_ROI[3],
                             CAM2_ROI[0]:CAM2_ROI[0]+CAM2_ROI[2]]
            roi_cam3 = frame3[CAM3_ROI[1]:CAM3_ROI[1]+CAM3_ROI[3],
                             CAM3_ROI[0]:CAM3_ROI[0]+CAM3_ROI[2]]

            roi_cam2_bajo = frame2[CAM2_ROI_BAJO[1]:CAM2_ROI_BAJO[1]+CAM2_ROI_BAJO[3],
                                   CAM2_ROI_BAJO[0]:CAM2_ROI_BAJO[0]+CAM2_ROI_BAJO[2]]
            roi_cam3_bajo = frame3[CAM3_ROI_BAJO[1]:CAM3_ROI_BAJO[1]+CAM3_ROI_BAJO[3],
                                   CAM3_ROI_BAJO[0]:CAM3_ROI_BAJO[0]+CAM3_ROI_BAJO[2]]

            # Máscaras de paredes
            mask_wall_cam2 = mask_black_gray(roi_cam2)
            mask_wall_cam3 = mask_black_gray(roi_cam3)
            mask_wall_cam2_bajo = mask_black_gray(roi_cam2_bajo)
            mask_wall_cam3_bajo = mask_black_gray(roi_cam3_bajo)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask_edges = cv2.Canny(gray, 50, 150)
            mask_edges = cv2.dilate(mask_edges, cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)), iterations=1)

            # Detección por color
            blue_pixels = cv2.countNonZero(roi_mask_blue)
            orange_pixels = cv2.countNonZero(roi_mask_orange)
            hay_azul = blue_pixels > 0
            hay_naranja = orange_pixels > 0

            # Invasión de paredes
            inv_cam2 = invasion_ratio(mask_wall_cam2)
            inv_cam3 = invasion_ratio(mask_wall_cam3)
            inv_cam2_bajo = invasion_ratio(mask_wall_cam2_bajo)
            inv_cam3_bajo = invasion_ratio(mask_wall_cam3_bajo)

            inv_cam2_total = max(inv_cam2, inv_cam2_bajo)
            inv_cam3_total = max(inv_cam3, inv_cam3_bajo)

            wall_steer = int(WALL_GAIN * 100 * (inv_cam2_total - inv_cam3_total))

            steer = 0
            velocidad = VELOCIDAD_FIJA
            linea_detectada = 0

            # Verificar si ya completó las 12 líneas
            if contador_lineas >= LINEAS_TOTALES and not en_pausa_final:
                en_pausa_final = True
                tiempo_ultima_linea = time.time()
                print(f"\n{'🏁'*30}")
                print(f"🏁 ¡{LINEAS_TOTALES} LÍNEAS COMPLETADAS!")
                print(f"⏸️  INICIANDO PAUSA DE {TIEMPO_PAUSA_FINAL} SEGUNDOS")
                print(f"{'🏁'*30}\n")
                continue

            # Contar frames sin detección para resetear la memoria
            if not hay_azul and not hay_naranja:
                frames_sin_linea += 1
                if frames_sin_linea >= FRAMES_PARA_RESETEAR:
                    ultima_linea_procesada = None
                    frames_sin_linea = 0
            else:
                frames_sin_linea = 0

            # Iniciar giro cuando detecta solo UNA línea
            if estado_giro is None:
                if hay_azul and not hay_naranja:
                    if ultima_linea_procesada != "AZUL":
                        estado_giro = "IZQUIERDA"
                        linea_inicial = "AZUL"
                        ultima_linea_procesada = "AZUL"
                        contador_lineas += 1
                        print(f"\n{'='*60}")
                        print(f"🔵 LÍNEA {contador_lineas}/{LINEAS_TOTALES} DETECTADA (AZUL)")
                        print(f"{'='*60}\n")
                        print("🔵 Iniciando giro IZQUIERDA")

                elif hay_naranja and not hay_azul:
                    if ultima_linea_procesada != "NARANJA":
                        estado_giro = "DERECHA"
                        linea_inicial = "NARANJA"
                        ultima_linea_procesada = "NARANJA"
                        contador_lineas += 1
                        print(f"\n{'='*60}")
                        print(f"🟠 LÍNEA {contador_lineas}/{LINEAS_TOTALES} DETECTADA (NARANJA)")
                        print(f"{'='*60}\n")
                        print("🟠 Iniciando giro DERECHA")

            elif estado_giro == "IZQUIERDA":
                if hay_naranja:
                    estado_giro = "GIRANDO_IZQUIERDA"
                    print("🔵→🟠 Segunda línea detectada, continuando giro...")

            elif estado_giro == "DERECHA":
                if hay_azul:
                    estado_giro = "GIRANDO_DERECHA"
                    print("🟠→🔵 Segunda línea detectada, continuando giro...")

            elif estado_giro == "GIRANDO_IZQUIERDA":
                if not hay_naranja:
                    estado_giro = None
                    linea_inicial = None
                    print("✅ Giro IZQUIERDA completado")

            elif estado_giro == "GIRANDO_DERECHA":
                if not hay_azul:
                    estado_giro = None
                    linea_inicial = None
                    print("✅ Giro DERECHA completado")

            # Aplicar dirección del giro
            if estado_giro in ["IZQUIERDA", "GIRANDO_IZQUIERDA"]:
                steer = -STEER_LIMIT
                linea_detectada = 1
            elif estado_giro in ["DERECHA", "GIRANDO_DERECHA"]:
                steer = STEER_LIMIT_RIGHT
                linea_detectada = 1
            else:
                if inv_cam2_total > 0.03 or inv_cam3_total > 0.03:
                    steer = wall_steer
                else:
                    steer = 0

            steer = int(np.clip(steer, -STEER_LIMIT, STEER_LIMIT_RIGHT))

            # Control GPIO: servo y motor
            steer_norm = int(np.clip(steer / STEER_LIMIT * 100, -100, 100))
            if servo is not None:
                try:
                    servo_pos = np.clip(steer_norm / 100.0, -1.0, 1.0)
                    servo.value = float(servo_pos)
                except Exception as e:
                    print("Error controlando servo:", e)

            if motor is not None:
                try:
                    speed = float(np.clip(velocidad / MAX_PWM, 0.0, 1.0))
                    if speed > 0.01:
                        motor.forward(speed)
                    else:
                        motor.stop()
                except Exception as e:
                    print("Error controlando motor:", e)

            # --- Visualización - TODAS LAS VENTANAS ---
            # Máscaras de colores (cámara de líneas - solo ROI)
            cv2.imshow("mask_blue", cv2.resize(roi_mask_blue, (320,180)))
            cv2.imshow("mask_orange", cv2.resize(roi_mask_orange, (320,180)))
            cv2.imshow("mask_edges", cv2.resize(mask_edges, (320,180)))

            # Máscaras de paredes horizontales (cámara de paredes)
            mask_wall_h_combined = cv2.bitwise_or(mask_wall_cam2, mask_wall_cam3)
            cv2.imshow("mask_wall_horizontal", cv2.resize(mask_wall_h_combined, (320,180)))

            # Máscaras de ROIs bajos
            mask_wall_bajo_combined = cv2.bitwise_or(mask_wall_cam2_bajo, mask_wall_cam3_bajo)
            cv2.imshow("mask_wall_bajo", cv2.resize(mask_wall_bajo_combined, (320,180)))

            # ROIs individuales
            cv2.imshow("roi_c", cv2.resize(roi_c, (320,180)))
            cv2.imshow("roi_cam2", cv2.resize(roi_cam2, (200,100)))
            cv2.imshow("roi_cam3", cv2.resize(roi_cam3, (200,100)))
            cv2.imshow("roi_cam2_bajo", cv2.resize(roi_cam2_bajo, (200,100)))
            cv2.imshow("roi_cam3_bajo", cv2.resize(roi_cam3_bajo, (200,100)))

            # Actualizar el color del contorno según detección
            if hay_azul and hay_naranja:
                roi_color = (0, 255, 255)
                ultimo_color_detectado = "AMBOS"
            elif hay_azul:
                roi_color = (255, 0, 0)
                ultimo_color_detectado = "AZUL"
            elif hay_naranja:
                roi_color = (0, 165, 255)
                ultimo_color_detectado = "NARANJA"
            else:
                if ultimo_color_detectado == "AZUL":
                    roi_color = (255, 0, 0)
                elif ultimo_color_detectado == "NARANJA":
                    roi_color = (0, 165, 255)
                else:
                    roi_color = (128, 128, 128)

            # Frame 1 (líneas - abajo centro) - con ROI marcado con el color detectado
            cv2.rectangle(disp, (x_c, y_c), (x_c+w_c, y_c+h_c), roi_color, 4)
            
            # Mostrar si está seleccionada
            cam_label = "CAM1: Lineas [SELECCIONADA]" if camera_selected == 1 else "CAM1: Lineas"
            color_cam1 = (0, 255, 255) if camera_selected == 1 else (0, 255, 0)
            cv2.putText(disp, cam_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_cam1, 2)
            if brightness_cam1 != 0:
                cv2.putText(disp, f"Brillo: {brightness_cam1:+d}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

            # Mostrar estado de detección
            detection_text = []
            if hay_azul:
                detection_text.append("AZUL")
            if hay_naranja:
                detection_text.append("NARANJA")

            if detection_text:
                cv2.putText(disp, f"Detectado: {' + '.join(detection_text)}",
                           (10, FRAME_H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(disp, f"Ultimo: {ultimo_color_detectado if ultimo_color_detectado else 'NINGUNO'}",
                           (10, FRAME_H - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

            # Mostrar info del contador de líneas en el centro
            center_x = FRAME_W // 2
            center_y = FRAME_H // 2
            box_width = 400
            box_height = 150

            overlay = disp.copy()
            cv2.rectangle(overlay,
                         (center_x - box_width//2, center_y - box_height//2),
                         (center_x + box_width//2, center_y + box_height//2),
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, disp, 0.3, 0, disp)

            cv2.rectangle(disp,
                         (center_x - box_width//2, center_y - box_height//2),
                         (center_x + box_width//2, center_y + box_height//2),
                         (0, 255, 255), 3)

            cv2.putText(disp, "CONTADOR DE LINEAS",
                       (center_x - 150, center_y - 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.putText(disp, f"Lineas: {contador_lineas}/{LINEAS_TOTALES}",
                       (center_x - 120, center_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

            status_text = "EN PROGRESO" if contador_lineas < LINEAS_TOTALES else "COMPLETADO"
            status_color = (0, 165, 255) if contador_lineas < LINEAS_TOTALES else (0, 255, 0)
            cv2.putText(disp, f"Estado: {status_text}",
                       (center_x - 100, center_y + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

            # Frame 2 (pared der - arriba izq) - con ROI horizontal marcado en magenta
            cv2.rectangle(disp2, (CAM2_ROI[0], CAM2_ROI[1]),
                         (CAM2_ROI[0]+CAM2_ROI[2], CAM2_ROI[1]+CAM2_ROI[3]), (255,0,255), 3)
            # ROI bajo en cyan
            cv2.rectangle(disp2, (CAM2_ROI_BAJO[0], CAM2_ROI_BAJO[1]),
                         (CAM2_ROI_BAJO[0]+CAM2_ROI_BAJO[2], CAM2_ROI_BAJO[1]+CAM2_ROI_BAJO[3]), (255,255,0), 3)
            # Mostrar si está seleccionada
            cam_label = "CAM2: Pared Der [SELECCIONADA]" if camera_selected == 2 else "CAM2: Pared Der"
            color_cam2 = (0, 255, 255) if camera_selected == 2 else (0, 255, 255)
            cv2.putText(disp2, cam_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_cam2, 2)
            if brightness_cam2 != 0:
                cv2.putText(disp2, f"Brillo: {brightness_cam2:+d}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            # Mostrar porcentaje de invasión en el centro
            cv2.putText(disp2, f"Inv: {inv_cam2*100:.1f}% / {inv_cam2_bajo*100:.1f}%",
                       (FRAME_W//2 - 120, FRAME_H//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
            cv2.putText(disp2, f"Total: {inv_cam2_total*100:.1f}%",
                       (FRAME_W//2 - 80, FRAME_H//2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Frame 3 (pared izq - arriba der) - con ROI horizontal marcado en magenta
            cv2.rectangle(disp3, (CAM3_ROI[0], CAM3_ROI[1]),
                         (CAM3_ROI[0]+CAM3_ROI[2], CAM3_ROI[1]+CAM3_ROI[3]), (255,0,255), 3)
            # ROI bajo en cyan
            cv2.rectangle(disp3, (CAM3_ROI_BAJO[0], CAM3_ROI_BAJO[1]),
                         (CAM3_ROI_BAJO[0]+CAM3_ROI_BAJO[2], CAM3_ROI_BAJO[1]+CAM3_ROI_BAJO[3]), (255,255,0), 3)
            # Mostrar si está seleccionada
            cam_label = "CAM3: Pared Izq [SELECCIONADA]" if camera_selected == 3 else "CAM3: Pared Izq"
            color_cam3 = (0, 255, 255) if camera_selected == 3 else (255, 165, 0)
            cv2.putText(disp3, cam_label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_cam3, 2)
            # Mostrar porcentaje de invasión en el centro
            cv2.putText(disp3, f"Inv: {inv_cam3*100:.1f}% / {inv_cam3_bajo*100:.1f}%",
                       (FRAME_W//2 - 120, FRAME_H//2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
            cv2.putText(disp3, f"Total: {inv_cam3_total*100:.1f}%",
                       (FRAME_W//2 - 80, FRAME_H//2 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Combinar las 3 cámaras
            top_row = np.hstack([
                cv2.resize(disp2, (320, 180)),
                cv2.resize(disp3, (320, 180))
            ])
            bottom_row = cv2.resize(disp, (640, 180))

            combined_frame = np.vstack([top_row, bottom_row])
            cv2.imshow("frame", combined_frame)

            # Detectar teclas
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

            elif key == ord('q') or key == ord('Q'):
                brightness_cam1 = max(-100, brightness_cam1 - 5)
                print(f"📷 CAM1 Brillo: {brightness_cam1:+d}")
            elif key == ord('w') or key == ord('W'):
                brightness_cam1 = min(100, brightness_cam1 + 5)
                print(f"📷 CAM1 Brillo: {brightness_cam1:+d}")

            elif key == ord('e') or key == ord('E'):
                brightness_cam2 = max(-100, brightness_cam2 - 5)
                print(f"📹 CAM2 Brillo: {brightness_cam2:+d}")
            elif key == ord('r') or key == ord('R'):
                brightness_cam2 = min(100, brightness_cam2 + 5)
                print(f"📹 CAM2 Brillo: {brightness_cam2:+d}")

            # Sistema de intercambio de cámaras - Selecciona primera cámara
            elif key == ord('1'):
                if camera_selected is None:
                    camera_selected = 1
                    print(f"🎯 CAM1 seleccionada - Presiona 2 o 3 para intercambiar")
                else:
                    # Intercambiar camera_selected con CAM1
                    temp = camera_mapping[camera_selected]
                    camera_mapping[camera_selected] = camera_mapping[1]
                    camera_mapping[1] = temp
                    print(f"🔄 Intercambiado: CAM{camera_selected} ↔ CAM1")
                    print(f"📸 Mapeo actual: {camera_mapping}")
                    camera_selected = None
                    
            elif key == ord('2'):
                if camera_selected is None:
                    camera_selected = 2
                    print(f"🎯 CAM2 seleccionada - Presiona 1 o 3 para intercambiar")
                else:
                    # Intercambiar camera_selected con CAM2
                    temp = camera_mapping[camera_selected]
                    camera_mapping[camera_selected] = camera_mapping[2]
                    camera_mapping[2] = temp
                    print(f"🔄 Intercambiado: CAM{camera_selected} ↔ CAM2")
                    print(f"📸 Mapeo actual: {camera_mapping}")
                    camera_selected = None
                    
            elif key == ord('3'):
                if camera_selected is None:
                    camera_selected = 3
                    print(f"🎯 CAM3 seleccionada - Presiona 1 o 2 para intercambiar")
                else:
                    # Intercambiar camera_selected con CAM3
                    temp = camera_mapping[camera_selected]
                    camera_mapping[camera_selected] = camera_mapping[3]
                    camera_mapping[3] = temp
                    print(f"🔄 Intercambiado: CAM{camera_selected} ↔ CAM3")
                    print(f"📸 Mapeo actual: {camera_mapping}")
                    camera_selected = None

    finally:
        try:
            input_thread.stop()
        except Exception:
            pass

        # Guardar configuración
        try:
            current_b_light = cv2.getTrackbarPos("B_light", "Adjust Range")
            current_b_mid = cv2.getTrackbarPos("B_mid", "Adjust Range")
            current_b_dark = cv2.getTrackbarPos("B_dark", "Adjust Range")
            current_o_light = cv2.getTrackbarPos("O_light", "Adjust Range")
            current_o_mid = cv2.getTrackbarPos("O_mid", "Adjust Range")
            current_o_dark = cv2.getTrackbarPos("O_dark", "Adjust Range")

            config_data = {
                "blue_lo": BLUE_LO.tolist(),
                "blue_hi": BLUE_HI.tolist(),
                "orange_lo": ORANGE_LO.tolist(),
                "orange_hi": ORANGE_HI.tolist(),
                "cameras_swapped": cameras_swapped,
                "b_light": current_b_light,
                "b_mid": current_b_mid,
                "b_dark": current_b_dark,
                "o_light": current_o_light,
                "o_mid": current_o_mid,
                "o_dark": current_o_dark,
                "camera_mapping": camera_mapping
            }
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config_data, f, indent=2)
            print("✓ Configuración guardada exitosamente")
        except Exception as e:
            print(f"Error al guardar configuración: {e}")

        # Detener cámaras
        cap.stop()
        cap2.stop()
        cap3.stop()
        print("✓ 3 Cámaras detenidas")

        cv2.destroyAllWindows()

        # Detener y cerrar motor/servo
        try:
            if motor is not None:
                motor.stop()
                motor.close()
        except Exception:
            pass
        try:
            if servo is not None:
                servo.close()
        except Exception:
            pass
        
        # Cerrar botón
        try:
            if start_button is not None:
                start_button.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
