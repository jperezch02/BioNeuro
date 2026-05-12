import pandas as pd
import numpy as np
import os
from scipy.signal import butter, filtfilt
import tkinter as tk
from tkinter import filedialog

# --- CONFIGURACIÓN DEL FILTRO ---
fs = 1000.0
lowcut = 20.0
highcut = 450.0

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def aplicar_procesamiento(data, lowcut, highcut, fs):
    # 1. Filtrado (Bloque 2)
    b, a = butter_bandpass(lowcut, highcut, fs, order=4)
    filtrada = filtfilt(b, a, data)
    
    # 2. Rectificación de Onda Completa (Bloque 3)
    # Aplicamos el valor absoluto para que todo sea positivo antes de integrar
    rectificada = np.abs(filtrada)
    return rectificada

# --- INTERFAZ DE SELECCIÓN ---
root = tk.Tk()
root.withdraw() # Ocultar la ventana principal de tkinter

print("Selecciona el archivo del paciente que deseas procesar...")
ruta_archivo = filedialog.askopenfilename(
    initialdir="datos_crudos",
    title="Seleccionar señal sEMG cruda",
    filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
)

if ruta_archivo:
    # 1. Cargar datos
    df = pd.read_csv(ruta_archivo)
    nombre_base = os.path.basename(ruta_archivo)
    
    # 2. Procesar canales (Filtro + Rectificación)
    sano_proc = aplicar_procesamiento(df['sano_v'], lowcut, highcut, fs)
    afectado_proc = aplicar_procesamiento(df['afectado_v'], lowcut, highcut, fs)
    
    # 3. Guardar resultados
    if not os.path.exists('datos_procesados'):
        os.makedirs('datos_procesados')
        
    df_final = pd.DataFrame({
        'tiempo_s': df['tiempo_s'],
        'sano_rect_v': sano_proc,
        'afectado_rect_v': afectado_proc
    })
    
    ruta_salida = f"datos_procesados/PROC_{nombre_base}"
    df_final.to_csv(ruta_salida, index=False)
    print(f"Éxito: Archivo procesado y guardado en {ruta_salida}")
else:
    print("No se seleccionó ningún archivo.")
