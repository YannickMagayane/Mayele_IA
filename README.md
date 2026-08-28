# 🇨🇩 Mayele IA — Plateforme d'Intelligence Stratégique & Analyse RDC

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vector Engine](https://img.shields.io/badge/ChromaDB-VectorDB-FF6F61?style=for-the-badge)](https://www.trychroma.com/)
[![Frontend](https://img.shields.io/badge/HTMX%20%2B%20Tailwind-CDN-007ACC?style=for-the-badge)](https://htmx.org/)
[![Author](https://img.shields.io/badge/Auteur-Yannick%20Magayane-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/yannick-magayane-8509ba1ab/)
[![Email Contact](https://img.shields.io/badge/Contact-Email-EA4335?style=for-the-badge&logo=gmail)](mailto:yannickmagayaneyannick@gmail.com)

**Mayele IA** est une plateforme souveraine et agentique d'intelligence économique, législative et minière spécialisée sur la **République Démocratique du Congo (RDC)** et l'Afrique. Elle triangule de façon autonome les données officielles et médiatiques via un pipeline de scraping direct multi-thread et un moteur **RAG (Retrieval-Augmented Generation)** avancé.

---

## 🌟 Fonctionnalités Clés

- 🤖 **Moteur RAG Agentique Triangulé** : Recherche vectorielle contextuelle via ChromaDB et synthèse dynamique sans hallucinations.
- 🌐 **Scraping Direct Multi-Thread & Autonome** : Ingestion concurrente sans dépendance API externe (Google CSE) sur plus de 50 portails cibles (Journal Officiel, BCC, ANAPI, Radio Okapi, Zoom-Eco, MediaCongo, Glencore, Ivanhoe Mines).
- 📄 **Extraction PDF Page par Page** : Conversion automatique des documents PDF officiels (décrets, arrêtés, rapports financiers) en enregistrements texte individuels par page (`pypdf`).
- ⏰ **Planification Asynchrone (00h00 / 12h00)** : Tâches d'arrière-plan gérées par `APScheduler` intégrées au démarrage du serveur Django.
- ⚡ **Interface Ultra-Fluide (HTMX & Alpine.js)** : Chat réactif avec zone de texte auto-extensible, raccourcis clavier (`Entrée` / `Maj+Entrée`), et actions instantanées (**Copier**, **Modifier**, **Réessayer**).
- 📊 **Tableau de Bord Macroéconomique** : Visualisation des opportunités d'emploi et des indices d'investissement par territoire (Kinshasa, Lubumbashi, Kolwezi, Goma).
- 🛡️ **Gestion des Quotas (Invités & Authentifiés)** : Calcul dynamique et restriction automatique des quotas quotidiens en session pour les invités et via profil ORM pour les utilisateurs enregistrés.

---

## 🏗️ Architecture du Projet

```text
assistant_IA/
├── analyzer/                 # Engine RAG, Vues HTMX, Modèles & Scheduler
│   ├── management/commands/  # Commandes Django (run_scraping_pipeline)
│   ├── templates/analyzer/   # Vues HTML (Chat, Dashboard, Composants)
│   ├── rag_engine.py         # Moteur Triangulé & Synthèse RAG
│   └── vector_engine.py      # Client ChromaDB Vector Store
├── authentication/           # Modèles Utilisateur, Profils & Quotas
├── data_pipeline/            # Pipeline de Collecte & Ingestion
│   ├── autonomous_linker.py  # Explorateur Direct & Keyword Routing (ThreadPool)
│   ├── cron_orchestrator.py  # Orchestrateur ACID Staging Area
│   └── parsers/
│       └── web_scraper.py    # Scrapeur Universal HTML & Parseur PDF (pypdf)
├── bin/                      # Scripts d'Administration & Déploiement
│   ├── init_db               # Initialisation SQLite & Données de Test
│   ├── up                    # Lancement Serveur Django + APScheduler
│   └── scrape                # Exécution Manuelle de la Vague de Scraping
├── core/                     # Configuration Django & Routes Principales
└── docker-compose.yml        # Configuration Conteneurs Docker & Traefik
```

---

## 🚀 Lancement Rapide

### 1. Cloner le Projet & Préparer l'Environnement

```bash
git clone <repository_url>
cd assistant_IA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialiser la Base de Données

```bash
bin/init_db
```

### 3. Démarrer l'Application

```bash
bin/up
```

L'application est accessible sur : `http://localhost:8000/`

---

## ⚙️ Commandes Utiles (`bin/`)

| Commande | Description |
| :--- | :--- |
| `bin/up` | Démarrage du serveur web Django et du planificateur APScheduler. |
| `bin/init_db` | Initialisation de la base SQLite et des profils de démonstration. |
| `bin/scrape` | Lancement manuel d'une vague complète de scraping web & PDF. |
| `bin/makemigration` | Génération des fichiers de migration Django (règle ORM). |

---

## 👤 Auteur & Contact

Conçu et développé par **Yannick Magayane**.

<p flex gap-4>
  <a href="https://www.linkedin.com/in/yannick-magayane-8509ba1ab/">
    <img src="https://img.shields.io/badge/LinkedIn-Yannick%20Magayane-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
  <a href="mailto:yannickmagayaneyannick@gmail.com">
    <img src="https://img.shields.io/badge/Email-yannickmagayaneyannick%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" />
  </a>

</p>

---

## 📄 Licence

Propriété exclusive — **Mayele IA RDC**. Tous droits réservés.
