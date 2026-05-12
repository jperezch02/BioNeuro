import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt
import os
from PIL import Image

class AnalizadorBiopotencialesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Analizador de Biopotenciales - Sistema Validado (Baba et al.)")
        self.geometry("1500x950")
        ctk.set_appearance_mode("dark")
        
        # Configuración técnica (Sincronizada con tus pilares)
        self.fs = 1000.0
        self.lowcut = 20.0
        self.highcut = 450.0
        self.ruta_carpeta = ""
        self.datos_actuales = None
        
        try:
            self.tabla_maestra = pd.read_csv('datos_enog.csv')
        except FileNotFoundError:
            messagebox.showerror("Error Crítico", "No se encuentra 'datos_enog.csv'.")
            self.destroy()

        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Panel de Control Lateral
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="ANÁLISIS NEUROMUSCULAR", font=("Consolas", 18, "bold"), text_color="#00FFC2").pack(pady=25)
        
        self.btn_folder = ctk.CTkButton(self.sidebar, text="1. CARGAR DIRECTORIO sEMG", command=self.cargar_carpeta)
        self.btn_folder.pack(pady=10, padx=20)

        self.pacientes_list = ctk.CTkOptionMenu(self.sidebar, values=["Esperando selección"], command=self.visualizar_crudo, fg_color="#333333")
        self.pacientes_list.pack(pady=10, padx=20)

        ctk.CTkLabel(self.sidebar, text="PROCESAMIENTO INDIVIDUAL", font=("Arial", 12, "italic"), text_color="gray").pack(pady=(15, 0))
        
        self.btn_proc = ctk.CTkButton(self.sidebar, text="2. FILTRAR Y RECTIFICAR", command=self.ejecutar_procesamiento, fg_color="#1f538d")
        self.btn_proc.pack(pady=10, padx=20)

        self.btn_diag = ctk.CTkButton(self.sidebar, text="3. CLASIFICAR CLÍNICA", command=self.ejecutar_diagnostico, fg_color="#006400")
        self.btn_diag.pack(pady=10, padx=20)

        # --- NUEVA SECCIÓN: ANÁLISIS POR LOTES ---
        ctk.CTkLabel(self.sidebar, text="ANÁLISIS POR LOTES (CARPETA)", font=("Arial", 12, "italic"), text_color="gray").pack(pady=(25, 0))
        
        self.btn_batch_raw = ctk.CTkButton(self.sidebar, text="GRAFICAR LOTE CRUDO", command=lambda: self.graficar_lote("crudo"), fg_color="#434343")
        self.btn_batch_raw.pack(pady=10, padx=20)

        self.btn_batch_proc = ctk.CTkButton(self.sidebar, text="GRAFICAR LOTE PROCESADO", command=lambda: self.graficar_lote("procesado"), fg_color="#434343")
        self.btn_batch_proc.pack(pady=10, padx=20)

        # 2. Panel Principal (Scrollable)
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="#121212")
        self.main_scroll.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.mostrar_imagen_espera()
        self.frame_crudo = None
        self.frame_proc = None

    def graficar_lote(self, tipo):
        """Genera una ventana independiente con un mosaico de todas las señales de la carpeta."""
        if tipo == "crudo":
            if not self.ruta_carpeta:
                messagebox.showwarning("Aviso", "Primero carga una carpeta de crudos.")
                return
            archivos = [os.path.join(self.ruta_carpeta, f) for f in os.listdir(self.ruta_carpeta) if f.endswith('.csv')]
            col_sano, col_afectado = 'sano_v', 'afectado_v'
            color_p = '#00AEEF'
            titulo_win = "Mosaico de Señales Crudas (T0)"
        else:
            ruta_proc = 'datos_procesados'
            if not os.path.exists(ruta_proc):
                messagebox.showwarning("Aviso", "No existe la carpeta de datos procesados.")
                return
            archivos = [os.path.join(ruta_proc, f) for f in os.listdir(ruta_proc) if f.endswith('.csv')]
            col_sano, col_afectado = 'sano_rect_v', 'afectado_rect_v'
            color_p = '#FFBF00'
            titulo_win = "Mosaico de Señales Procesadas (Baba et al.)"

        if not archivos: return

        # Crear ventana emergente
        ventana_lote = ctk.CTkToplevel(self)
        ventana_lote.title(titulo_win)
        ventana_lote.geometry("1200x800")
        
        scroll_lote = ctk.CTkScrollableFrame(ventana_lote, fg_color="#000000")
        scroll_lote.pack(fill="both", expand=True)

        # Cálculo de rejilla (ejemplo: 4 columnas)
        n = len(archivos)
        cols = 1  # <--- Cambiamos a 1 columna
        rows = n
        
        # Ajustamos el tamaño de la figura: 
        # (Ancho=12, Alto=3 pulgadas por cada gráfica para que sean alargadas)
        fig, axs = plt.subplots(rows, cols, figsize=(12, 3 * rows), facecolor='#000000')
        fig.subplots_adjust(hspace=0.6) # Un poco más de espacio entre pacientes

        # Si solo hay 1 archivo, Matplotlib no devuelve un array, lo convertimos:
        if n == 1: axs = [axs]
        
        for i, ruta in enumerate(archivos):
            df_temp = pd.read_csv(ruta)
            nombre = os.path.basename(ruta).replace('PROC_', '').replace('.csv', '')
            
            # Graficamos con mayor detalle
            axs[i].plot(df_temp[col_afectado], color=color_p, lw=0.6)
            axs[i].set_title(f"PACIENTE: {nombre}", color='#00FFC2', loc='left', fontsize=12, fontweight='bold')
            
            # Estética de osciloscopio médico
            axs[i].set_facecolor('#050505')
            axs[i].tick_params(colors='white', labelsize=9)
            axs[i].grid(True, alpha=0.15, color='green') # Rejilla tipo monitor médico
            axs[i].set_ylabel("Amplitud (V)", color='white', fontsize=8)

        # Limpiar ejes sobrantes
        for j in range(i + 1, len(axs)):
            fig.delaxes(axs[j])

        canvas = FigureCanvasTkAgg(fig, master=scroll_lote)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

    def mostrar_imagen_espera(self):
        try:
            img_pil = Image.open("bioneuro4.png")
            self.img_espera = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(1100, 600))
            self.lbl_espera = ctk.CTkLabel(self.main_scroll, image=self.img_espera, text="")
            self.lbl_espera.pack(expand=True, pady=50)
        except:
            self.lbl_espera = ctk.CTkLabel(self.main_scroll, text="ESPERANDO SELECCIÓN", font=("Consolas", 20))
            self.lbl_espera.pack(expand=True, pady=50)

    def preparar_scroll(self):
        if self.lbl_espera: self.lbl_espera.pack_forget()
        if self.frame_crudo: self.frame_crudo.pack_forget()
        if self.frame_proc: self.frame_proc.pack_forget()
        if hasattr(self, 'lbl_res_clinic'): self.lbl_res_clinic.pack_forget()
        
        self.frame_crudo = ctk.CTkFrame(self.main_scroll, fg_color="#121212")
        self.frame_crudo.pack(fill="x", pady=10)
        self.frame_proc = ctk.CTkFrame(self.main_scroll, fg_color="#121212")

    def visualizar_crudo(self, nombre):
        path = os.path.join(self.ruta_carpeta, nombre)
        self.datos_actuales = pd.read_csv(path)
        self.preparar_scroll()
        self.graficar_en_frame(self.frame_crudo, self.datos_actuales['sano_v'], self.datos_actuales['afectado_v'], "sEMG CRUDO (ADQUISICIÓN)")

    def ejecutar_procesamiento(self):
        if self.datos_actuales is None: return
        nyq = 0.5 * self.fs
        low, high = self.lowcut / nyq, self.highcut / nyq
        b, a = butter(4, [low, high], btype='band')
        self.sano_proc = np.abs(filtfilt(b, a, self.datos_actuales['sano_v']))
        self.afectado_proc = np.abs(filtfilt(b, a, self.datos_actuales['afectado_v']))

        if not os.path.exists('datos_procesados'): os.makedirs('datos_procesados')
        nombre_base = self.pacientes_list.get()
        df_proc = pd.DataFrame({'tiempo_s': self.datos_actuales['tiempo_s'], 'sano_rect_v': self.sano_proc, 'afectado_rect_v': self.afectado_proc})
        df_proc.to_csv(f"datos_procesados/PROC_{nombre_base}", index=False)

        if not self.frame_proc.winfo_ismapped(): self.frame_proc.pack(fill="x", pady=20)
        self.graficar_en_frame(self.frame_proc, self.sano_proc, self.afectado_proc, "sEMG PROCESADO (RECTIFICADO)")

    def graficar_en_frame(self, frame, data_s, data_a, titulo):
        for widget in frame.winfo_children(): widget.destroy()
        ctk.CTkLabel(frame, text=titulo, font=("Arial", 14, "bold")).pack()
        fig, axs = plt.subplots(2, 1, figsize=(10, 6), facecolor='#121212')
        axs[0].plot(data_s, color='#00AEEF', lw=0.7); axs[1].plot(data_a, color='#FF5555', lw=0.7)
        for ax in axs:
            ax.set_facecolor('#000000'); ax.tick_params(colors='white'); ax.grid(True, alpha=0.1)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True); canvas.draw()

    def ejecutar_diagnostico(self):
        if not hasattr(self, 'sano_proc'): return
        dt = 1/self.fs
        iemg_s, iemg_a = np.sum(self.sano_proc)*dt, np.sum(self.afectado_proc)*dt
        iemg_p = (iemg_a / iemg_s) * 100
        id_paciente = self.pacientes_list.get().replace('.csv', '')
        val_enog = self.tabla_maestra[self.tabla_maestra['paciente'] == id_paciente]['enog'].values[0]
        diag = "RECUPERACIÓN INCOMPLETA" if (iemg_p <= 25 and val_enog < 10) else "RECUPERACIÓN COMPLETA"
        color = "#8B0000" if "INCOMPLETA" in diag else "#006400"

        if hasattr(self, 'lbl_res_clinic'): self.lbl_res_clinic.pack_forget()
        self.lbl_res_clinic = ctk.CTkLabel(self.main_scroll, text=f"PRONÓSTICO: {diag}\niEMG': {iemg_p:.2f}% | ENoG: {val_enog}%", 
                                            font=("Consolas", 18, "bold"), fg_color=color, text_color="white", height=60)
        self.lbl_res_clinic.pack(fill="x", pady=10, before=self.frame_crudo)

    def cargar_carpeta(self):
        self.ruta_carpeta = filedialog.askdirectory()
        if self.ruta_carpeta:
            archivos = sorted([f for f in os.listdir(self.ruta_carpeta) if f.endswith('.csv')])
            self.pacientes_list.configure(values=archivos)

if __name__ == "__main__":
    app = AnalizadorBiopotencialesApp()
    app.mainloop()
