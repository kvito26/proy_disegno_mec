"""
LiDAR D300 / LD19 (LDRobot) - Visor de mapa escaneado
Formato de log: [LDS][INFO][ts][stamp:...,angle:...,distance(mm):...,intensity:...]

Requiere: pip install matplotlib numpy
"""

import re
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# ─────────────────────────────────────────────
#  PARSEO DEL LOG
# ─────────────────────────────────────────────
LINE_RE = re.compile(
    r"angle:([\d.]+),distance\(mm\):([\d]+),intensity:([\d]+)"
)

def parse_log(filepath: str, max_dist_mm: int, min_intensity: int,
              progress_cb=None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Lee el archivo y devuelve arrays de (x, y, intensity) en metros.
    Filtra: distance==0, distance > max_dist_mm, intensity < min_intensity.
    """
    angles, distances, intensities = [], [], []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    total = len(lines)
    for i, line in enumerate(lines):
        if progress_cb and i % 5000 == 0:
            progress_cb(i / total * 100)

        m = LINE_RE.search(line)
        if not m:
            continue

        angle_deg = float(m.group(1))
        dist_mm   = int(m.group(2))
        inten     = int(m.group(3))

        if dist_mm == 0 or dist_mm > max_dist_mm or inten < min_intensity:
            continue

        angles.append(math.radians(angle_deg))
        distances.append(dist_mm / 1000.0)   # → metros
        intensities.append(inten)

    if not angles:
        return np.array([]), np.array([]), np.array([])

    a  = np.array(angles)
    d  = np.array(distances)
    iv = np.array(intensities, dtype=float)

    x = d * np.cos(a)
    y = d * np.sin(a)

    return x, y, iv


# ─────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────
class LidarViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LiDAR D300 / LD19 — Visor de mapa")
        self.configure(bg="#1e1e2e")
        self.geometry("1100x780")
        self.resizable(True, True)

        self.filepath = tk.StringVar(value="(ningún archivo seleccionado)")
        self.max_dist  = tk.IntVar(value=8000)
        self.min_inten = tk.IntVar(value=0)
        self.point_size = tk.DoubleVar(value=0.8)
        self.colormap   = tk.StringVar(value="plasma")
        self.show_origin = tk.BooleanVar(value=True)
        self.show_rings  = tk.BooleanVar(value=True)

        self._x = self._y = self._iv = None

        self._build_ui()

    # ── INTERFAZ ──────────────────────────────
    def _build_ui(self):
        BG   = "#1e1e2e"
        PANEL= "#2a2a3e"
        FG   = "#cdd6f4"
        ACC  = "#89b4fa"
        BTN  = "#313244"

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame",        background=PANEL)
        style.configure("TLabel",        background=PANEL, foreground=FG,
                         font=("Segoe UI", 9))
        style.configure("TCheckbutton",  background=PANEL, foreground=FG,
                         font=("Segoe UI", 9))
        style.configure("TButton",       background=BTN,   foreground=FG,
                         font=("Segoe UI", 9, "bold"), relief="flat", padding=5)
        style.map("TButton",
                  background=[("active", ACC)],
                  foreground=[("active", "#1e1e2e")])
        style.configure("TScale",        background=PANEL, troughcolor=BTN)
        style.configure("Horizontal.TProgressbar",
                         troughcolor=BTN, background=ACC, thickness=8)

        # ── Panel izquierdo (controles) ────────
        ctrl = ttk.Frame(self, width=240)
        ctrl.pack(side="left", fill="y", padx=0, pady=0)
        ctrl.pack_propagate(False)

        tk.Label(ctrl, text="⟨ LiDAR Viewer ⟩",
                 bg=PANEL, fg=ACC, font=("Segoe UI", 12, "bold")).pack(pady=(16, 4))

        self._sep(ctrl)

        # Archivo
        tk.Label(ctrl, text="ARCHIVO LOG", bg=PANEL, fg="#6c7086",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8,2))
        tk.Label(ctrl, textvariable=self.filepath, bg=PANEL, fg=FG,
                 font=("Segoe UI", 8), wraplength=210, justify="left").pack(
                 anchor="w", padx=12)
        ttk.Button(ctrl, text="📂  Abrir archivo...", command=self._open_file).pack(
                 fill="x", padx=12, pady=(6, 4))

        self._sep(ctrl)

        # Filtros
        tk.Label(ctrl, text="FILTROS", bg=PANEL, fg="#6c7086",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8,0))

        self._slider(ctrl, "Distancia máx. (mm):", self.max_dist, 500, 20000, 500)
        self._slider(ctrl, "Intensidad mín.:",      self.min_inten, 0, 255, 1)

        self._sep(ctrl)

        # Visualización
        tk.Label(ctrl, text="VISUALIZACIÓN", bg=PANEL, fg="#6c7086",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8,0))

        self._slider(ctrl, "Tamaño de punto:", self.point_size, 0.1, 5.0, 0.1)

        tk.Label(ctrl, text="Paleta de colores:", bg=PANEL, fg=FG,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(6, 2))
        cmap_options = ["plasma", "viridis", "inferno", "magma",
                        "hot", "cool", "turbo", "rainbow", "YlOrRd"]
        cm_menu = tk.OptionMenu(ctrl, self.colormap, *cmap_options)
        cm_menu.config(bg=BTN, fg=FG, font=("Segoe UI", 9),
                       activebackground=ACC, activeforeground="#1e1e2e",
                       relief="flat", highlightthickness=0, bd=0)
        cm_menu["menu"].config(bg=BTN, fg=FG)
        cm_menu.pack(fill="x", padx=12, pady=(0, 4))

        ttk.Checkbutton(ctrl, text="Mostrar origen (sensor)",
                        variable=self.show_origin).pack(anchor="w", padx=12)
        ttk.Checkbutton(ctrl, text="Mostrar anillos de distancia",
                        variable=self.show_rings).pack(anchor="w", padx=12, pady=(0,6))

        self._sep(ctrl)

        ttk.Button(ctrl, text="▶  Generar mapa", command=self._start_render).pack(
                 fill="x", padx=12, pady=(8, 4))
        ttk.Button(ctrl, text="💾  Guardar imagen", command=self._save_image).pack(
                 fill="x", padx=12, pady=(0, 4))

        self._sep(ctrl)

        # Stats
        self.lbl_stats = tk.Label(ctrl, text="", bg=PANEL, fg="#a6e3a1",
                                  font=("Segoe UI", 8), justify="left", wraplength=210)
        self.lbl_stats.pack(anchor="w", padx=12, pady=4)

        # Barra de progreso
        self.progress = ttk.Progressbar(ctrl, orient="horizontal",
                                        mode="determinate", style="Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=12, pady=(4, 8))
        self.lbl_status = tk.Label(ctrl, text="Listo.", bg=PANEL, fg="#6c7086",
                                   font=("Segoe UI", 8))
        self.lbl_status.pack(anchor="w", padx=12)

        # ── Panel derecho (matplotlib) ─────────
        plot_frame = tk.Frame(self, bg=BG)
        plot_frame.pack(side="right", fill="both", expand=True)

        self.fig = plt.Figure(facecolor="#11111b")
        self.ax  = self.fig.add_subplot(111)
        self._init_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar_frame = tk.Frame(plot_frame, bg="#1e1e2e")
        toolbar_frame.pack(fill="x")
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.config(background="#1e1e2e")
        toolbar.update()

    def _sep(self, parent):
        tk.Frame(parent, bg="#313244", height=1).pack(fill="x", padx=8, pady=4)

    def _slider(self, parent, label, var, from_, to, resolution):
        tk.Label(parent, text=label, bg="#2a2a3e", fg="#cdd6f4",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(4,0))
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=12, pady=(0,4))
        sc = tk.Scale(row, from_=from_, to=to, resolution=resolution,
                      variable=var, orient="horizontal",
                      bg="#2a2a3e", fg="#cdd6f4", troughcolor="#313244",
                      highlightthickness=0, bd=0, sliderrelief="flat",
                      font=("Segoe UI", 8))
        sc.pack(fill="x")

    def _init_axes(self):
        ax = self.ax
        ax.set_facecolor("#11111b")
        ax.tick_params(colors="#585b70")
        for spine in ax.spines.values():
            spine.set_edgecolor("#313244")
        ax.set_xlabel("X (m)", color="#585b70", fontsize=9)
        ax.set_ylabel("Y (m)", color="#585b70", fontsize=9)
        ax.set_title("Sin datos cargados — abre un archivo .log",
                     color="#6c7086", fontsize=10)
        ax.set_aspect("equal")
        ax.grid(True, color="#1e1e2e", linewidth=0.5)
        self.canvas.draw() if hasattr(self, "canvas") else None

    # ── ACCIONES ──────────────────────────────
    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de log LiDAR",
            filetypes=[("Archivos log", "*.log *.txt"), ("Todos", "*.*")]
        )
        if path:
            # Mostrar solo el nombre del archivo
            import os
            self.filepath.set(os.path.basename(path))
            self._full_path = path

    def _start_render(self):
        if not hasattr(self, "_full_path"):
            messagebox.showwarning("Sin archivo", "Por favor selecciona un archivo .log primero.")
            return
        # Ejecutar en hilo para no bloquear la UI
        threading.Thread(target=self._render_thread, daemon=True).start()

    def _render_thread(self):
        self._set_status("Leyendo y procesando datos...")
        self.progress["value"] = 0

        def on_progress(pct):
            self.progress["value"] = pct
            self.update_idletasks()

        try:
            x, y, iv = parse_log(
                self._full_path,
                max_dist_mm=self.max_dist.get(),
                min_intensity=self.min_inten.get(),
                progress_cb=on_progress
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
            self._set_status("Error al leer.")
            return

        self.progress["value"] = 100
        self._x, self._y, self._iv = x, y, iv

        if len(x) == 0:
            messagebox.showwarning("Sin puntos", "No se encontraron puntos válidos con los filtros actuales.")
            self._set_status("Sin puntos.")
            return

        self._set_status("Dibujando mapa...")
        self.after(0, self._draw_map)

    def _draw_map(self):
        x, y, iv = self._x, self._y, self._iv
        self.ax.clear()
        ax = self.ax
        ax.set_facecolor("#11111b")

        # Scatter coloreado por intensidad
        sc = ax.scatter(x, y,
                        c=iv,
                        cmap=self.colormap.get(),
                        s=self.point_size.get(),
                        alpha=0.85,
                        linewidths=0,
                        vmin=iv.min(), vmax=iv.max())

        # Barra de color
        if hasattr(self, "_cbar"):
            try: self._cbar.remove()
            except: pass
        self._cbar = self.fig.colorbar(sc, ax=ax, pad=0.02, shrink=0.7)
        self._cbar.set_label("Intensidad", color="#cdd6f4", fontsize=8)
        self._cbar.ax.yaxis.set_tick_params(color="#585b70")
        plt.setp(self._cbar.ax.yaxis.get_ticklabels(), color="#cdd6f4", fontsize=7)

        # Origen
        if self.show_origin.get():
            ax.plot(0, 0, "o", color="#f38ba8", markersize=7, zorder=5, label="Sensor")
            ax.plot(0, 0, "+", color="#f38ba8", markersize=14, zorder=5, linewidth=1.5)

        # Anillos de distancia
        if self.show_rings.get():
            max_r = math.sqrt(max(x.max()**2, y.max()**2, x.min()**2, y.min()**2))
            ring_step = self._nice_step(max_r)
            r = ring_step
            while r <= max_r * 1.05:
                circle = plt.Circle((0, 0), r, color="#313244",
                                    fill=False, linewidth=0.6, linestyle="--", zorder=0)
                ax.add_patch(circle)
                ax.text(r * math.cos(math.radians(10)),
                        r * math.sin(math.radians(10)),
                        f"{r:.1f}m", color="#585b70", fontsize=7, zorder=1)
                r += ring_step

        # Ejes y título
        ax.tick_params(colors="#585b70", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#313244")
        ax.set_xlabel("X (m)", color="#cdd6f4", fontsize=9)
        ax.set_ylabel("Y (m)", color="#cdd6f4", fontsize=9)
        ax.set_title(f"Mapa LiDAR — {len(x):,} puntos  |  "
                     f"dist. máx: {self.max_dist.get()} mm",
                     color="#cdd6f4", fontsize=10, pad=10)
        ax.set_aspect("equal")
        ax.grid(True, color="#1e1e2e", linewidth=0.4, zorder=0)
        if self.show_origin.get():
            ax.legend(fontsize=8, facecolor="#1e1e2e", edgecolor="#313244",
                      labelcolor="#cdd6f4")

        self.canvas.draw()

        # Stats
        dists = np.sqrt(x**2 + y**2)
        stats = (f"Puntos: {len(x):,}\n"
                 f"Dist. media: {dists.mean()*100:.1f} cm\n"
                 f"Dist. mín:   {dists.min()*100:.1f} cm\n"
                 f"Dist. máx:   {dists.max()*100:.1f} cm\n"
                 f"Intens. media: {iv.mean():.0f}")
        self.lbl_stats.config(text=stats)
        self.progress["value"] = 100
        self._set_status("✓ Mapa generado.")

    def _nice_step(self, max_r):
        """Calcula un paso 'limpio' para los anillos."""
        raw = max_r / 5
        magnitude = 10 ** math.floor(math.log10(raw))
        for factor in [1, 2, 2.5, 5, 10]:
            if magnitude * factor >= raw:
                return round(magnitude * factor, 4)
        return round(magnitude * 10, 4)

    def _save_image(self):
        if self._x is None or len(self._x) == 0:
            messagebox.showwarning("Sin mapa", "Genera el mapa primero.")
            return
        path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("SVG", "*.svg"), ("PDF", "*.pdf")]
        )
        if path:
            self.fig.savefig(path, dpi=200, bbox_inches="tight",
                             facecolor=self.fig.get_facecolor())
            messagebox.showinfo("Guardado", f"Imagen guardada en:\n{path}")

    def _set_status(self, msg):
        self.lbl_status.config(text=msg)
        self.update_idletasks()


# ─────────────────────────────────────────────
#  ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = LidarViewer()
    app.mainloop()
