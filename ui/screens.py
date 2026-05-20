"""
CAPA DE PRESENTACIÓN
====================
Módulo responsable de todas las pantallas de la aplicación.

Usa CustomTkinter para una interfaz moderna y atractiva.
Pantallas:
  - LoginScreen  → versión + login
  - HomeScreen   → usuario + botones
  - TablesScreen → esquema de tablas
  - LocalidadesScreen → localidades recogidas

Principios SOLID:
- Cada pantalla es una clase independiente (SRP)
- Heredan de BasePage para comportamiento común (OCP)
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

from security.security_layer import check_version, login
from data.database import DatabaseManager, DataSynchronizer

# ──────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL DE TEMA
# ──────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Paleta de colores de la marca
COLORS = {
    "bg":          "#0D0D0D",
    "card":        "#1A1A2E",
    "accent":      "#E63946",       # rojo Inter
    "accent2":     "#457B9D",       # azul secundario
    "text":        "#F1FAEE",
    "subtext":     "#A8DADC",
    "success":     "#2DC653",
    "warning":     "#F4A261",
    "border":      "#2A2A4A",
}


# ──────────────────────────────────────────────
# CLASE BASE
# ──────────────────────────────────────────────

class BasePage(ctk.CTkFrame):
    """
    Marco base para todas las pantallas.
    Proporciona el fondo, encabezado y método de navegación compartidos.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")

    def show_error(self, message: str):
        """Muestra un cuadro de diálogo de error."""
        messagebox.showerror("Error", message)

    def show_info(self, message: str):
        """Muestra un cuadro de diálogo informativo."""
        messagebox.showinfo("Información", message)

    def _make_header(self, title: str, subtitle: str = ""):
        """Crea el encabezado estándar de cada pantalla."""
        header = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0)
        header.pack(fill="x", pady=(0, 0))

        # Barra de acento superior
        accent_bar = ctk.CTkFrame(header, fg_color=COLORS["accent"], height=4, corner_radius=0)
        accent_bar.pack(fill="x")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(padx=30, pady=15, fill="x")

        ctk.CTkLabel(
            inner, text=title,
            font=ctk.CTkFont(family="Courier New", size=22, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                inner, text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["subtext"],
            ).pack(anchor="w")

        return header

    def _make_button(self, parent, text: str, command, color=None, width=200):
        """Botón estilizado reutilizable."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=color or COLORS["accent"],
            hover_color="#C1121F",
            text_color=COLORS["text"],
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            width=width,
            height=42,
        )


# ──────────────────────────────────────────────
# PANTALLA 1: LOGIN
# ──────────────────────────────────────────────

class LoginScreen(BasePage):
    """
    Pantalla de inicio:
    1. Muestra el estado de versión
    2. Permite ejecutar el login contra la API
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()
        self._run_version_check()

    def _build_ui(self):
        """Construye todos los elementos visuales de la pantalla de login."""

        self._make_header("⚡ INTER RAPIDÍSIMO", "Sistema de Autenticación v1.0")

        # ── Contenedor central ────────────────────────
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=60, pady=30)

        # ── Tarjeta de versión ────────────────────────
        version_card = ctk.CTkFrame(center, fg_color=COLORS["card"], corner_radius=12)
        version_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            version_card, text="CONTROL DE VERSIÓN",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["subtext"],
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.version_label = ctk.CTkLabel(
            version_card,
            text="🔄 Verificando versión...",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["warning"],
            wraplength=500,
            justify="left",
        )
        self.version_label.pack(anchor="w", padx=20, pady=(0, 15))

        # ── Tarjeta de login ──────────────────────────
        login_card = ctk.CTkFrame(center, fg_color=COLORS["card"], corner_radius=12)
        login_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            login_card, text="AUTENTICACIÓN",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["subtext"],
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            login_card,
            text="Usuario: pam.meredy21\nServicio: PTO/BOGOTA — Origen App 9",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # ── Estado del login ─────────────────────────
        self.login_status = ctk.CTkLabel(
            login_card, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"],
            wraplength=500,
        )
        self.login_status.pack(anchor="w", padx=20, pady=(0, 5))

        # ── Barra de progreso ────────────────────────
        self.progress = ctk.CTkProgressBar(login_card, fg_color=COLORS["border"], progress_color=COLORS["accent"])
        self.progress.pack(fill="x", padx=20, pady=(0, 15))
        self.progress.set(0)

        # ── Botón de login ───────────────────────────
        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.login_btn = self._make_button(
            btn_frame, "🔐  INICIAR SESIÓN", self._run_login, width=220
        )
        self.login_btn.pack(side="left")

    def _run_version_check(self):
        """Ejecuta la verificación de versión en un hilo para no bloquear la UI."""
        def task():
            result = check_version()
            # Actualiza la UI desde el hilo principal
            self.after(0, lambda: self._update_version_ui(result))

        threading.Thread(target=task, daemon=True).start()

    def _update_version_ui(self, result: dict):
        """Actualiza la etiqueta de versión con el resultado."""
        colors = {
            "updated": COLORS["success"],
            "outdated": COLORS["warning"],
            "ahead":   COLORS["accent2"],
            "error":   COLORS["accent"],
        }
        color = colors.get(result["status"], COLORS["subtext"])
        self.version_label.configure(text=result["message"], text_color=color)

    def _run_login(self):
        """Ejecuta el login en un hilo y actualiza la UI."""
        self.login_btn.configure(state="disabled", text="Autenticando...")
        self.progress.start()
        self.login_status.configure(text="Conectando con el servidor...")

        def task():
            result = login()
            self.after(0, lambda: self._handle_login_result(result))

        threading.Thread(target=task, daemon=True).start()

    def _handle_login_result(self, result: dict):
        """Procesa el resultado del login y navega si fue exitoso."""
        self.progress.stop()
        self.progress.set(0)
        self.login_btn.configure(state="normal", text="🔐  INICIAR SESIÓN")
        self.login_status.configure(text=result["message"])

        if result["success"]:
            self.login_status.configure(text_color=COLORS["success"])
            # Sincroniza esquema y navega al home
            self._sync_and_navigate(result["user"])
        else:
            self.login_status.configure(text_color=COLORS["accent"])

    def _sync_and_navigate(self, user: dict):
        """Sincroniza la BD de esquema y navega al HOME."""
        def task():
            sync = DataSynchronizer()
            sync.sync_schema()
            self.after(0, lambda: self.controller.show_frame("HomeScreen", user=user))

        threading.Thread(target=task, daemon=True).start()


# ──────────────────────────────────────────────
# PANTALLA 2: HOME
# ──────────────────────────────────────────────

class HomeScreen(BasePage):
    """
    Pantalla principal después del login.
    Muestra datos del usuario y botones de navegación.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.user = {}
        self._build_ui()

    def load_user(self, user: dict):
        """Carga los datos del usuario en los labels."""
        self.user = user
        self.lbl_nombre.configure(text=user.get("Nombre", "—"))
        self.lbl_usuario.configure(text=user.get("Usuario", "—"))
        self.lbl_id.configure(text=user.get("Identificacion", "—"))

    def _build_ui(self):
        self._make_header("🏠 HOME", "Panel principal del usuario")

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=60, pady=30)

        # ── Tarjeta de usuario ────────────────────────
        user_card = ctk.CTkFrame(center, fg_color=COLORS["card"], corner_radius=12)
        user_card.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(
            user_card, text="DATOS DEL USUARIO AUTENTICADO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["subtext"],
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Avatar circular decorativo
        avatar = ctk.CTkFrame(user_card, width=60, height=60, fg_color=COLORS["accent"], corner_radius=30)
        avatar.pack(padx=20, pady=(0, 10), anchor="w")
        ctk.CTkLabel(avatar, text="👤", font=ctk.CTkFont(size=24), fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")

        fields = [
            ("Nombre completo", "lbl_nombre"),
            ("Usuario",         "lbl_usuario"),
            ("Identificación",  "lbl_id"),
        ]
        for label_text, attr in fields:
            row = ctk.CTkFrame(user_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(
                row, text=f"{label_text}:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["subtext"],
                width=160, anchor="w",
            ).pack(side="left")
            lbl = ctk.CTkLabel(
                row, text="—",
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text"],
                anchor="w",
            )
            lbl.pack(side="left")
            setattr(self, attr, lbl)

        ctk.CTkFrame(user_card, fg_color="transparent", height=10).pack()

        # ── Botones de navegación ─────────────────────
        nav = ctk.CTkFrame(center, fg_color="transparent")
        nav.pack(fill="x")

        self._make_button(
            nav, "📋  TABLAS",
            lambda: self.controller.show_frame("TablesScreen"),
            color=COLORS["accent2"], width=180,
        ).pack(side="left", padx=(0, 15))

        self._make_button(
            nav, "📍  LOCALIDADES",
            lambda: self.controller.show_frame("LocalidadesScreen"),
            width=180,
        ).pack(side="left")

        # Botón de cerrar sesión
        self._make_button(
            nav, "↩ Cerrar sesión",
            lambda: self.controller.show_frame("LoginScreen"),
            color=COLORS["border"], width=160,
        ).pack(side="right")


# ──────────────────────────────────────────────
# PANTALLA 3: TABLAS
# ──────────────────────────────────────────────

class TablesScreen(BasePage):
    """
    Muestra las tablas del esquema almacenadas en SQLite.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self):
        self._make_header("📋 ESQUEMA DE TABLAS", "Datos sincronizados desde el servidor")

        # ── Toolbar ───────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0)
        toolbar.pack(fill="x")

        self._make_button(
            toolbar, "← Volver",
            lambda: self.controller.show_frame("HomeScreen"),
            color=COLORS["border"], width=120,
        ).pack(side="left", padx=15, pady=10)

        self._make_button(
            toolbar, "🔄 Sincronizar",
            self._resync,
            color=COLORS["accent2"], width=150,
        ).pack(side="left", pady=10)

        self.sync_status = ctk.CTkLabel(
            toolbar, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"],
        )
        self.sync_status.pack(side="left", padx=15)

        # ── Área de scroll ────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"], label_text=""
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=15)

        self._load_tables()

    def _load_tables(self):
        """Carga las tablas desde SQLite y las renderiza."""
        # Limpia cards previas
        for widget in self.scroll.winfo_children():
            widget.destroy()

        try:
            db = DatabaseManager()
            tables = db.get_tables_schema()
        except RuntimeError as e:
            self.show_error(str(e))
            return

        if not tables:
            ctk.CTkLabel(
                self.scroll,
                text="⚠️ No hay tablas sincronizadas.\nUsa el botón Sincronizar.",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["warning"],
            ).pack(pady=40)
            return

        for i, table in enumerate(tables):
            self._make_table_card(table, i)

    def _make_table_card(self, table: dict, index: int):
        """Renderiza una tarjeta para cada tabla del esquema."""
        card = ctk.CTkFrame(self.scroll, fg_color=COLORS["card"], corner_radius=10)
        card.pack(fill="x", pady=6)

        # Número + nombre
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 4))

        ctk.CTkLabel(
            header,
            text=f"#{index + 1:02d}",
            font=ctk.CTkFont(family="Courier New", size=12, weight="bold"),
            text_color=COLORS["accent"],
            width=40,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=table["nombre_tabla"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left", padx=8)

        # Descripción
        if table.get("descripcion"):
            ctk.CTkLabel(
                card,
                text=table["descripcion"],
                font=ctk.CTkFont(size=12),
                text_color=COLORS["subtext"],
                anchor="w",
                wraplength=550,
            ).pack(anchor="w", padx=55, pady=(0, 4))

        # Campos
        if table.get("campos"):
            ctk.CTkLabel(
                card,
                text=f"Campos: {table['campos'][:120]}{'...' if len(table['campos']) > 120 else ''}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["accent2"],
                anchor="w",
            ).pack(anchor="w", padx=55, pady=(0, 10))

    def _resync(self):
        """Re-sincroniza el esquema desde la API."""
        self.sync_status.configure(text="Sincronizando...", text_color=COLORS["warning"])

        def task():
            sync = DataSynchronizer()
            result = sync.sync_schema()
            self.after(0, lambda: self._after_sync(result))

        threading.Thread(target=task, daemon=True).start()

    def _after_sync(self, result: dict):
        color = COLORS["success"] if result["success"] else COLORS["accent"]
        self.sync_status.configure(text=result["message"], text_color=color)
        self._load_tables()


# ──────────────────────────────────────────────
# PANTALLA 4: LOCALIDADES
# ──────────────────────────────────────────────

class LocalidadesScreen(BasePage):
    """
    Consume la API de localidades recogidas y muestra
    AbreviacionCiudad y NombreCompleto de cada registro.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build_ui()

    def _build_ui(self):
        self._make_header("📍 LOCALIDADES RECOGIDAS", "Ciudades disponibles en el sistema")

        # ── Toolbar ───────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0)
        toolbar.pack(fill="x")

        self._make_button(
            toolbar, "← Volver",
            lambda: self.controller.show_frame("HomeScreen"),
            color=COLORS["border"], width=120,
        ).pack(side="left", padx=15, pady=10)

        # Buscador
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._filter_list)
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            placeholder_text="🔍 Buscar ciudad...",
            width=220,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        search_entry.pack(side="left", padx=10, pady=10)

        self.count_label = ctk.CTkLabel(
            toolbar, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["subtext"],
        )
        self.count_label.pack(side="left", padx=10)

        # ── Área de scroll ────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg"])
        self.scroll.pack(fill="both", expand=True, padx=20, pady=15)

        # Estado de carga
        self.load_label = ctk.CTkLabel(
            self.scroll,
            text="🔄 Cargando localidades...",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["warning"],
        )
        self.load_label.pack(pady=40)

        self.all_localidades = []
        self._fetch_localidades()

    def _fetch_localidades(self):
        """Obtiene las localidades en un hilo."""
        def task():
            sync = DataSynchronizer()
            result = sync.get_localidades()
            self.after(0, lambda: self._render_localidades(result))

        threading.Thread(target=task, daemon=True).start()

    def _render_localidades(self, result: dict):
        """Renderiza la lista de localidades."""
        self.load_label.destroy()

        if not result["success"] or not result["data"]:
            ctk.CTkLabel(
                self.scroll,
                text=result["message"],
                font=ctk.CTkFont(size=13),
                text_color=COLORS["accent"],
            ).pack(pady=40)
            return

        self.all_localidades = result["data"]
        self.count_label.configure(text=f"{len(self.all_localidades)} localidades")
        self._display_localidades(self.all_localidades)

    def _display_localidades(self, localidades: list):
        """Dibuja las tarjetas de localidades."""
        for widget in self.scroll.winfo_children():
            widget.destroy()

        for loc in localidades:
            abrev = loc.get("AbreviacionCiudad") or loc.get("abreviacion") or "—"
            nombre = loc.get("NombreCompleto") or loc.get("nombre") or "—"

            row = ctk.CTkFrame(self.scroll, fg_color=COLORS["card"], corner_radius=8)
            row.pack(fill="x", pady=3)

            # Badge de abreviación
            badge = ctk.CTkFrame(row, fg_color=COLORS["accent"], corner_radius=6, width=70)
            badge.pack(side="left", padx=12, pady=10)
            badge.pack_propagate(False)
            ctk.CTkLabel(
                badge,
                text=abrev,
                font=ctk.CTkFont(family="Courier New", size=12, weight="bold"),
                text_color=COLORS["text"],
            ).pack(expand=True)

            ctk.CTkLabel(
                row,
                text=nombre,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text"],
                anchor="w",
            ).pack(side="left", padx=10, fill="x", expand=True)

    def _filter_list(self, *args):
        """Filtra la lista según el texto del buscador."""
        query = self.search_var.get().lower()
        filtered = [
            loc for loc in self.all_localidades
            if query in (loc.get("AbreviacionCiudad") or "").lower()
            or query in (loc.get("NombreCompleto") or "").lower()
        ]
        self.count_label.configure(text=f"{len(filtered)} localidades")
        self._display_localidades(filtered)
