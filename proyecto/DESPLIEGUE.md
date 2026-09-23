# TUNI — Documentacion de Despliegue

> Guia de arquitectura, servicios, y migracion a VM Proxmox (Windows) para el piloto de 12 semanas.

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

## 2. Tres servicios en ejecucion

| Servicio              | Tecnologia              | Puerto | Descripcion                                       |
| --------------------- | ----------------------- | ------ | ------------------------------------------------- |
| **Bot Telegram**      | python-telegram-bot 21  | —      | Long-polling, ConversationHandler, APScheduler     |
| **API Supervisor**    | FastAPI + Uvicorn       | 8001   | Endpoints de analisis, salud del piloto, consulta IA |
| **Dashboard**         | Next.js 15              | 3001   | Frontend del supervisor con graficas y chat IA     |

Servicio adicional cuando se usa modelo local:

| Servicio              | Tecnologia              | Puerto | Descripcion                                       |
| --------------------- | ----------------------- | ------ | ------------------------------------------------- |
| **Ollama**            | llama.cpp (Ollama)      | 11434  | Servidor de inferencia LLM local                   |

Dependencias externas (cloud):
- **Supabase** (PostgreSQL + Auth) — cloud, free tier

---

## 3. Variables de entorno (.env)

#### Modo cloud (Gemini)
```env
TELEGRAM_BOT_TOKEN=...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJ...
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
APP_ENV=production
DATA_DIR=data/students
```

#### Modo local (Ollama) — sin limites de tokens
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

> **Nota:** En modo `ollama`, el bot usa el modelo local para las conversaciones con estudiantes (sin limite). La consulta IA del dashboard (`POST /api/ai/query`) sigue usando Gemini porque necesita contexto largo (~4000+ tokens de datos del piloto) y el supervisor la usa esporadicamente.

El frontend usa `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://<IP_VM>:8001/api
```

---

## 4. Migracion a VM Proxmox

### 4.1 Escenarios de despliegue

El proyecto soporta dos proveedores LLM (variable `LLM_PROVIDER` en `.env`):

| Escenario | LLM_PROVIDER | Modelo | Ventaja | Desventaja |
|-----------|-------------|--------|---------|------------|
| **A: Cloud** | `gemini` | gemini-2.5-flash | VM barata, sin GPU | Limite de tokens gratis, latencia red, dependencia externa |
| **B: Local** | `ollama` | qwen3:8b / 14b | Sin limite de tokens, sin costo por uso, privacidad total | Requiere mas hardware, inferencia mas lenta en CPU |

---

### 4.2 Especificacion de la VM — Escenario B (modelo local, sin limites)

El cuello de botella es la inferencia LLM. Ollama usa llama.cpp que corre en CPU o GPU. Con ~60 estudiantes hay que considerar picos de concurrencia (5-15 alumnos simultaneos en hora de estudio).

#### Opcion 1: Solo CPU (sin GPU en el host Proxmox)

**Factor limitante:** La velocidad de generacion de tokens esta limitada por el ancho de banda de memoria, no por la cantidad de cores. Cada token requiere leer el modelo completo de RAM una vez:

```
tok/s ≈ ancho_de_banda_RAM / tamaño_del_modelo
```

| Tipo de RAM | Ancho de banda | qwen3:8b Q4 (5.5 GB) | qwen3:4b Q4 (3 GB) |
|-------------|---------------|----------------------|---------------------|
| DDR4-3200 single channel | ~25 GB/s | ~4 tok/s | ~8 tok/s |
| DDR4-3200 dual channel | ~50 GB/s | ~9 tok/s | ~16 tok/s |
| DDR5-4800 dual channel | ~77 GB/s | ~14 tok/s | ~25 tok/s |
| DDR5-5600 dual channel | ~90 GB/s | ~16 tok/s | ~30 tok/s |

> **Critico:** Verificar que la RAM del host Proxmox esta en **dual channel** (2 DIMMs minimo, uno por canal). Single channel reduce el rendimiento a la mitad.

**Que mejora con mas cores y RAM:**

| Recurso extra | Efecto real |
|---------------|-------------|
| Mas cores (8→16) | Prefill mas rapido (procesar prompt inicial), no sube el techo de tok/s |
| Mas RAM (24→48 GB) | Permite `OLLAMA_NUM_PARALLEL=4-6`, cada slot paralelo consume ~2 GB extra de KV cache |
| RAM mas rapida / dual channel | Sube directamente el techo de tok/s — **la mejora mas impactante** |

**Specs recomendadas (CPU-only, maximizando concurrencia):**

| Recurso      | Agresivo (mejor UX)  | Moderado            | Minimo             |
| ------------ | -------------------- | ------------------- | ------------------ |
| **CPU**      | 16 vCPUs             | 12 vCPUs            | 8 vCPUs            |
| **RAM**      | 48 GB                | 32 GB               | 24 GB              |
| **Disco**    | 120 GB SSD/NVMe      | 120 GB SSD          | 80 GB SSD          |
| **Modelo**   | qwen3:8b Q4_K_M      | qwen3:8b Q4_K_M     | qwen3:4b Q4_K_M    |
| **Parallel** | `OLLAMA_NUM_PARALLEL=6` | `OLLAMA_NUM_PARALLEL=4` | `OLLAMA_NUM_PARALLEL=2` |
| **Red**      | VirtIO bridge        | VirtIO bridge       | VirtIO bridge      |
| **SO**       | Windows 11 Pro       | Windows 11 Pro      | Windows 10         |

**Rendimiento esperado (DDR4-3200 dual channel, ~50 GB/s):**

| Config | Modelo | tok/s por usuario | Usuarios simultaneos | Espera en cola (5 concurrentes) |
|--------|--------|-------------------|---------------------|--------------------------------|
| 16 cores / 48 GB | qwen3:8b | ~9 tok/s | 6 simultaneos | ~0-10 seg |
| 12 cores / 32 GB | qwen3:8b | ~9 tok/s | 4 simultaneos | ~15-30 seg |
| 8 cores / 24 GB | qwen3:8b | ~9 tok/s | 2 simultaneos | ~30-60 seg |
| 8 cores / 24 GB | qwen3:4b | ~16 tok/s | 3 simultaneos | ~10-20 seg |

> **Nota:** El tok/s por usuario no cambia con mas cores (techo de ancho de banda), pero mas RAM permite mas slots paralelos que reducen la espera en cola. Con 48 GB y `NUM_PARALLEL=6`, el bot puede generar 6 respuestas simultaneas a ~9 tok/s cada una. Eso cubre picos normales de 60 estudiantes.

**Estrategia alternativa — modelo mas pequeno:**

Si el hardware disponible es limitado (8 cores, 24 GB), usar `qwen3:4b` en vez de `8b` duplica la velocidad por usuario y permite mas concurrencia. La calidad baja un poco en razonamiento matematico complejo, pero sigue siendo funcional para tutoria basica. Se puede probar ambos y decidir segun la experiencia.

```env
# Cambiar modelo en .env
OLLAMA_MODEL=qwen3:4b
```

#### Opcion 2: GPU passthrough (recomendado para produccion)

| Recurso      | Recomendado           | Minimo               | Nota                                          |
| ------------ | --------------------- | -------------------- | --------------------------------------------- |
| **CPU**      | 6 vCPUs               | 4 vCPUs              | 1 socket. Tipo: `host`.                       |
| **RAM**      | 16 GB                 | 12 GB                | Modelo en VRAM, no en RAM del sistema         |
| **GPU**      | RTX 3060 12GB         | GTX 1660 Super 6GB   | PCIe passthrough desde el host Proxmox        |
| **VRAM**     | 12 GB                 | 6 GB                 | qwen3:8b Q4 cabe en 6 GB, 14b necesita 10 GB |
| **Disco**    | 120 GB (SSD/NVMe)     | 80 GB                |                                               |
| **Red**      | VirtIO bridge         | —                    |                                               |
| **SO**       | Windows 11 Pro        | Windows 10           | + NVIDIA drivers en la VM                     |

Rendimiento esperado con GPU:

| Modelo | VRAM requerida | Velocidad | Concurrencia practica |
|--------|---------------|-----------|----------------------|
| qwen3:4b | ~3 GB | ~60-90 tok/s | 8-10 usuarios |
| **qwen3:8b** | ~5.5 GB | ~35-55 tok/s | 5-8 usuarios |
| qwen3:14b | ~9.5 GB | ~20-35 tok/s | 3-5 usuarios |
| qwen3:32b | ~20 GB | necesita 2x GPU | 2-3 usuarios |

> Con una RTX 3060 12GB corriendo qwen3:8b a ~40 tok/s, atiende cómodamente 5-8 usuarios simultaneos. Mas que suficiente para el piloto.

#### Modelo recomendado

**qwen3:8b** es el sweet spot para este proyecto:
- Excelente razonamiento matematico (algebra, calculo, discretas)
- Buen espanol nativo (no es traduccion)
- Modo thinking activable para problemas complejos
- Cabe en 6 GB VRAM o 8 GB RAM
- Ya esta configurado en el proyecto (`OLLAMA_MODEL=qwen3:8b`)

Si el host tiene 12+ GB VRAM, **qwen3:14b** mejora notablemente la calidad de tutoria Socratica a costa de velocidad.

---

### 4.3 Configuracion Proxmox

#### VM base (aplica a ambas opciones)

```
General:
  VM ID:    libre
  Name:     tuni-pilot

OS:
  ISO:      Win11_xxxx.iso
  Type:     Microsoft Windows
  Version:  11/2025

System:
  Machine:  q35
  BIOS:     OVMF (UEFI)
  TPM:      Agregar TPM v2.0 (requerido para Win11)
  SCSI:     VirtIO SCSI single

Disks:
  scsi0:    120 GB, cache=writeback, SSD emulation=on, discard=on

Network:
  net0:     VirtIO bridge=vmbr0
```

#### CPU-only (recomendado sin GPU)

```
CPU:
  Sockets:  1
  Cores:    12-16       # Mas cores = prefill mas rapido + mejor multitarea
  Type:     host        # IMPORTANTE: tipo "host" expone AVX2/AVX-512 que llama.cpp necesita

Memory:
  RAM:      32768 MB (32 GB)   # o 49152 MB (48 GB) si se busca NUM_PARALLEL=6
  Ballooning: desactivado
```

#### Con GPU passthrough

```
CPU:
  Sockets:  1
  Cores:    6
  Type:     host

Memory:
  RAM:      16384 MB (16 GB)
  Ballooning: desactivado

PCI Device:
  Device:   <GPU PCI address> (ej: 0000:01:00.0)
  All Functions: si
  ROM-Bar:  si
  PCI-Express: si
```

Pasos para habilitar GPU passthrough en Proxmox:
1. Editar GRUB: `GRUB_CMDLINE_LINUX_DEFAULT="quiet intel_iommu=on iommu=pt"` (o `amd_iommu=on` para AMD)
2. Agregar a `/etc/modules`: `vfio vfio_iommu_type1 vfio_pci vfio_virqfd`
3. Blacklist el driver nativo: `echo "blacklist nouveau" >> /etc/modprobe.d/blacklist.conf`
4. Identificar PCI ID: `lspci -nn | grep NVIDIA`
5. Vincular a vfio: `echo "options vfio-pci ids=XXXX:XXXX" >> /etc/modprobe.d/vfio.conf`
6. `update-initramfs -u && reboot`
7. Agregar el PCI device en la config de la VM (ver arriba)
8. En la VM Windows: instalar NVIDIA drivers normalmente

> **Nota sobre drivers:** Descargar tambien los VirtIO drivers para Windows (`virtio-win.iso`) y montarlos durante la instalacion de Windows para que detecte el disco y la red.

---

### 4.4 Estimacion de costos de hardware

Si no tienes GPU disponible y necesitas comprar:

| GPU | VRAM | Precio aprox. (USD) | Modelo maximo | Nota |
|-----|------|---------------------|---------------|------|
| GTX 1660 Super | 6 GB | $100-130 (usada) | qwen3:8b Q4 | Minimo viable, ajustado |
| **RTX 3060** | **12 GB** | **$180-220 (usada)** | **qwen3:14b Q4** | **Mejor relacion costo/beneficio** |
| RTX 3090 | 24 GB | $550-700 (usada) | qwen3:32b Q4 | Overkill para este piloto |
| RTX 4060 Ti | 16 GB | $350-400 (nueva) | qwen3:14b Q5 | Mas eficiente energeticamente |

Para el piloto de 12 semanas con 60 estudiantes, una **RTX 3060 12GB usada** es la recomendacion.

### 4.5 Pasos de migracion

#### Fase 1 — Preparar la VM

1. Crear la VM en Proxmox con las specs de la seccion 4.3
2. Instalar Windows 11 con drivers VirtIO
3. Si hay GPU: instalar NVIDIA drivers en Windows
4. Instalar software base:
   - Python 3.11+ (marcar "Add to PATH")
   - Node.js 20 LTS
   - Git for Windows
   - Ollama para Windows (https://ollama.com/download/windows)
5. Configurar IP fija o reserva DHCP

#### Fase 2 — Instalar Ollama y el modelo

```powershell
# Ollama se instala como servicio de Windows automaticamente
# Verificar que esta corriendo:
curl http://localhost:11434/api/version

# Descargar el modelo (una sola vez, ~5 GB)
ollama pull qwen3:8b

# Probar que funciona:
ollama run qwen3:8b "Hola, resuelve x^2 - 4 = 0"

# Verificar que corre en GPU (si hay):
ollama ps
# La columna PROCESSOR debe mostrar "GPU" no "CPU"
```

Configuracion de Ollama para concurrencia (crear variables de entorno del sistema en Windows):
```
OLLAMA_NUM_PARALLEL=4        # Peticiones simultaneas (default: 1)
                             # Cada slot extra consume ~2 GB RAM de KV cache
                             # 32 GB RAM → 4 slots, 48 GB → 6 slots
OLLAMA_MAX_LOADED_MODELS=1   # Modelos en memoria (1 es suficiente)
OLLAMA_KEEP_ALIVE=24h        # Mantener modelo cargado (evita recarga de 5-10 seg)
OLLAMA_FLASH_ATTENTION=1     # Flash Attention — reduce uso de RAM y acelera prefill
```

> Despues de cambiar variables de Ollama, reiniciar el servicio: `net stop ollama && net start ollama`

#### Fase 3 — Transferir el proyecto

```powershell
git clone <repo-url> C:\tuni\TUNI
cd C:\tuni\TUNI\proyecto\tuni-bot

# Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Frontend supervisor
cd frontend-supervisor
npm install
npm run build
cd ..
```

#### Fase 4 — Configurar entorno

```powershell
copy .env.example .env
notepad .env
```

Configurar `.env` para modelo local:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Crear `frontend-supervisor\.env.local`:
```
NEXT_PUBLIC_API_URL=http://<IP_VM>:8001/api
```

#### Fase 5 — Ejecutar los servicios

Ollama ya corre como servicio de Windows. Los demas tres servicios:

Opcion A — **Tres terminales PowerShell** (desarrollo/pruebas):

```powershell
# Terminal 1: Bot
cd C:\tuni\TUNI\proyecto\tuni-bot
venv\Scripts\python run_bot.py

# Terminal 2: API
cd C:\tuni\TUNI\proyecto\tuni-bot
venv\Scripts\python run_api.py

# Terminal 3: Dashboard
cd C:\tuni\TUNI\proyecto\tuni-bot\frontend-supervisor
npm run start
```

Opcion B — **Servicios de Windows con NSSM** (recomendado para produccion):

```powershell
# Descargar NSSM: https://nssm.cc/download
mkdir C:\tuni\logs

nssm install tuni-bot "C:\tuni\TUNI\proyecto\tuni-bot\venv\Scripts\python.exe" "run_bot.py"
nssm set tuni-bot AppDirectory "C:\tuni\TUNI\proyecto\tuni-bot"
nssm set tuni-bot AppStdout "C:\tuni\logs\bot.log"
nssm set tuni-bot AppStderr "C:\tuni\logs\bot-error.log"

nssm install tuni-api "C:\tuni\TUNI\proyecto\tuni-bot\venv\Scripts\python.exe" "run_api.py"
nssm set tuni-api AppDirectory "C:\tuni\TUNI\proyecto\tuni-bot"
nssm set tuni-api AppStdout "C:\tuni\logs\api.log"
nssm set tuni-api AppStderr "C:\tuni\logs\api-error.log"

nssm install tuni-dashboard "C:\Program Files\nodejs\node.exe" "node_modules\.bin\next" "start" "--port" "3001"
nssm set tuni-dashboard AppDirectory "C:\tuni\TUNI\proyecto\tuni-bot\frontend-supervisor"
nssm set tuni-dashboard AppStdout "C:\tuni\logs\dashboard.log"
nssm set tuni-dashboard AppStderr "C:\tuni\logs\dashboard-error.log"

nssm start tuni-bot
nssm start tuni-api
nssm start tuni-dashboard
```

Los 4 servicios (Ollama + bot + api + dashboard) se inician automaticamente con Windows.

#### Fase 6 — Firewall y acceso

```powershell
netsh advfirewall firewall add rule name="TUNI API" dir=in action=allow protocol=tcp localport=8001
netsh advfirewall firewall add rule name="TUNI Dashboard" dir=in action=allow protocol=tcp localport=3001
```

Dashboard accesible en `http://<IP_VM>:3001`.

#### Fase 7 — Verificacion

- [ ] `ollama ps` muestra qwen3:8b cargado en GPU/CPU
- [ ] `http://localhost:11434/api/version` responde (Ollama activo)
- [ ] `http://<IP_VM>:8001/api/health` retorna `{"status": "ok"}`
- [ ] `http://<IP_VM>:8001/api/pilot-health` retorna metricas
- [ ] `http://<IP_VM>:3001` muestra el dashboard
- [ ] `/start` en Telegram completa onboarding
- [ ] Enviar un mensaje y verificar que la respuesta viene de Ollama (ver logs del bot)
- [ ] `data/students/` genera archivos JSON

---

## 5. Monitoreo y mantenimiento

### Logs
- Bot: `C:\tuni\logs\bot.log`
- API: `C:\tuni\logs\api.log`
- Dashboard: `C:\tuni\logs\dashboard.log`

### Datos locales
- Estudiantes: `data/students/{telegram_id}.json`
- Conversaciones: `data/conversations/{session_id}.json`
- Cronogramas: `data/cronogramas/*.yaml`

### Backups
Configurar tarea programada en Windows para copiar `data/` periodicamente:
```powershell
# Ejemplo: backup diario a las 3 AM
schtasks /create /tn "TUNI Backup" /tr "robocopy C:\tuni\TUNI\proyecto\tuni-bot\data C:\tuni\backups\%date:~-4,4%%date:~-7,2%%date:~-10,2% /MIR" /sc daily /st 03:00
```

### Actualizaciones
```powershell
cd C:\tuni\TUNI
git pull
cd proyecto\tuni-bot
venv\Scripts\pip install -r requirements.txt
nssm restart tuni-bot
nssm restart tuni-api
```

---

## 6. Endpoints del API supervisor

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
