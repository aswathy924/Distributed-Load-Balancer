# Distributed Load Balancer

A high-performance, asynchronous distributed load balancing system designed for modern web architectures. This project implements a robust reverse proxy that intelligently distributes traffic across multiple backend instances, ensuring high availability, fault tolerance, and optimal resource utilization.

## 📄 Abstract

As web applications scale, the ability to distribute incoming traffic efficiently across a cluster of servers becomes critical. This project presents a **Distributed Load Balancer** built using **FastAPI** and **Asynchronous Python**. Unlike traditional load balancers, this system offers dynamic flexibility through multiple scheduling algorithms, including Round Robin, Least Connections, Weighted Round Robin, Power of Two Choice, and Consistent Hashing.

The system features an integrated **Real-Time Monitoring Dashboard** that visualizes traffic patterns, server health, and response times. It includes a proactive **Health Monitoring Service** that automatically detects and removes unhealthy nodes from the cluster. Supporting both **Dockerized orchestration** and manual local execution, the project demonstrates a scalable approach to managing distributed systems with ultra-low latency and high transparency.

---

## ✨ Key Features

- 🚀 **Asynchronous Proxying**: Built with FastAPI and `httpx` for non-blocking I/O performance.
- ⚖️ **Multiple Balancing Algorithms**:
  - `Round Robin`: Simple sequential distribution.
  - `Least Connections`: Directs traffic to the server with the fewest active tasks.
  - `Random`: Stochastic distribution.
  - `Weighted Round Robin`: Assigns priority based on server capacity.
  - `Power of Two Choice`: Reduces load variance by picking the best of two random servers.
  - `Consistent Hashing`: Ensures session persistence based on client IP.
- 📊 **Real-Time Dashboard**: Premium glassmorphic interface showing live metrics (requests/sec, latency, server status).
- 💓 **Health Checks**: Automated background monitoring to ensure 100% uptime.
- 🛠️ **Dynamic Management**: API endpoints to add or remove backend servers on the fly without downtime.
- 🐳 **Docker Ready**: Fully containerized with `docker-compose` for instant deployment.
- 📈 **Load Testing**: Integrated Locust environment for stress testing the system.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) (Recommended)
- Python 3.9+ (For local execution)

### Option 1: Running with Docker (Recommended)

The easiest way to start the entire ecosystem (3 backends, Load Balancer, Dashboard, and Locust) is via Docker Compose:

```bash
docker-compose up --build
```

### Option 2: Running Locally

If you prefer to run it without Docker:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt  # If available, or install fastapi, uvicorn, httpx, flask
   ```
2. **Start the System**:
   ```bash
   python run_system.py
   ```

## 🌐 Multi-System (Multi-User) Setup

This project is designed to handle distributed backends across multiple physical machines. If you are working with a partner (e.g., machine at `192.168.2.31` and yours at `192.168.2.10`), follow these steps:

### 1. Partner's Machine (The Worker Node)
Your partner acts as an additional backend server in your cluster.
- **Run the Server**: She should run the backend script on her machine:
  ```bash
  python backend/server.py 5001
  ```
- **Find IP**: She needs to find her local IP address (e.g., open Cmd/PowerShell and type `ipconfig`). Look for its "IPv4 Address" (e.g., `192.168.2.31`).
- **Firewall**: She must allow incoming traffic on port `5001`. On Windows:
  - Settings > Update & Security > Windows Security > Firewall & network protection > Advanced settings > Inbound Rules > New Rule > Port > TCP > 5001 > Allow the connection.

### 2. Your Machine (The Load Balancer & Dashboard)
- **Open Dashboard**: Go to [http://localhost:7000](http://localhost:7000).
- **Register Partner**: In the **Cluster Provisioning** box, enter her address: `http://192.168.2.31:5001`.
- **Add & Monitor**: Click **Add**. The dashboard will immediately start pinging her machine. If it shows **UP** in green, the connection is successful!
- **Test Load**: Use the **🚀 Start Traffic Simulation** button on your dashboard. You will see her "Node Instance" statistics update as she processes requests.

---

## 🔗 Access Points

Once the system is running, you can access the various components:

- **Load Balancer**: [http://localhost:5000](http://localhost:5000)
- **Monitoring Dashboard**: [http://localhost:7000](http://localhost:7000)
- **Locust Load Tester**: [http://localhost:8089](http://localhost:8089)

---

## 🛠️ System Architecture

1. **Clients**: Send requests to the Load Balancer IP.
2. **Load Balancer**: Receives requests, selects a backend using the active algorithm, and proxies the request.
3. **Backend Servers**: Process the requests and return responses to the Load Balancer.
4. **Health Monitor**: Runs in the background, pinging servers to verify availability.
5. **Dashboard**: Fetches metrics from the Load Balancer and renders them in a modern UI.

---

## 📡 API Endpoints

- `GET /metrics`: Retrieve current system statistics.
- `GET /get_algorithm`: View the current balancing strategy.
- `GET /set_algorithm/{algo}`: Change the algorithm at runtime.
- `POST /api/servers/add`: Register a new backend server.
- `POST /api/servers/remove`: Unregister a backend server.
