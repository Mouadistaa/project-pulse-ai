# Project Pulse AI 🚦
**Jira + GitHub → KPIs delivery → Risques → Forecast → Rapports IA traçables**

Project Pulse AI est un tableau de bord intelligent de pilotage projet qui agrège l’activité Jira/GitHub (lecture seule) et fournit :
- des **métriques delivery** (lead time PR, temps en review, WIP, throughput),
- une **détection de risques** (retard, surcharge, instabilité) avec explications,
- un **forecast** (probabilité de tenir une date avec incertitude),
- des **rapports IA** hebdomadaires **traçables** (draft → approve → sent),
- un **mode simulation** (what-if : +1 dev / réduire scope / limiter WIP).

> Objectif : permettre à un PO/Manager/Tech Lead de savoir “où on en est vraiment” en 30 secondes.

---

## ✨ MVP (cible)
- Connexions Jira Cloud & GitHub (read-only)
- Cycle time analytics : lead time PR, temps avant 1ère review, temps en review, throughput, WIP
- Détection de dérive : bugs, PR trop grosses, hotspots, rework
- Alertes : NEW / ACK / RESOLVED + preuves (liens PR/tickets)
- Forecast : tendance + intervalle d’incertitude + probabilité de tenir une date
- Rapport IA : génération contrôlée + validation humaine + sources & audit trail
- Simulation : baseline vs scénario (capacité / scope / WIP)

---

## 🧱 Architecture (high-level)
- Frontend : Next.js + TypeScript
- Backend : FastAPI (Python) ou Node.js (API + connecteurs)
- Data : PostgreSQL (option DuckDB pour analytics)
- ML : modèles simples + règles métier (explicables)
- IA : résumés contrôlés + templates + citations de sources
- Observabilité : logs, métriques, suivi qualité modèle

---

## 📁 Structure du projet

Le dépôt est organisé en **monorepo** (frontend + backend + infra + docs), avec une séparation claire des modules métiers.

```txt
project-pulse-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # Lint + tests (front/back)
│       └── docker.yml                  # Build images (option)
├── docs/
│   ├── architecture/
│   │   ├── decisions/                  # ADR (Architecture Decision Records)
│   │   ├── diagrams/                   # PlantUML / schémas
│   │   └── README.md                   # Vue d’ensemble architecture
│   ├── api/
│   │   └── openapi.md                  # Convention API (si besoin)
│   ├── product/
│   │   ├── personas.md
│   │   ├── metrics_definitions.md      # Définitions KPI (p50/p85, WIP, etc.)
│   │   └── risk_rules.md               # Règles risques + seuils + explications
│   └── runbooks/
│       ├── local_setup.md              # Setup local
│       └── troubleshooting.md
├── infra/
│   ├── docker/
│   │   ├── postgres/                   # init scripts
│   │   └── grafana/                    # dashboards (option)
│   └── docker-compose.yml              # DB + app + (option) grafana/prometheus
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app + routers
│   │   ├── core/                       # config, logs, sécurité, erreurs
│   │   ├── db/                         # session, models, migrations
│   │   ├── modules/                    # intégrations, ingestion, analytics, forecast, rapports
│   │   ├── schemas/                    # Pydantic schemas
│   │   └── tests/                      # tests backend
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── README.md
├── frontend/
│   ├── app/                            # Next.js App Router
│   ├── components/                     # UI, charts, layout
│   ├── lib/                            # client API + utils
│   ├── styles/
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── README.md
├── scripts/
│   ├── dev.ps1                         # lance tout (Windows)
│   ├── init.ps1                        # setup (env, deps)
│   └── seed.ps1                        # seed DB fake data
├── .editorconfig
├── .env.example
├── docker-compose.yml                  # raccourci vers infra (option)
├── package.json                        # scripts monorepo (pnpm/turbo)
├── turbo.json                          # pipeline tasks
└── README.md
```

---

## 🗺️ Roadmap
### Phase 0 — Setup
- [ ] CI (lint/tests)
- [ ] Skeleton backend + healthcheck
- [ ] Skeleton frontend + pages vides
- [ ] Modèle de données + migrations

### Phase 1 — Ingestion
- [ ] GitHub connector (PRs/commits)
- [ ] Jira connector (tickets/sprints)
- [ ] Jobs de sync + rate limit handling

### Phase 2 — KPIs + alerting
- [ ] Calcul métriques
- [ ] Règles risques + explication
- [ ] UI alertes + détails

### Phase 3 — Forecast + simulation
- [ ] Modèle forecast + incertitude
- [ ] UI simulation (what-if)

### Phase 4 — Rapport IA traçable
- [ ] Templates + sources
- [ ] Workflow draft → approve → sent
- [ ] Audit trail complet

---

## 🔒 Principes
- Lecture seule côté Jira/GitHub
- Explicabilité : aucun risque sans métriques et preuves
- Traçabilité IA : chaque résumé cite ses sources
- Qualité : CI, lint, tests

---

## 📄 Licence
MIT — voir [LICENSE](LICENSE).
