import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import io

def procesar_y_comparar_physionet(archivo_txt, id_paciente):
    try:
        print(f"Leyendo {archivo_txt}...")
        
        # 1. LEER Y LIMPIAR MANUALMENTE (Para evitar errores de columnas extra)
        valores_emg = []
        with open(archivo_txt, 'r', encoding='latin1') as f:
            for linea in f:
                # Dividimos la línea por cualquier espacio o carácter raro
                partes = linea.replace('í', ' ').replace('ì', ' ').split()
                if len(partes) >= 2:
                    try:
                        # Forzamos la lectura de la SEGUNDA columna (índice 1)
                        val = float(partes[1])
                        valores_emg.append(val)
                    except ValueError:
                        continue # Si no es un número, saltamos la línea
        
        señal_4khz = np.array(valores_emg)
        
        if len(señal_4khz) == 0:
            print(f"❌ No se extrajeron datos de {archivo_txt}")
            return

        # 2. Resampling de 4kHz a 1kHz
        fs_original = 4000
        fs_nueva = 1000
        num_muestras = int(len(señal_4khz) * (fs_nueva / fs_original))
        señal_1khz = signal.resample(señal_4khz, num_muestras)
        señal_1khz = señal_1khz - np.mean(señal_1khz) # Quitar offset
        
        # 3. Preparar 2 segundos (2000 muestras)
        segmento_real = señal_1khz[:2000]
        if np.max(np.abs(segmento_real)) > 0:
            segmento_real = (segmento_real / np.max(np.abs(segmento_real))) * 0.5
        # -----------------------------------------

        t = np.linspace(0, 2, 2000)
        
        # Lado Sano de referencia (Simulado)
        lado_sano_ref = 0.6 * np.random.normal(0, 1, 2000)
        
        # 4. Guardar CSV
        df = pd.DataFrame({
            'tiempo_s': t,
            'sano_v': lado_sano_ref,
            'afectado_v': segmento_real
        })
        df.to_csv(f'datos_crudos/{id_paciente}.csv', index=False)

        # 5. Gráfica de comparación
        plt.figure(figsize=(10, 5))
        plt.plot(t, lado_sano_ref, label='Lado Sano (Sintético)', alpha=0.5, color='gray')
        plt.plot(t, segmento_real, label=f'Lado Afectado (Real: {id_paciente})', color='red', linewidth=1)
        plt.title(f'Validación con Datos Reales: {id_paciente}')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Voltaje (V)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    except Exception as e:
        print(f"❌ Error crítico: {e}")

# Llamadas
procesar_y_comparar_physionet('emg_healthy.txt', 'PACIENTE_REAL_SANO')
procesar_y_comparar_physionet('emg_neuropathy.txt', 'PACIENTE_REAL_NEURO')
