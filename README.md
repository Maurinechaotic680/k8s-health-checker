# 🏥 k8s-health-checker

[![PyPI](https://img.shields.io/pypi/v/k8s-health-checker.svg)](https://pypi.org/project/k8s-health-checker/)
[![CI](https://github.com/SanjaySundarMurthy/k8s-health-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/SanjaySundarMurthy/k8s-health-checker/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/k8s-health-checker.svg)](https://pypi.org/project/k8s-health-checker/)

**A powerful CLI tool to scan Kubernetes clusters for health issues, misconfigurations, and security risks.**

Run one command. Get a complete health report with severity ratings, fix suggestions, and a health score — right in your terminal.

```
$ k8s-health scan
```

![k8s-health-checker demo](https://raw.githubusercontent.com/SanjaySundarMurthy/k8s-health-checker/main/docs/demo-screenshot.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🫛 **Pod Health** | CrashLoopBackOff, Pending, Failed, OOMKilled, high restarts |
| 🖥️ **Node Health** | NotReady, DiskPressure, MemoryPressure, PIDPressure, cordoned |
| 📊 **Resource Limits** | Missing CPU/memory requests and limits |
| 🩺 **Health Probes** | Missing readiness and liveness probes |
| 🔒 **Security** | NetworkPolicies, privileged containers, service accounts |
| ⚙️ **Workloads** | Deployment/StatefulSet/DaemonSet replicas, stuck rollouts |
| 📈 **Autoscaling** | HPA at max, min=max (disabled autoscaling) |
| 🎯 **Health Score** | 0-100 score with letter grade (A-F) |
| 🎨 **Beautiful Output** | Rich terminal tables with colors and icons |
| 📄 **JSON Export** | Pipe results to other tools or dashboards |
| 🎮 **Demo Mode** | Try instantly — no cluster needed |

---

## 🚀 Quick Start

### Install

```bash
pip install k8s-health-checker
```

Or install from source:

```bash
git clone https://github.com/SanjaySundarMurthy/k8s-health-checker.git
cd k8s-health-checker
pip install -e .
```

### Try It (No Cluster Needed)

```bash
k8s-health scan --demo
```

This runs a full scan with realistic demo data — perfect for trying the tool before connecting to a real cluster.

### Scan Your Cluster

```bash
# Full cluster scan
k8s-health scan

# Scan a specific namespace
k8s-health scan -n production

# Scan specific categories only
k8s-health scan -c pods -c nodes

# JSON output (pipe to jq, file, or API)
k8s-health scan -o json
k8s-health scan -o json > report.json

# Just the health score
k8s-health score
```

---

## 📋 Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python** | 3.9 or higher |
| **kubectl** | Configured with access to your cluster |
| **RBAC** | Cluster-wide read access (or namespace-scoped) |

For demo mode, only Python is needed — no cluster, no kubectl, no credentials.

---

## 🔍 What It Checks

### 🫛 Pods
- **CrashLoopBackOff** — containers crash-looping (CRITICAL)
- **OOMKilled** — containers killed by OOM killer (CRITICAL)
- **Failed state** — pods in Failed phase (CRITICAL)
- **Excessive restarts** — containers with 20+ restarts (CRITICAL)
- **Elevated restarts** — containers with 5+ restarts (WARNING)
- **Pending** — pods stuck in Pending phase (WARNING)

### 🖥️ Nodes
- **NotReady** — nodes not accepting workloads (CRITICAL)
- **DiskPressure** — nodes running out of disk (CRITICAL)
- **MemoryPressure** — nodes running out of memory (CRITICAL)
- **PIDPressure** — too many processes on node (WARNING)
- **Cordoned** — nodes marked unschedulable (INFO)

### 📊 Resources
- **Missing requests** — containers without CPU/memory requests (WARNING)
- **Missing limits** — containers without CPU/memory limits (WARNING)

### 🩺 Probes
- **Missing readiness probe** — traffic may hit unready containers (WARNING)
- **Missing liveness probe** — hung containers won't restart (INFO)

### 🔒 Security
- **Privileged containers** — full host access (CRITICAL)
- **Running as root** — UID 0 containers (WARNING)
- **No NetworkPolicies** — unrestricted pod communication (WARNING)
- **Default ServiceAccount** — pods using default SA (INFO)

### ⚙️ Workloads
- **No ready replicas** — deployment completely down (CRITICAL)
- **Partial readiness** — not all replicas ready (WARNING)
- **Stuck rollout** — rollout not progressing (WARNING)
- **Single replica** — no high availability (INFO)
- **Scaled to zero** — intentionally or accidentally (INFO)

### 📈 Autoscaling
- **HPA at max** — autoscaler can't add more replicas (WARNING)
- **HPA min = max** — autoscaling effectively disabled (INFO)
- **No HPAs** — no autoscaling configured (INFO)

---

## 📊 Health Score

The tool calculates a health score from **0 to 100**:

| Severity | Points Deducted |
|----------|----------------|
| 🔴 CRITICAL | -8 per issue |
| 🟡 WARNING | -3 per issue |
| 🔵 INFO | -1 per issue |
| 🟢 PASS | 0 |

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | **A** | Excellent — minimal issues |
| 75-89 | **B** | Good — some improvements needed |
| 60-74 | **C** | Fair — several issues to address |
| 40-59 | **D** | Poor — significant problems |
| 0-39 | **F** | Critical — immediate attention needed |

---

## 🔧 CLI Reference

```
Usage: k8s-health [OPTIONS] COMMAND [ARGS]...

🏥 k8s-health-checker — Scan Kubernetes clusters for health issues.

Commands:
  scan     Run a full health scan on your Kubernetes cluster.
  score    Show just the cluster health score (0-100).

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.
```

### `k8s-health scan`

```
Options:
  -n, --namespace TEXT        Scan a specific namespace only.
  -c, --category [pods|nodes|resources|probes|security|workloads|autoscaling]
                              Run only specific categories (repeatable).
  -o, --output [terminal|json]
                              Output format (default: terminal).
  --demo                      Run with demo data (no cluster needed).
  --help                      Show this message and exit.
```

### `k8s-health score`

```
Options:
  -n, --namespace TEXT  Scan a specific namespace.
  --demo                Use demo data.
  --help                Show this message and exit.
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone and set up dev environment
git clone https://github.com/SanjaySundarMurthy/k8s-health-checker.git
cd k8s-health-checker
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Sanjay S** — Senior DevOps Engineer

- Portfolio: [sanjaysundarmurthy-portfolio.vercel.app](https://sanjaysundarmurthy-portfolio.vercel.app/)
- GitHub: [@SanjaySundarMurthy](https://github.com/SanjaySundarMurthy)
- LinkedIn: [Sanjay S](https://www.linkedin.com/in/sanjay-sundar-murthy/)

---

⭐ **If this tool helps you, give it a star on GitHub!**
