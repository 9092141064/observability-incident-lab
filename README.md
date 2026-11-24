# Observability & Incident Response Lab

Containerized monitoring, alerting, and log-triage lab using Docker Compose, Prometheus, Blackbox Exporter, Grafana, Alertmanager, Mailpit, and Elasticsearch/Kibana.

## Architecture Overview
- **App & Datastore (`app`, `redis`):** Exposes `/health` (`http://localhost:8080/health`) backed by Redis on `observability-incident-lab_monitoring-net`.
- **Probing & Alerting (`blackbox-exporter`, `prometheus`, `alertmanager`, `mailpit`):** Probes HTTP health/latency and Redis TCP reachability, evaluates alert rules (`AppEndpointDown`, `DatabasePortUnreachable`, `HighEndpointLatency`), and delivers alert emails to Mailpit (`http://localhost:8025`).
- **Visualization & Logs (`grafana`, `elasticsearch`, `kibana`):** Displays health, latency, and active firing alerts on Grafana (`http://localhost:3000`), with optional Elasticsearch/Kibana in `logging/docker-compose.logging.yml` (`http://localhost:5601`).

## Quick Start
```bash
docker compose up -d
docker compose -f logging/docker-compose.logging.yml up -d
