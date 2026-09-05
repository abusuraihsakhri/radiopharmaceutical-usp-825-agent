# Radiopharmaceutical USP 825 Agent

> **Domain:** Nuclear Medicine & Radiopharmaceutical Quality Assurance
> **Reference Standard:** USP <825> Radiopharmaceuticals Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

Radiopharmaceutical USP 825 Agent is a multi-worker evaluation engine for nuclear medicine quality assurance. It processes task payloads through specialized workers that check:

- **Primary parameter boundaries** (Mo-99 breakthrough thresholds, purity limits)
- **Critical safety interlocks** (emergency flags, secondary kinetic breaches)
- **Protocol conformance** (specification anomalies, discordance detection)

Each evaluation produces a cryptographically signed consensus dossier with an HMAC-SHA256 tamper-evident audit trail.

---

## Key Capabilities

- **Deterministic Calculation Engine**: Strict compliance with USP <825> reference formulations and thresholds
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC)
- **Zero-PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs with integrity verification
- **FastAPI REST API**: OpenAPI 3.1 endpoints for audit, chat, and metrics
- **Prometheus Telemetry**: Operational metrics exporter

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/radiopharmaceutical-usp-825-agent.git
cd radiopharmaceutical-usp-825-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set required environment variable
export AUDIT_SECRET_KEY="your-cryptographic-key-min-16-chars"
# On Windows: set AUDIT_SECRET_KEY=your-cryptographic-key-min-16-chars
```

---

## CLI Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

---

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/audit` | Submit task for evaluation |
| POST | `/api/chat` | Supervisory chat query |
| GET | `/api/audit/logs` | Retrieve and verify audit trail |

---

## Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task identifier (alphanumeric, dash, dot, underscore) | Required |
| `target_identifier` | string | Target entity identifier | Required |
| `primary_metric` | float | Primary measurement value | Required |
| `secondary_metric` | float | Secondary kinetic/confidence score | Optional (default: 0.0) |
| `status_descriptor` | string | Status code or phenotype | Optional (default: "NOMINAL") |
| `is_critical_flag` | boolean | Emergency escalation trigger | Optional (default: false) |

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --tb=short

# Run security tests only
pytest tests/test_security.py -v
```

---

## Simulation Benchmark

```bash
# Run 1000 tasks with 8 concurrent workers
python simulator.py --tasks 1000 --concurrency 8
```

---

## Docker Deployment

```bash
# Copy environment template
cp .env.example .env
# Edit .env with your AUDIT_SECRET_KEY

# Build and run
docker-compose up --build
```

---

## Security Architecture

- **Zero-PHI Outbound Interceptor**: Blocks SSNs, MRNs, phone numbers, emails, DOB patterns, and patient names
- **HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs with full integrity verification (chain linkage + signature validation)
- **Input Validation**: Pydantic validators enforce identifier format and metric bounds
- **No Hardcoded Secrets**: `AUDIT_SECRET_KEY` must be provided via environment variable

---

## Project Structure

```
radiopharmaceutical-usp-825-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Multi-worker orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider abstraction
│   ├── metrics.py          # Prometheus metrics collector
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry broadcaster
├── usp_825_nuclear/        # USP-825 domain module
│   ├── agents.py           # Domain-specific sub-agents
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Domain data models
│   ├── cli.py              # Domain CLI
│   └── server.py           # Domain FastAPI server
├── tests/                  # Test suite
│   ├── conftest.py         # Shared fixtures
│   ├── test_security.py    # Security & edge case tests
│   ├── test_radiopharmaceutical_usp_825_agent.py
│   ├── test_usp_825_nuclear.py
│   └── test_enrichment.py
├── web/index.html          # Operations console UI
├── cli.py                  # Main CLI entry point
├── simulator.py            # High-throughput simulator
├── enrichment.py           # Domain enrichment engines
├── Dockerfile              # Container build
├── docker-compose.yml      # Container orchestration
└── pyproject.toml          # Project metadata
```
