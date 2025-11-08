# 🔄 Simple Docker Load Balancer

A lightweight, production-ready load balancer implementation using **NGINX** and **Docker Compose**. This project demonstrates horizontal scaling with multiple Python Flask backend servers behind an NGINX reverse proxy.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![NGINX](https://img.shields.io/badge/NGINX-009639?style=flat&logo=nginx&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Testing](#-testing)
- [Monitoring](#-monitoring)
- [Scaling](#-scaling)
- [Troubleshooting](#-troubleshooting)

## ✨ Features

- **Load Balancing**: Distributes incoming requests across 4 Python Flask servers
- **Health Checks**: Automatic failure detection and failover with configurable timeouts
- **Real-time Monitoring**: Live RPS (Requests Per Second) tracking and visualization
- **Horizontal Scaling**: Easy to add or remove backend servers
- **Containerized**: Fully containerized with Docker for easy deployment
- **Stress Testing**: Built-in load testing tool to validate performance
- **Server-Sent Events**: Real-time streaming of performance metrics

## 🏗 Architecture

```
                    ┌─────────────────┐
                    │   NGINX (Port   │
                    │      80)        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼────────┐ ┌──▼──────────┐ ┌─▼─────────────┐
    │ Python Server 1  │ │  Server 2   │ │   Server 3    │
    │   (Port 5001)    │ │ (Port 5002) │ │ (Port 5003)   │
    └──────────────────┘ └─────────────┘ └───────────────┘
              │
    ┌─────────▼────────┐
    │ Python Server 4  │
    │   (Port 5004)    │
    └──────────────────┘
```

**Load Balancing Strategy**: Round-robin distribution with automatic health checks
- `max_fails=1`: Marks server as unavailable after 1 failed request
- `fail_timeout=30s`: Retries unavailable servers after 30 seconds

## 🔧 Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: 3.8+ (for local stress testing only)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/MarkDM/simple_docker_load_balancer.git
cd simple_docker_load_balancer
```

### 2. Start the Load Balancer

```bash
docker compose up -d
```

This command will:
- Build 4 Python Flask server containers
- Start an NGINX load balancer
- Configure automatic load distribution

### 3. Verify Setup

```bash
# Check all containers are running
docker compose ps

# Test the load balancer
curl http://localhost
```

### 4. View Real-time Monitoring

Open your browser and navigate to:
```
http://localhost/rps-display
```

You'll see a beautiful dashboard displaying real-time requests per second.

## 📁 Project Structure

```
simple_docker_load_balancer/
├── compose.yaml              # Docker Compose configuration
├── nginx.conf                # NGINX load balancer configuration
├── stress-test.py            # Load testing utility
├── README.md                 # This file
└── python-server/
    ├── Dockerfile            # Python server container definition
    ├── requirements.txt      # Python dependencies
    └── server.py             # Flask application with RPS tracking
```

## ⚙️ Configuration

### NGINX Configuration (`nginx.conf`)

The NGINX configuration uses an **upstream** block to define backend servers:

```nginx
upstream backend {
    server python-server-1:5001 max_fails=1 fail_timeout=30s;
    server python-server-2:5002 max_fails=1 fail_timeout=30s;
    server python-server-3:5003 max_fails=1 fail_timeout=30s;
    server python-server-4:5004 max_fails=1 fail_timeout=30s;
}
```

**Load Balancing Parameters**:
- `max_fails`: Number of failed attempts before marking server as down (default: 1)
- `fail_timeout`: Time before retrying an unavailable server (default: 30s)

### Docker Compose (`compose.yaml`)

Each Python server is defined as a separate service with:
- Unique port mapping
- Build arguments for dynamic port configuration
- Container name for easy identification

## 📖 Usage

### Basic Operations

**Start the services**:
```bash
docker compose up -d
```

**Stop the services**:
```bash
docker compose down
```

**View logs**:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f python-server-1
docker compose logs -f nginx
```

**Restart a specific server**:
```bash
docker compose restart python-server-1
```

### API Endpoints

Each backend server exposes the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main endpoint (returns request count and current RPS) |
| `/health` | GET | Health check endpoint |
| `/rps` | GET | Server-Sent Events stream of RPS data |
| `/rps-display` | GET | HTML dashboard for real-time RPS monitoring |

**Example Response** (`/`):
```json
{
  "status": "ok",
  "message": "Request received",
  "current_rps": 1234
}
```

## 🧪 Testing

### Stress Testing Tool

The project includes a Python-based stress testing tool to validate load distribution.

**Install dependencies**:
```bash
pip install requests
```

**Run basic test**:
```bash
python stress-test.py --n 1000
```

**Advanced usage**:
```bash
# Send 20,000 requests with 50 concurrent connections
python stress-test.py --n 20000 --c 50

# Custom URL
python stress-test.py --n 5000 --c 10 --u http://localhost:80
```

**Parameters**:
- `-n, --number`: Number of requests to send (default: 1000)
- `-c, --concurrent`: Number of concurrent requests (default: 1)
- `-u, --url`: Target URL (default: http://localhost:80)

### Sample Output

```
Sending 20000 requests to http://localhost:80
Concurrency: 50
------------------------------------------------------------
Request 1: Status 200, Time: 0.023s
Request 2: Status 200, Time: 0.019s
...
------------------------------------------------------------
Total requests: 20000
Successful: 20000
Failed: 0
Average response time: 0.025s
Total time: 12.345s
Requests per second: 1620.45
```

## 📊 Monitoring

### Real-time Dashboard

Access the built-in monitoring dashboard at:
```
http://localhost/rps-display
```

Features:
- Real-time RPS counter
- Connection status indicator
- Beautiful gradient UI with animations
- Automatic updates via Server-Sent Events

### Server Logs

Each Python server logs its current RPS every second:

```bash
docker compose logs -f python-server-1
```

Output:
```
[2025-11-08 10:30:45] Current RPS: 1234
[2025-11-08 10:30:46] Current RPS: 1189
[2025-11-08 10:30:47] Current RPS: 1256
```

## 📈 Scaling

### Adding More Servers

1. **Edit `compose.yaml`** to add a new service:

```yaml
python-server-5:
  build:
    context: ./python-server
    dockerfile: Dockerfile
    args:
      APP_PORT: 5005
  container_name: python-server-5
  ports:
    - "5005:5005"
```

2. **Edit `nginx.conf`** to include the new server:

```nginx
upstream backend {
    server python-server-1:5001 max_fails=1 fail_timeout=30s;
    server python-server-2:5002 max_fails=1 fail_timeout=30s;
    server python-server-3:5003 max_fails=1 fail_timeout=30s;
    server python-server-4:5004 max_fails=1 fail_timeout=30s;
    server python-server-5:5005 max_fails=1 fail_timeout=30s;
}
```

3. **Restart the services**:

```bash
docker compose down
docker compose up -d
```

### Removing Servers

Simply remove the service from both `compose.yaml` and `nginx.conf`, then restart.

## 🔍 Troubleshooting

### Container won't start

**Check logs**:
```bash
docker compose logs [service-name]
```

**Rebuild containers**:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Port already in use

If port 80 or 500x is already in use:

1. **Find the process**:
   ```bash
   # Windows
   netstat -ano | findstr :80
   
   # Linux/Mac
   lsof -i :80
   ```

2. **Stop the process or change ports** in `compose.yaml`

### NGINX can't connect to backend

**Verify backend servers are running**:
```bash
docker compose ps
```

**Test backend directly**:
```bash
curl http://localhost:5001
curl http://localhost:5002
```

### Load not distributed evenly

This is expected with round-robin! The distribution becomes more even with higher request volumes. Run a stress test to see balanced distribution:

```bash
python stress-test.py --n 10000 --c 50
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ using Docker, NGINX, and Python**
