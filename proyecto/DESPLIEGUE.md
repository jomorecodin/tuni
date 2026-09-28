# TUNI — Documentacion de Despliegue

> Guia de arquitectura, servicios, y migracion a CT Proxmox (Ubuntu LXC) para el piloto de 12 semanas.

---

## 1. Arquitectura del proyecto

```
tuni-bot/
├── run_bot.py                  # Punto de entrada del bot Telegram
├── run_api.py                  # Punto de entrada del API supervisor (FastAPI)
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (no versionado)
│
├── app/
│   ├── core/config.py          # Pydantic Settings (lee .env)
│   ├── db/client.py            # Singleton Supabase client
│   ├── services/
│   │   ├── llm_client.py       # Abstraccion Gemini/Ollama streaming
│   │   └── prompt_loader.py    # Construccion de system prompts
│   ├── bot/
│   │   ├── main.py             # Telegram ConversationHandler + scheduler
│   │   ├── constants.py        # Estados, strings UI, carreras
│   │   ├── keyboards.py        # Teclados inline
│   │   ├── handlers/           # start, chat, commands, class_checkin, reflection, etc.
│   │   └── services/           # session_manager, student_tracker, cronograma, scheduler,
│   │                           # analysis_engine, intent_detector, latex_renderer, streaming
│   └── api/
│       ├── server.py           # FastAPI app (CORS, startup, routers)
│       └── routes/             # health, analysis, ai_query
│
├── frontend-supervisor/        # Next.js 15 + React 19 + TailwindCSS v4 + Recharts
│   ├── app/                    # Paginas: /, /gaps, /students, /ai
│   ├── components/             # Sidebar, StatsCard
│   └── lib/api.ts              # Cliente HTTP tipado para la API
│
├── data/
│   ├── students/               # JSON por estudiante ({telegram_id}.json)
│   ├── conversations/          # JSON por sesion ({session_id}.json)
│   └── cronogramas/            # YAML por materia (15 archivos)
│
├── context/                    # Contexto curricular por materia (.md)
│   └── ingenieria_de_sistemas/
│       ├── trimestre_3/ (5 materias)
│       ├── trimestre_4/ (5 materias)
│       └── trimestre_5/ (5 materias)
│
├── prompts/                    # System prompts del LLM
│   ├── modo_tutor.md           # Modo Socratico
│   └── modo_general.md         # Modo consulta general
│
├── migrations/                 # SQL (Supabase)
│   ├── 003_telegram_support.sql
│   ├── 004_curriculum_subjects.sql
│   └── 005_reflection_and_cronograma.sql
│
└── supabase/                   # Supabase CLI config + migrations
```

---

## 2. Servicios en ejecucion

| Servicio              | Tecnologia              | Puerto | Descripcion                                       |
| --------------------- | ----------------------- | ------ | ------------------------------------------------- |
| **Bot Telegram**      | python-telegram-bot 21  | —      | Long-polling, ConversationHandler, APScheduler     |
| **API Supervisor**    | FastAPI + Uvicorn       | 8001   | Endpoints de analisis, salud del piloto, consulta IA |
| **Dashboard**         | Next.js 15              | 3001   | Frontend del supervisor con graficas y chat IA     |
| **Ollama**            | llama.cpp (Ollama)      | 11434  | Servidor de inferencia LLM local                   |

Dependencias externas (cloud):
- **Supabase** (PostgreSQL + Auth) — cloud, free tier

---

## 3. Variables de entorno (.env)

```env
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
GEMINI_API_KEY=...               # Se mantiene para consultas IA del supervisor
GEMINI_MODEL=gemini-2.5-flash    # El dashboard AI query sigue usando Gemini
APP_ENV=production
DATA_DIR=data/students
```

> **Nota:** El bot usa Ollama para conversaciones con estudiantes (sin limite de tokens). La consulta IA del dashboard (`POST /api/ai/query`) sigue usando Gemini porque el supervisor la usa esporadicamente.

Frontend `frontend-supervisor/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://<IP_CT>:8001/api
```

---

## 4. Configuracion del CT en Proxmox

### 4.1 Crear el contenedor LXC

Desde la interfaz web de Proxmox (`https://<IP_HOST>:8006`):

```
General:
  CT ID:      libre (ej: 100)
  Hostname:   tuni-pilot
  Password:   <password root del CT>
  Unprivileged: Si

Template:
  Storage:    local
  Template:   ubuntu-22.04-standard_22.04-1_amd64.tar.zst
              (descargar desde: Datacenter → Storage → CT Templates → Templates)

Disks:
  rootfs:     120 GB, storage donde tengas espacio

CPU:
  Cores:      12        # Tipo host se hereda automaticamente en LXC

Memory:
  RAM:        32768 MB (32 GB)
  Swap:       4096 MB

Network:
  net0:       name=eth0, bridge=vmbr0, ip=dhcp
              (o IP fija: ip=192.168.x.x/24, gw=192.168.x.1)

DNS:
  Usar configuracion del host
```

### 4.2 Performance esperado (CPU-only, DDR4-3200 dual channel)

| Config | Modelo | tok/s por usuario | Usuarios simultaneos | Espera en cola (5 concurrentes) |
|--------|--------|-------------------|---------------------|--------------------------------|
| 12 cores / 32 GB | qwen3:8b | ~9 tok/s | 5 simultaneos | ~10-20 seg |

> **Ventaja del CT vs VM:** ~31 GB disponibles para Ollama (vs ~28 GB en VM con Windows). Esto permite `OLLAMA_NUM_PARALLEL=5` en vez de 4.

> **Critico:** Verificar que la RAM del host Proxmox esta en **dual channel** (2 DIMMs minimo). Single channel reduce el rendimiento a la mitad.

---

## 5. Instalacion paso a paso

### Paso 1 — Entrar al CT y actualizar

```bash
# Desde Proxmox, abrir la consola del CT, o por SSH:
ssh root@<IP_CT>

apt update && apt upgrade -y
```

### Paso 2 — Instalar dependencias del sistema

```bash
apt install -y python3 python3-pip python3-venv git curl unzip
```

### Paso 3 — Instalar Node.js 20 LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
node --version   # debe mostrar v20.x
```

### Paso 4 — Instalar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh

# Verificar que esta corriendo
systemctl status ollama
curl http://localhost:11434/api/version
```

### Paso 5 — Descargar el modelo

```bash
ollama pull qwen3:8b
# ~5 GB de descarga, una sola vez

# Probar que funciona
ollama run qwen3:8b "Hola, resuelve x^2 - 4 = 0"
```

### Paso 6 — Configurar Ollama para concurrencia

```bash
# Editar el servicio de Ollama
systemctl edit ollama

# Agregar estas lineas entre los comentarios:
[Service]
Environment="OLLAMA_NUM_PARALLEL=5"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_FLASH_ATTENTION=1"

# Guardar, salir, y reiniciar
systemctl daemon-reload
systemctl restart ollama
```

### Paso 7 — Transferir el proyecto

**Opcion A — Desde zip (si no hay acceso git):**

```bash
# Desde tu maquina local, comprimir tuni-bot/ (sin venv ni node_modules):
# Subir el zip al CT via SCP:
scp tuni-bot.zip root@<IP_CT>:/opt/

# En el CT:
cd /opt
unzip tuni-bot.zip
```

**Opcion B — Clonar el repo:**

```bash
cd /opt
git clone <repo-url> tuni
cd tuni/proyecto/tuni-bot
```

### Paso 8 — Crear el entorno Python

```bash
cd /opt/tuni-bot    # o /opt/tuni/proyecto/tuni-bot si clonaste
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Paso 9 — Instalar dependencias del frontend

```bash
cd frontend-supervisor
npm install
npm run build
cd ..
```

### Paso 10 — Crear el .env

```bash
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=tu_token_aqui
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxx
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
GEMINI_API_KEY=tu_gemini_key
GEMINI_MODEL=gemini-2.5-flash
APP_ENV=production
DATA_DIR=data/students
EOF
```

```bash
cat > frontend-supervisor/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://<IP_CT>:8001/api
EOF
```

### Paso 11 — Crear servicios systemd

**Bot Telegram:**
```bash
cat > /etc/systemd/system/tuni-bot.service << 'EOF'
[Unit]
Description=TUNI Telegram Bot
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tuni-bot
ExecStart=/opt/tuni-bot/venv/bin/python run_bot.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/tuni/bot.log
StandardError=append:/var/log/tuni/bot-error.log

[Install]
WantedBy=multi-user.target
EOF
```

**API Supervisor:**
```bash
cat > /etc/systemd/system/tuni-api.service << 'EOF'
[Unit]
Description=TUNI Supervisor API
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tuni-bot
ExecStart=/opt/tuni-bot/venv/bin/python run_api.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/tuni/api.log
StandardError=append:/var/log/tuni/api-error.log

[Install]
WantedBy=multi-user.target
EOF
```

**Dashboard:**
```bash
cat > /etc/systemd/system/tuni-dashboard.service << 'EOF'
[Unit]
Description=TUNI Supervisor Dashboard
After=network.target tuni-api.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tuni-bot/frontend-supervisor
ExecStart=/usr/bin/npx next start --port 3001
Restart=always
RestartSec=5
StandardOutput=append:/var/log/tuni/dashboard.log
StandardError=append:/var/log/tuni/dashboard-error.log

[Install]
WantedBy=multi-user.target
EOF
```

**Activar todo:**
```bash
mkdir -p /var/log/tuni

systemctl daemon-reload
systemctl enable tuni-bot tuni-api tuni-dashboard
systemctl start tuni-bot tuni-api tuni-dashboard
```

### Paso 12 — Verificar

```bash
# Estado de los servicios
systemctl status ollama tuni-bot tuni-api tuni-dashboard

# Logs en tiempo real
journalctl -u tuni-bot -f          # Ctrl+C para salir
tail -f /var/log/tuni/bot.log

# Endpoints
curl http://localhost:11434/api/version          # Ollama
curl http://localhost:8001/api/health             # API
curl http://localhost:8001/api/pilot-health       # Metricas

# Desde fuera del CT
# http://<IP_CT>:8001/api/health
# http://<IP_CT>:3001
# /start en Telegram
```

---

## 6. Operacion manual (sin systemd, para pruebas)

Si prefieres correr todo en terminales separadas (tmux o varias sesiones SSH):

```bash
# Terminal 1 — Bot
cd /opt/tuni-bot && source venv/bin/activate && python run_bot.py

# Terminal 2 — API
cd /opt/tuni-bot && source venv/bin/activate && python run_api.py

# Terminal 3 — Dashboard
cd /opt/tuni-bot/frontend-supervisor && npx next start --port 3001
```

**Tip:** Usar `tmux` para que las sesiones sobrevivan al cerrar SSH:
```bash
apt install -y tmux
tmux new -s tuni

# Dentro de tmux:
# Ctrl+B, C = nueva ventana
# Ctrl+B, N = siguiente ventana
# Ctrl+B, D = detach (dejar corriendo en background)
# tmux attach -t tuni = reconectar
```

---

## 7. Monitoreo y mantenimiento

### Logs
```bash
tail -f /var/log/tuni/bot.log           # Bot
tail -f /var/log/tuni/api.log           # API
tail -f /var/log/tuni/dashboard.log     # Dashboard
journalctl -u ollama -f                 # Ollama
```

### Reiniciar servicios
```bash
systemctl restart tuni-bot
systemctl restart tuni-api
systemctl restart tuni-dashboard
systemctl restart ollama
```

### Datos locales
```
data/students/{telegram_id}.json         # Un archivo por estudiante
data/conversations/{session_id}.json     # Un archivo por sesion
data/cronogramas/*.yaml                  # 15 archivos de cronogramas
```

### Backups automaticos (cron)
```bash
# Backup diario a las 3 AM
crontab -e

# Agregar esta linea:
0 3 * * * tar czf /opt/backups/tuni-data-$(date +\%Y\%m\%d).tar.gz /opt/tuni-bot/data/
```

```bash
mkdir -p /opt/backups
```

### Actualizar el proyecto
```bash
cd /opt/tuni-bot
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart tuni-bot tuni-api
```

---

## 8. Endpoints del API supervisor

| Metodo | Ruta                            | Descripcion                              |
| ------ | ------------------------------- | ---------------------------------------- |
| GET    | `/api/health`                   | Health check basico                      |
| GET    | `/api/pilot-health`             | Metricas en tiempo real del piloto       |
| GET    | `/api/analysis/weekly-report`   | Reporte semanal de brechas (?weeks=N)    |
| GET    | `/api/analysis/gaps/{materia}`  | Analisis profundo por materia            |
| GET    | `/api/analysis/students`        | Resumen de todos los estudiantes         |
| GET    | `/api/analysis/subjects`        | Lista de materias con cronograma         |
| POST   | `/api/ai/query`                 | Consulta IA sobre datos del piloto       |

### Ejemplo: Consulta IA
```bash
curl -X POST http://localhost:8001/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Cuales son las brechas mas criticas detectadas?"}'
```

---

## 9. Rendimiento y tuning

### Factor limitante: ancho de banda de RAM

```
tok/s ≈ ancho_de_banda_RAM / tamaño_del_modelo
```

| Tipo de RAM | Ancho de banda | qwen3:8b Q4 (5.5 GB) | qwen3:4b Q4 (3 GB) |
|-------------|---------------|----------------------|---------------------|
| DDR4-3200 single channel | ~25 GB/s | ~4 tok/s | ~8 tok/s |
| DDR4-3200 dual channel | ~50 GB/s | ~9 tok/s | ~16 tok/s |
| DDR5-4800 dual channel | ~77 GB/s | ~14 tok/s | ~25 tok/s |

### Que mejora con mas recursos

| Recurso extra | Efecto real |
|---------------|-------------|
| Mas cores (8→16) | Prefill mas rapido (procesar prompt inicial), no sube el techo de tok/s |
| Mas RAM (24→48 GB) | Permite `OLLAMA_NUM_PARALLEL=5-6`, cada slot consume ~2 GB extra de KV cache |
| RAM mas rapida / dual channel | Sube directamente el techo de tok/s — **la mejora mas impactante** |

### Modelo alternativo si el hardware es limitado

Si el rendimiento con qwen3:8b no es suficiente, cambiar a qwen3:4b:
```bash
ollama pull qwen3:4b
# Editar .env: OLLAMA_MODEL=qwen3:4b
systemctl restart tuni-bot
```

Duplica la velocidad por usuario. La calidad baja un poco en razonamiento matematico complejo pero sigue siendo funcional.
