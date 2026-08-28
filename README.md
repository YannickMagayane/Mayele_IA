# 🇨🇩 Mayele IA — Plateforme d'Intelligence Stratégique & Analyse RDC

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vector Engine](https://img.shields.io/badge/ChromaDB-VectorDB-FF6F61?style=for-the-badge)](https://www.trychroma.com/)
[![Frontend](https://img.shields.io/badge/HTMX%20%2B%20Tailwind-CDN-007ACC?style=for-the-badge)](https://htmx.org/)
[![Author](https://img.shields.io/badge/Auteur-Yannick%20Magayane-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/yannick-magayane-8509ba1ab/)
[![Email Contact](https://img.shields.io/badge/Contact-Email-EA4335?style=for-the-badge&logo=gmail)](mailto:yannickmagayaneyannick@gmail.com)

**Mayele IA** est une plateforme souveraine et agentique d'intelligence économique, législative et minière spécialisée sur la **République Démocratique du Congo (RDC)** et l'Afrique. 

Résultat de **3 mois d'ingénierie intensive**, la plateforme triangule de façon autonome les données officielles et médiatiques via un pipeline de scraping direct multi-thread (sans API externe payante) et un moteur **RAG (Retrieval-Augmented Generation)** avancé.

---

## 🌟 Fonctionnalités Clés

- 🤖 **Moteur RAG Agentique Triangulé** : Recherche vectorielle contextuelle via ChromaDB et synthèse dynamique Gemini sans hallucinations.
- 🌐 **Scraping Direct Multi-Thread & Autonome** : Ingestion concurrente sans dépendance API externe (Google CSE) sur plus de 50 portails cibles (Journal Officiel, BCC, ANAPI, Radio Okapi, Zoom-Eco, MediaCongo, Glencore, Ivanhoe Mines).
- 📄 **Extraction PDF Page par Page** : Conversion automatique des documents PDF officiels (décrets, arrêtés, rapports financiers) en enregistrements texte individuels par page (`pypdf`).
- ⏰ **Planification Asynchrone (00h00 / 12h00)** : Tâches d'arrière-plan gérées par `APScheduler` intégrées au démarrage du serveur Django.
- ⚡ **Interface Ultra-Fluide (HTMX & Alpine.js)** : Chat réactif avec zone de texte auto-extensible, raccourcis clavier (`Entrée` / `Maj+Entrée`), et actions instantanées (**Copier**, **Modifier**, **Réessayer**).
- 📊 **Tableau de Bord Macroéconomique** : Visualisation des opportunités d'emploi et des indices d'investissement par territoire (Kinshasa, Lubumbashi, Kolwezi, Goma).
- 🛡️ **Gestion des Quotas (Invités & Authentifiés)** : Calcul dynamique et restriction automatique des quotas quotidiens en session pour les invités (50 requêtes/jour) et via profil ORM pour les utilisateurs enregistrés.

---

## 🔑 Variables d'Environnement (`.env`)

Créez un fichier `.env` à la racine du projet en vous basant sur la structure suivante :

```env
# Clé API Google Gemini (Requis pour la synthèse RAG et les embeddings)
GEMINI_API_KEY_PRO=votre_cle_gemini_api_ici

# Configuration Django
SECRET_KEY=django-insecure-votre_cle_secrete_ici
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Configuration Base de données (Optionnel - Par défaut SQLite WAL)
# DATABASE_URL=sqlite:///observatory_rdc.db
```

---

## 🏗️ Architecture Détaillée du Système

```text
Mayele_IA/
├── analyzer/                 # Engine RAG, Vues HTMX, Modèles & Scheduler
│   ├── management/commands/  # Commandes Django (run_scraping_pipeline)
│   ├── templates/analyzer/   # Vues HTML (Chat, Dashboard, Composants)
│   ├── rag_engine.py         # Moteur Triangulé & Synthèse RAG
│   └── vector_engine.py      # Client ChromaDB Vector Store
├── authentication/           # Modèles Utilisateur, Profils & Quotas
├── data_pipeline/            # Pipeline de Collecte & Ingestion
│   ├── autonomous_linker.py  # Explorateur Direct & Keyword Routing (ThreadPool)
│   ├── cron_orchestrator.py  # Orchestrateur ACID Staging Area (Granular Commits)
│   └── parsers/
│       └── web_scraper.py    # Scrapeur Universal HTML & Parseur PDF Page par Page (pypdf)
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
git clone https://github.com/YannickMagayane/Mayele_IA.git
cd Mayele_IA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurer les Variables d'Environnement

```bash
cp .env.example .env # Ou créez directement .env avec votre GEMINI_API_KEY_PRO
```

### 3. Initialiser la Base de Données

```bash
bin/init_db
```

### 4. Démarrer l'Application

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

## ⚠️ Lacunes du Système & Axes d'Amélioration (Roadmap)

Bien que fonctionnelle et robuste, la plateforme présente des opportunités d'amélioration pour les développeurs souhaitant contribuer :

1. **Rendu JavaScript Dynamique (SPAs)** : Les sites utilisant massivement React/Vue (sans SSR) nécessitent l'intégration d'un headless browser (`Playwright`) dans `web_scraper.py`.
2. **Gestion des Protocole Anti-Bot (WAF / Cloudflare)** : Certains portails (ex: `politico.cd`, `tmb.cd`) bloquent les requêtes directes (HTTP 403/503). L'ajout de rotation d'IP/Proxies est recommandé.
3. **OCR pour PDF Numérisés (Scannés)** : L'extraction actuelle (`pypdf`) traite les PDF contenant du texte vectoriel. L'intégration de `Tesseract OCR` permettrait de lire les anciens décrets scannés.
4. **Scalabilité Vectorielle (Qdrant / Milvus)** : Actuellement basée sur **ChromaDB local**, la base vectorielle gagnerait à être migrée vers un cluster Qdrant pour dépasser le million de vecteurs.

---

## 🤝 Guide de Contribution

Les contributions de la communauté sont les bienvenues ! Pour contribuer :

1. **Forker** le dépôt sur GitHub (`https://github.com/YannickMagayane/Mayele_IA`).
2. **Créer une branche** pour votre fonctionnalité (`git checkout -b feature/nom-fonctionnalite`).
3. **Respecter les conventions du projet** :
   - Python 3.14+ avec documentation Sphinx et exemples d'utilisation.
   - Préférer l'ORM Django aux requêtes SQL brutes.
   - Styling exclusivement via **Tailwind CSS CDN** et interactivité **HTMX + Alpine.js**.
   - Ne jamais exécuter de migration directe manuelle sans script `bin/`.
4. **Soumettre une Pull Request** avec une explication claire des modifications.

---

## 👤 Auteur & Contact

Conçu et développé sur une période de **3 mois d'ingénierie intensive** par **Yannick Magayane**.

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
