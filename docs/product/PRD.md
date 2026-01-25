# PRD — Project Pulse AI (MVP)
**Version :** 1.0  
**Date :** 25/01/2026  
**Owner :** Mouad Sahraoui Doukkali  
**Statut :** MVP / Portfolio / Démo  
**Repos & sources :** Jira Cloud + GitHub (lecture seule)  
**Doc de référence :** Cahier des charges (MVP) + diagrammes (use cases / architecture / séquences) :contentReference[oaicite:3]{index=3} :contentReference[oaicite:4]{index=4}

---

## 1) Résumé (1 phrase)
Un tableau de bord intelligent qui connecte Jira/GitHub, calcule des KPIs delivery, détecte des dérives et prédit des risques (avec incertitude), puis génère des rapports IA **traçables** validés par un humain. :contentReference[oaicite:5]{index=5}

---

## 2) Problème & contexte
Dans beaucoup d’équipes, l’état réel d’un projet est difficile à lire :
- Jira est déclaratif (ce qui “devrait” être fait),
- GitHub reflète l’activité (ce qui “se fait” vraiment),
- la synthèse reste manuelle (où on en est, quels risques arrivent, quelles décisions prendre). :contentReference[oaicite:6]{index=6}

**Conséquence :** reporting coûteux, décisions tardives, risques subis plutôt qu’anticipés.

---

## 3) Objectifs (SMART)
1. **Réduire** le temps de reporting hebdo à **< 10 min** (génération + validation). :contentReference[oaicite:7]{index=7}
2. Mettre à jour KPIs + alertes **au moins 1 fois/jour** (batch). :contentReference[oaicite:8]{index=8}
3. Détecter **3 familles de risques** (retard, surcharge, instabilité) avec **explication + sources**. :contentReference[oaicite:9]{index=9}
4. Fournir une **probabilité de tenir une date** + une **incertitude visible**. :contentReference[oaicite:10]{index=10}
5. Déployer en **Docker** avec logs structurés + métriques principales. :contentReference[oaicite:11]{index=11} :contentReference[oaicite:12]{index=12}

**KPI produit (mesure du succès) :**
- TTR (time-to-report) : temps entre “je veux un update” → “rapport validé et envoyé”.
- Adhésion : nb de rapports générés/validés, taux de lecture.
- Qualité : % d’alertes ACK/RESOLVED, faux positifs perçus (feedback).
- Performance : dashboard principal < 2s sur données déjà ingérées.

---

## 4) Périmètre MVP
### Inclus
- Intégrations Jira Cloud + GitHub en **lecture seule**. :contentReference[oaicite:13]{index=13}
- Ingestion **incrémentale quotidienne** + reprise simple. :contentReference[oaicite:14]{index=14} :contentReference[oaicite:15]{index=15}
- KPIs delivery : lead time PR (p50/p85), temps review, WIP, throughput, bug ratio, taille PR. :contentReference[oaicite:16]{index=16}
- Dérives : PR trop grosses, explosion bugs, hotspots (zone de code très touchée). :contentReference[oaicite:17]{index=17}
- Forecast : tendance + incertitude + proba de tenir une date cible. :contentReference[oaicite:18]{index=18}
- Alerting : cycle NEW/ACK/RESOLVED + explications. :contentReference[oaicite:19]{index=19}
- Rapport IA hebdo : **draft → approve → send** + traçabilité. :contentReference[oaicite:20]{index=20}
- Simulation : impact estimé si on ajoute 1 dev / réduit scope / limite WIP. :contentReference[oaicite:21]{index=21}

### Hors périmètre (MVP)
- Webhooks temps réel (après stabilisation).
- GitLab/Azure DevOps (V2).
- Actions automatiques sur Jira/GitHub (recommandations seulement).
- Warehouse externe type BigQuery (option volumétrie). :contentReference[oaicite:22]{index=22}

### Ce que le MVP n’est PAS
- Ne remplace pas Jira/GitHub.
- Ne “garantit” pas une date : le forecast est une estimation avec incertitude. :contentReference[oaicite:23]{index=23}

---

## 5) Personae & rôles (RBAC)
**Personae (métier) :** PO/PM, Manager, Tech Lead, Dev, Admin. :contentReference[oaicite:24]{index=24}  
**RBAC (droits applicatifs) :** Admin / Analyste / Lecteur. :contentReference[oaicite:25]{index=25}

Mapping recommandé (MVP) :
- Admin (persona) → Admin (RBAC)
- Tech Lead → Analyste
- PO/Manager → Lecteur ou Analyste
- Dev → Lecteur (ou Analyste si besoin d’investigation)

---

## 6) Hypothèses à challenger (points “casse-pieds” mais importants)
1. **“Jira + GitHub suffisent à refléter le travail réel”** : faux partiellement (support, réunions, incidents, dette non tracée). Risque : KPI biaisés. :contentReference[oaicite:26]{index=26}
2. **Mapping Jira↔PR** via clé dans titre/branche/commit : utile, mais incomplet (naming variable, squash merges, PR multi-tickets). Prévoir fallback “non lié” + taux de couverture visible. :contentReference[oaicite:27]{index=27}
3. **Forecast fiable sans historique** : dangereux. Sans volume/historique, mieux vaut un forecast conservateur + bandes d’incertitude + explication. :contentReference[oaicite:28]{index=28}
4. **Alertes** : si seuils mal calibrés → bruit → perte de confiance. Il faut un mode “explain + adjust” (même minimal). :contentReference[oaicite:29]{index=29}
5. **Rapports IA** : le risque n°1 est l’hallucination → obligation de sources et validation humaine (non négociable). :contentReference[oaicite:30]{index=30} :contentReference[oaicite:31]{index=31}

---

## 7) User journeys (MVP)
### UJ1 — “Où en est-on ?” (PO/Manager)
1) Ouvre dashboard → KPIs + tendances + alertes
2) Clique une alerte → voit “pourquoi” + preuves
3) Lance une simulation “+1 dev / réduire scope”
4) Décide (et le rapport hebdo reflète la décision)

### UJ2 — “Pourquoi on ralentit ?” (Tech Lead)
1) Dashboard → lead time en hausse
2) Drilldown : review time / taille PR / hotspots
3) Observe la dérive + tickets bugs
4) Recommandations “réduire WIP / PR plus petites / focus hotspot”

### UJ3 — “Rapport hebdo traçable” (Manager/PO)
1) Generate draft (période)
2) Lecture du draft + sources
3) Approve
4) Envoi (email/slack) + statut SENT :contentReference[oaicite:32]{index=32}

---

## 8) Exigences fonctionnelles (Epics → Stories → Acceptance)
Les use cases MVP attendus : auth, intégrations, KPIs, dérives, alertes, simulation, rapport IA. :contentReference[oaicite:33]{index=33}

### Epic A — Auth + Workspace + RBAC
**A1. Workspace**
- Créer un workspace, paramètres, invitation utilisateurs.
- AC : un user appartient à 1 workspace, et l’accès est refusé hors workspace. :contentReference[oaicite:34]{index=34}

**A2. Auth**
- OAuth ou email+mdp (MVP : email+mdp acceptable).
- AC : endpoints protégés, token/session, logout.

**A3. RBAC côté serveur**
- AC : impossible d’appeler “connecter Jira/GitHub” sans Admin ; simulation sans Analyste. :contentReference[oaicite:35]{index=35}

---

### Epic B — Intégrations Jira & GitHub (read-only) + ingestion
**B1. Connecteur GitHub**
- Récupérer repos, PR, commits, reviews (option : issues).
- AC : stockage normalisé + raw_json conservé pour audit. :contentReference[oaicite:36]{index=36} :contentReference[oaicite:37]{index=37}

**B2. Connecteur Jira**
- Récupérer projets, issues, sprints, statuts, transitions.
- AC : stockage normalisé + raw_json. :contentReference[oaicite:38]{index=38} :contentReference[oaicite:39]{index=39}

**B3. Ingestion incrémentale quotidienne**
- AC : relancer un job ne crée pas de doublons incohérents (idempotence). :contentReference[oaicite:40]{index=40} :contentReference[oaicite:41]{index=41}

**B4. Gestion erreurs API**
- Rate limit, timeouts, backoff, reprise au dernier point connu.
- AC : logs structurés + statut job + erreur exploitable. :contentReference[oaicite:42]{index=42}

**B5. Mapping Jira↔PR**
- Détecter clé ticket dans titr
