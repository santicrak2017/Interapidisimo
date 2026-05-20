# Informe Técnico — Proyecto Inter Rapidísimo
**Prueba Técnica · Ingeniería de Software 2**

---

## 1. Descripción General

El trabajo consiste en una aplicacion que cumpla algunos requerimientos: seguridad,datos y presentación. En donde la aplicacion consumira unos endpoints REST para confirmar informacion que esta en esta y verificar con la que esta en el local. Y ademas crear una base de datos con SQLite para sincronizar y crear una interfaz que contenga un login , y las consultas para los endpoints.

---

## 2. Capa de Seguridad

### 2.1 Control de Versiones

Se implementó el consumo del endpoint:

```
GET /ParametrosFramework/ConsultarParametrosFramework/VPStoreAppControl
```

La lógica compara la versión local (`VERSION_LOCAL = "1.0.0"`) con la versión retornada por la API y muestra un mensaje al usuario según el resultado:
Si la version local es menor a la de la API entonces hay una version mas reciente y la dice . Si llega a ser que la local es mas nueva ,entonces muestra que la version es mas nueva que la del servidor. Y si llega a ser la misma pues la App esta al dia.


> **Momento de ejecucion:** el endpoint no retorna los permisos necesarios para acceder a la información de versión. Por esta razón, el control de versiones queda implementado en código pero no puede validarse con datos reales del servidor.

---

### 2.2 Login

Se implementó el consumo del endpoint de autenticación:

```
POST /ApiSeguridadPruebas/api/Seguridad/AuthenticaUsuarioApp
```
Y el flujo de este consiste en:

1. La app envía la petición POST con las credenciales
2. Si el código HTTP es diferente de `200`, se muestra un mensaje de alerta con el detalle del error
3. Si el código HTTP es `200`, se extraen los campos `Usuario`, `Identificacion` y `Nombre` del response
4. Esos datos se almacenan en la tabla local `usuarios` de la base de datos

---

## 3. Capa de Datos

### 3.1 Base de Datos Local

Se creó una base de datos **SQLite** local con tres tablas:

**Tabla `usuarios`** — almacena el usuario autenticado:
```sql
CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario         TEXT NOT NULL,
    identificacion  TEXT NOT NULL,
    nombre          TEXT NOT NULL,
    fecha_login     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabla `esquema_tablas`** — almacena las tablas del sistema:
```sql
CREATE TABLE IF NOT EXISTS esquema_tablas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_tabla    TEXT NOT NULL,
    descripcion     TEXT,
    campos          TEXT,
    fecha_sync      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabla `localidades`** — cache local de ciudades:
```sql
CREATE TABLE IF NOT EXISTS localidades (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    abreviacion_ciudad  TEXT,
    nombre_completo     TEXT,
    fecha_sync          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Las tablas se crean automáticamente al iniciar la aplicación si no existen, garantizando que la base de datos siempre esté lista antes de cualquier operación.

### 3.2 Sincronización de Tablas

Se implementó el consumo del endpoint:

```
GET /SincronizadorDatos/ObtenerEsquema/true
```

La lógica descarga la lista de tablas del sistema y las almacena en la tabla `esquema_tablas` local para su consulta posterior sin necesidad de internet.

> **Momento de ejecucion:** el endpoint no retorna los permisos necesarios para acceder al esquema.Esto como en el ejemplo anterior, haciendo que al momento de crear o mostrar la tabla haya un error al no tener la información de la API debido a que no tiene ningun tipo de acceso.

## 4. Capa de Presentación

La interfaz gráfica fue desarrollada con **CustomTkinter**, y ayuda a realizar de una manera mas sencilla la parte del frontend.

Se implementaron **4 pantallas**:

### Pantalla LOGIN
- Muestra el estado del control de versiones en tiempo real
- Presenta las credenciales configuradas para la autenticación
- Botón de inicio de sesión con barra de progreso animada durante la petición
- Todas las llamadas a la API se ejecutan en hilos secundarios para no bloquear la interfaz

### Pantalla HOME
- Muestra los datos del usuario autenticado: Nombre completo, Usuario e Identificación
- Dos botones de navegación: **Tablas** y **Localidades**
- Botón de cierre de sesión

### Pantalla TABLAS
- Lista las tablas almacenadas en SQLite con nombre, descripción y campos
- Botón de re-sincronización que actualiza los datos desde la API

### Pantalla LOCALIDADES
- Consume el endpoint `ObtenerLocalidadesRecogidas` en tiempo real
- Muestra `AbreviacionCiudad` y `NombreCompleto` de cada registro
- Buscador en tiempo real para filtrar por nombre o abreviación


## 5.Herramientas usadas

Python  3.11 
CustomTkinter  5.2.2 
Requests  2.31.0 
SQLite3 
Threading


## 6. Conclusiones.

- El endpoint de **"control de versiones"** y el de **"sincronización de esquema"** no cuentan con los permisos necesarios para retornar información, por lo que estas funcionalidades están implementadas en código pero no pueden validarse con datos reales. A pesar de eso se pudo hacer una analisis interesante acerca de las APIS y como estas se puede construir y guardar gracias a herramientas que nos permiten recolectar información valiosa.

