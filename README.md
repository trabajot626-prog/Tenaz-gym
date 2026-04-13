# Gym-Tenaz

Sistema de gestión para el gimnasio **Gym-Tenaz**. Backend Flask + Frontend HTML/CSS/JS estático.

## Stack

| Capa | Tecnología | Deploy |
|------|-----------|--------|
| Backend | Python / Flask | [Render](https://render.com) |
| Frontend | HTML + CSS + Vanilla JS | [Vercel](https://vercel.com) |
| Base de datos | JSON file (persistido en disco Render) | – |

---

## Estructura

```
Tenaz-gym/
├── backend/          # Flask API
├── frontend/         # HTML/CSS/JS estático
└── tests/            # pytest
```

---

## Setup local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # editar valores según entorno
python app.py
```

El servidor queda disponible en `http://localhost:5000`.

### Frontend

Sirve los archivos estáticos con cualquier servidor HTTP:

```bash
cd frontend
python -m http.server 8080
# Abrir http://localhost:8080/login.html
```

O instala `live-server`:

```bash
npx live-server frontend --port=8080
```

---

## Variables de entorno (backend)

| Variable | Descripción | Defecto |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Flask session | `dev-secret-key-...` |
| `ENABLE_AUTOLOGIN` | Login automático sin contraseña | `false` |
| `ALLOWED_ORIGIN` | Origen CORS permitido | `*` |
| `DATA_PATH` | Ruta al archivo JSON de datos | `gym_data.json` |
| `PORT` | Puerto del servidor | `5000` |
| `ADMIN_USERNAME` | Usuario administrador inicial | `admin` |
| `ADMIN_PASSWORD` | Contraseña administrador inicial | `gym123` |
| `UPLOAD_FOLDER` | Carpeta para fotos de miembros | `static/photos` |

---

## Deploy en Render (Backend)

1. Crear cuenta en [render.com](https://render.com).
2. Nuevo servicio **Web Service** → conectar repositorio.
3. El archivo `backend/render.yaml` configura el servicio automáticamente.
4. Configurar `ADMIN_PASSWORD` como variable de entorno secreta en el dashboard de Render.
5. El disco persistente `/var/data` almacena `gym_data.json`.

---

## Deploy en Vercel (Frontend)

1. Crear cuenta en [vercel.com](https://vercel.com).
2. Importar repositorio → seleccionar carpeta `frontend/` como raíz.
3. Agregar variable de entorno `NEXT_PUBLIC_API_URL` (o inyectar `window.API_URL` en un build step) apuntando a la URL del backend en Render.
4. El archivo `frontend/vercel.json` configura rewrites y headers de seguridad.

> **Nota:** Para que las cookies de sesión funcionen entre Vercel y Render, el backend tiene  
> `SESSION_COOKIE_SAMESITE=None` y `SESSION_COOKIE_SECURE=True`, y CORS está configurado con  
> `supports_credentials=True`.

---

## Algoritmo de fechas de corte

Las fechas de corte son el **8, 18 y 28** de cada mes.

Dado un `payment_date`:
1. Calcular `|payment_date.day − cut_day|` para cada corte.
2. Elegir el corte con menor diferencia. En empate, elegir el mayor.
3. Si el corte elegido ya pasó en el mes actual (`expiry < payment_date`), mover al mismo día del mes siguiente.

| Pago | Vencimiento |
|------|------------|
| 08/12/2025 | 08/12/2025 |
| 13/12/2025 | 18/12/2025 |
| 24/12/2025 | 28/12/2025 |
| 20/12/2025 | 18/01/2026 |

---

## Ejecutar tests

```bash
pip install -r backend/requirements.txt
python -m pytest tests/ -v
```

---

## Credenciales por defecto

- **Usuario:** `admin`
- **Contraseña:** `gym123`

> ⚠️ Cambiar la contraseña antes de hacer deploy en producción.
