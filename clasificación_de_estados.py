import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# --- CONFIGURACIÓN DE ARCHIVOS ---
TABLA_MAESTRA_PATH = 'datos_enog.csv'
RESULTADOS_TOTALES_PATH = 'reporte_diagnosticos_finales.csv'

# --- 1. CARGA DE TABLA MAESTRA (ENoG) ---
try:
    tabla_maestra = pd.read_csv(TABLA_MAESTRA_PATH)
except FileNotFoundError:
    print(f"Error: No se encuentra {TABLA_MAESTRA_PATH}. Asegúrate de que el archivo existe.")
    exit()

# --- 2. SELECCIÓN DEL PACIENTE ---
root = tk.Tk()
root.withdraw()
print("Seleccionando archivo para diagnóstico...")
ruta_archivo = filedialog.askopenfilename(initialdir="datos_procesados", title="Seleccionar señal RECTIFICADA")

if ruta_archivo:
    df_señal = pd.read_csv(ruta_archivo)
    id_paciente = os.path.basename(ruta_archivo).replace('PROC_', '').replace('.csv', '')
    
    # --- 3. CÁLCULO DE iEMG' (Bloque 4) ---
    fs, dt = 1000, 1/1000
    iemg_sano = df_señal['sano_rect_v'].sum() * dt
    iemg_afectado = df_señal['afectado_rect_v'].sum() * dt
    iemg_prime = (iemg_afectado / iemg_sano) * 100

    # --- 4. CRUCE CON ENoG Y DIAGNÓSTICO (Bloque 5) ---
    datos_paciente = tabla_maestra[tabla_maestra['paciente'] == id_paciente]
    
    if not datos_paciente.empty:
        val_enog = datos_paciente['enog'].values[0]
        
        # Lógica de decisión de Baba et al.
        if iemg_prime <= 25 and val_enog < 10:
            resultado_binario = "Incompleto"
            diagnostico = "PRONÓSTICO: RECUPERACIÓN INCOMPLETA"
        else:
            resultado_binario = "Completo"
            diagnostico = "PRONÓSTICO: RECUPERACIÓN COMPLETA"

        # --- 5. ALMACENAMIENTO PERSISTENTE (LO QUE FALTABA) ---
        # Creamos un diccionario con la nueva información
        nueva_fila = {
            'ID_Paciente': id_paciente,
            'iEMG_Sano': round(iemg_sano, 4),
            'iEMG_Afectado': round(iemg_afectado, 4),
            'iEMG_Prime_Porcentaje': round(iemg_prime, 2),
            'ENoG_Porcentaje': val_enog,
            'Resultado': resultado_binario
        }
        
        # Convertimos a DataFrame para facilitar el guardado
        df_nuevo = pd.DataFrame([nueva_fila])
        
        # Guardado consecutivo:
        # If 'file' doesn't exist, write with header. If it exists, append without header.
        if not os.path.isfile(RESULTADOS_TOTALES_PATH):
            df_nuevo.to_csv(RESULTADOS_TOTALES_PATH, index=False, mode='w')
        else:
            df_nuevo.to_csv(RESULTADOS_TOTALES_PATH, index=False, mode='a', header=False)

        print(f"\n✅ Registro completado para {id_paciente}")
        print(f"Métricas: iEMG'={iemg_prime:.2f}%, ENoG={val_enog}% -> {resultado_binario}")
        print(f"Los datos se han guardado/añadido en: {RESULTADOS_TOTALES_PATH}")
    else:
        print(f"❌ Error: El ID {id_paciente} no está en la tabla maestra de ENoG.")
else:
    print("Operación cancelada.")
