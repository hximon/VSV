# Architecture Overview

## System Architecture

### Vercel Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         VERCEL CLOUD                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌─────────────────────┐          │
│  │   CDN Edge   │────────▶│  Serverless         │          │
│  │   Network    │         │  Function Instance  │          │
│  └──────────────┘         └─────────────────────┘          │
│                                     │                        │
│                                     ▼                        │
│                          ┌─────────────────────┐            │
│                          │  api/index.py       │            │
│                          │  (Flask App)        │            │
│                          └─────────────────────┘            │
│                                     │                        │
│                          ┌──────────┴──────────┐            │
│                          │                     │            │
│                    ┌─────▼─────┐        ┌─────▼─────┐      │
│                    │ templates/│        │  static/  │      │
│                    │ index.html│        │ style.css │      │
│                    └───────────┘        └───────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   User Browser   │
                    │  (Dashboard UI)  │
                    └──────────────────┘
```

### Docker Deployment Architecture (Original)

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER CONTAINER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                  start.sh                          │    │
│  │  (Entry Point - Starts all services)              │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                    │
│           ┌─────────────┴────────────┐                      │
│           │                          │                      │
│     ┌─────▼──────┐          ┌───────▼────────┐            │
│     │  tmate.sh  │          │    app.py      │            │
│     │  (SSH)     │          │  (Flask App)   │            │
│     └────────────┘          └────────────────┘            │
│           │                          │                      │
│           │                          │                      │
│     ┌─────▼──────┐          ┌───────▼────────┐            │
│     │ tmate      │          │   Gunicorn     │            │
│     │ Session    │          │   (WSGI)       │            │
│     └────────────┘          └────────────────┘            │
│                                      │                      │
│                           ┌──────────┴──────────┐          │
│                           │                     │          │
│                     ┌─────▼─────┐        ┌─────▼─────┐    │
│                     │ templates/│        │  static/  │    │
│                     │ index.html│        │ style.css │    │
│                     └───────────┘        └───────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              │                          │
              │                          │
    ┌─────────▼────────┐      ┌─────────▼──────────┐
    │  SSH Terminal    │      │   Web Browser      │
    │  (tmate client)  │      │  (Dashboard UI)    │
    └──────────────────┘      └────────────────────┘
```

## File Flow

### Vercel Request Flow

```
User Request
    │
    ▼
Vercel Edge CDN
    │
    ├─── /static/* ───────▶ Static Files (CSS)
    │
    ├─── / ───────────────▶ api/index.py → render_template('index.html')
    │
    ├─── /status ─────────▶ api/index.py → get_server_status() → JSON
    │
    └─── /regenerate ─────▶ api/index.py → Error (SSH not available)
```

### Docker Request Flow

```
User Request
    │
    ▼
Gunicorn (WSGI)
    │
    ▼
app.py (Flask)
    │
    ├─── /static/* ───────▶ Static Files (CSS)
    │
    ├─── / ───────────────▶ render_template('index.html')
    │
    ├─── /status ─────────▶ get_server_status() → JSON
    │
    └─── /regenerate ─────▶ subprocess.Popen(['bash', 'tmate.sh'])
                                    │
                                    ▼
                            Restart tmate session
                                    │
                                    ▼
                            Update ssh_url.txt
```

## Component Responsibilities

### Vercel Components

| Component | Responsibility |
|-----------|---------------|
| `vercel.json` | Deployment configuration, routes, environment |
| `api/index.py` | Main Flask application for serverless |
| `templates/index.html` | Frontend dashboard UI |
| `static/style.css` | Styling and design |
| `.vercelignore` | Files to exclude from deployment |

### Docker Components

| Component | Responsibility |
|-----------|---------------|
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container orchestration |
| `start.sh` | Entry point, installs tmate and starts services |
| `tmate.sh` | Creates tmate session, saves SSH URL |
| `app.py` | Main Flask application |
| `requirements.txt` | Python dependencies |

## Data Flow - System Monitoring

```
┌─────────────────┐
│  psutil Library │  (Reads system stats)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  get_server_status() function   │
│  - CPU: psutil.cpu_percent()   │
│  - Memory: psutil.virtual_memory()
│  - Disk: psutil.disk_usage()   │
│  - Network: psutil.net_io_counters()
│  - Uptime: psutil.boot_time()  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  JSON Response  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Browser (JS)   │  (Fetches every 3 seconds)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update UI      │
│  - Progress bars│
│  - Text values  │
│  - SSH URL      │
└─────────────────┘
```

## Deployment Workflows

### Vercel Deployment Workflow

```
Local Changes
    │
    ├─── git add .
    ├─── git commit
    └─── git push
         │
         ▼
    GitHub Repository
         │
         │ (Webhook trigger)
         ▼
    Vercel Build System
         │
         ├─── Install Python dependencies (requirements.txt)
         ├─── Build serverless function (api/index.py)
         ├─── Copy static files
         └─── Deploy to Edge Network
              │
              ▼
         Live on Vercel
         (https://your-project.vercel.app)
```

### Docker Deployment Workflow

```
Local Changes
    │
    ├─── git add .
    ├─── git commit
    └─── git push
         │
         ▼
    GitHub Repository
         │
         │ (Webhook trigger)
         ▼
    Platform Build System (Railway/Render)
         │
         ├─── docker build
         ├─── Install system packages (Dockerfile)
         ├─── Copy application files
         └─── docker run
              │
              ├─── Execute start.sh
              ├─── Download & setup tmate
              ├─── Start tmate session
              ├─── Create virtual environment
              ├─── Install Python dependencies
              └─── Start Gunicorn
                   │
                   ▼
              Live on Platform
              (Web + SSH access)
```

## Technology Stack

### Vercel Stack
```
Frontend:
├── HTML5
├── CSS3
├── JavaScript (ES6+)
└── Fetch API

Backend:
├── Python 3.x
├── Flask 2.2.3
├── psutil 5.9.4
├── requests 2.28.1
└── Werkzeug 2.2.3

Infrastructure:
├── Vercel Serverless Functions
├── Vercel Edge Network (CDN)
└── Auto-scaling
```

### Docker Stack
```
Frontend:
├── HTML5
├── CSS3
├── JavaScript (ES6+)
└── Fetch API

Backend:
├── Python 3.x
├── Flask 2.2.3
├── Gunicorn 20.1.0
├── psutil 5.9.4
└── requests 2.28.1

System:
├── Ubuntu 20.04
├── tmate 2.4.0
├── OpenSSH Server
└── System utilities

Infrastructure:
├── Docker Container
├── Volume mounting
└── Port mapping
```

## Performance Characteristics

### Vercel
```
Cold Start: ~1-3 seconds
Warm Response: ~50-200ms
Timeout: 10s (Hobby), 60s (Pro)
Scaling: Automatic & instant
Global: Yes (Edge network)
```

### Docker (Railway/Render)
```
Cold Start: ~30-60 seconds
Warm Response: ~100-300ms
Timeout: None (persistent)
Scaling: Manual/Auto (plan dependent)
Global: Single region
```

---

**This architecture supports both deployment models while maintaining code compatibility!**
