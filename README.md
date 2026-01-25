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
