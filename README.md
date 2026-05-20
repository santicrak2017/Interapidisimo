# 🚀 Inter Rapidísimo — Prueba Técnica en Python

Implementación de la prueba técnica usando Python + CustomTkinter.

## 📁 Estructura del proyecto

```
proyecto_inter/
│
├── main.py                   ← Punto de entrada, arrancar aquí
│
├── security/
│   ├── __init__.py
│   └── security_layer.py     ← Control de versión + Login
│
├── data/
│   ├── __init__.py
│   ├── database.py           ← SQLite + sincronización de esquema
│   └── interrapidisimo.db    ← Se crea automáticamente al ejecutar
│
├── ui/
│   ├── __init__.py
│   └── screens.py            ← Las 4 pantallas de la aplicación
│
└── requirements.txt          ← Dependencias
```

## ⚙️ Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la app

```bash
python main.py
```

---

## 🗺️ Flujo de la aplicación

```
[Login Screen]
    │
    ├─ Verifica versión (API) ──→ muestra mensaje de estado
    │
    └─ Botón "INICIAR SESIÓN"
         │
         ├─ Llama API de autenticación
         ├─ Guarda usuario en SQLite
         ├─ Sincroniza esquema de tablas
         │
         └──→ [Home Screen]
                  │
                  ├─ Botón "TABLAS"  ──→ [Tables Screen] (lee SQLite)
                  └─ Botón "LOCALIDADES" ──→ [Localidades Screen] (llama API)
```

---

## 🏗️ Capas del proyecto

| Capa          | Archivo               | Responsabilidad                          |
|---------------|-----------------------|------------------------------------------|
| Seguridad     | `security_layer.py`   | Versión + Login + manejo de errores HTTP |
| Datos         | `database.py`         | SQLite + sync de esquema + localidades   |
| Presentación  | `screens.py`          | 4 pantallas con CustomTkinter            |
| Controlador   | `main.py`             | Navegación entre pantallas               |

---

## 🛠️ Herramientas alternativas para la presentación

Si no quieres usar CustomTkinter, aquí hay otras opciones:

| Herramienta    | Tipo          | Ventaja                                   |
|----------------|---------------|-------------------------------------------|
| **CustomTkinter** | Desktop    | Moderna, sin instalar browser             |
| **PyQt6**      | Desktop       | Muy profesional, parecido a Android       |
| **Flet**       | Desktop/Web   | Parecido a Flutter, muy visual            |
| **Tkinter**    | Desktop       | Ya viene en Python, sin instalar nada     |
| **Streamlit**  | Web (browser) | Muy fácil, abre en el navegador           |
| **Flask + HTML** | Web        | Control total del diseño                  |

---

## 📌 Notas importantes

- La base de datos SQLite se crea automáticamente en `data/interrapidisimo.db`
- Todas las llamadas a la API se hacen en hilos separados (no congela la interfaz)
- Los errores de red se capturan y muestran al usuario sin romper la app
- La versión local está en `security_layer.py → VERSION_LOCAL = "1.0.0"`
