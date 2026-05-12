import numpy as np
import pandas as pd
import os

# Configuración de carpetas
if not os.path.exists('datos_crudos'):
    os.makedirs('datos_crudos')

def generar_dataset_completo():
    fs = 1000
    duracion = 2.0
    lista_enog = []

    for i in range(1, 25):
        t = np.linspace(0, duracion, int(fs * duracion))
        id_paciente = f'paciente_{i:02d}'
        
        # --- LÓGICA DE CATEGORÍAS (Baba et al.) ---
        if i <= 7:
            # CATEGORÍA: RECUPERACIÓN INCOMPLETA
            # EMG débil
            amp_sano = 0.6 + np.random.normal(0, 0.05)
            amp_afectado = 0.08 + np.random.normal(0, 0.01) 
            # ENoG bajo (menor a 10%)
            val_enog = round(np.random.uniform(1.0, 9.5), 2)
        else:
            # CATEGORÍA: RECUPERACIÓN COMPLETA
            # EMG normal/fuerte
            amp_sano = 0.6 + np.random.normal(0, 0.05)
            amp_afectado = 0.35 + np.random.normal(0, 0.08)
            # ENoG normal (mayor a 10%, usualmente mucho más alto)
            val_enog = round(np.random.uniform(15.0, 95.0), 2)

        # 1. Crear y guardar la señal EMG
        sano = amp_sano * np.random.normal(0, 1, len(t))
        afectado = amp_afectado * np.random.normal(0, 1, len(t))
        
        df_señal = pd.DataFrame({'tiempo_s': t, 'sano_v': sano, 'afectado_v': afectado})
        df_señal.to_csv(f'datos_crudos/{id_paciente}.csv', index=False)
        
        # 2. Guardar el valor de ENoG en nuestra lista temporal
        lista_enog.append({'paciente': id_paciente, 'enog': val_enog})

    # 3. Crear y guardar la TABLA MAESTRA de ENoG
    df_enog_final = pd.DataFrame(lista_enog)
    df_enog_final.to_csv('datos_enog.csv', index=False)
    
    print("✅ Proceso terminado:")
    print("- 24 archivos de señales en /datos_crudos")
    print("- Archivo 'datos_maestros_enog.csv' generado con éxito.")

generar_dataset_completo()
