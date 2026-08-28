# 🛠️ Configuration des Prérequis Système & API - Mayele IA (RDC)

Ce document décrit la configuration des outils système, des clés API et de l'environnement réseau requis pour faire tourner l'architecture autonome du projet **Mayele IA** (Sprint Vibe Coding 4 Jours). 

Puisque le système fonctionne en **Scraping-Driven RAG** (zéro URL en dur), ces configurations sont indispensables pour permettre au robot de découvrir les sources et de traiter les médias lourds.

---

## 1. Outils Système (À installer sur la machine hôte)

### A. FFmpeg (Impératif pour le traitement audio)
Le processeur de médias utilise la bibliothèque Python `pydub` pour segmenter les fichiers audio des procès et des directs YouTube. `pydub` ne peut pas fonctionner sans la suite logicielle `ffmpeg`.

*   **Sur Linux (Ubuntu/Debian) :**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```
*   **Sur Mac (via Homebrew) :**
    ```bash
    brew install ffmpeg
    ```
*   **Sur Windows :**
    1. Télécharge les binaires compilés depuis le site officiel de FFmpeg.
    2. Extrais le dossier dans `C:\ffmpeg`.
    3. Ajoute le chemin `C:\ffmpeg\bin` à la variable d'environnement `PATH` de ton système.

---

## 2. Génération de la Clé API Google AI Studio (Compte Pro Payé)

Pour traiter des milliers de pages de syllabus ou des heures de fichiers audio sans bloquer sur les quotas gratuits (*Rate Limits*), ta clé doit être rattachée à ton abonnement Pro payé :

1. Rends-toi sur la console officielle : [Google AI Studio](https://aistudio.google.com).
2. Connecte-toi avec l'adresse Google détenant ton forfait **AI Pro / Gemini Advanced**.
3. Clique sur **"Get API key"** dans le menu latéral gauche.
4. Clique sur **"Create API key"** ➔ Choisis **"Create API key in a new project"** pour lier la facturation et les quotas de production à ton compte.
5. Copie la clé générée immédiatement (elle commence par `AIzaSy...`).

---

## 3. Moteur de Découverte Programmatique (Zéro URL en dur)

Puisque le script `autonomous_linker.py` doit chercher des liens tout seul sur le web congolais (LinkedIn, ONEM, sites ministériels), tu as besoin d'activer un accès de recherche automatisée.

### Option Conseillée : Google Custom Search Engine (CSE)
L'API Google CSE te permet d'exécuter 100 requêtes de recherche gratuites par jour, ce qui est parfait pour tes vagues d'ingestion de 00h00 et 12h00.

1. Rends-toi sur la [Console Google Cloud](https://console.cloud.google.com).
2. Crée un projet et active l'API **Custom Search API**.
3. Génère une clé API pour ce service (différente de la clé Gemini).
4. Va sur le portail [Google Programmable Search Engine](https://programmablesearchengine.google.com) pour créer un moteur de recherche configuré sur "Recherche sur tout le Web" avec une priorité pour les domaines `.cd` ou les expressions liées au marché du travail en RDC.
5. Récupère l'**Identifiant du moteur de recherche (CX ID)**.

---

## 4. Fichier des Secrets Environnementaux complet (`.env`)

Crée un fichier `.env` à la racine de ton application Django et rassemble toutes les clés d'infrastructure requises :

```env
# Configuration Django
DEBUG=False
SECRET_KEY=votre_cle_secrete_aleatoire_django_production

# Base de Données Analytique
DATABASE_URL=sqlite:///observatory_rdc.db

# Clé d'Intelligence Artificielle Pro (Génération & Embeddings)
GEMINI_API_KEY_PRO=AIzaSyVotreCleGoogleAiStudioProIci

# Clés du Moteur de Découverte de Liens Autonome (Google Custom Search)
GOOGLE_CSE_API_KEY=VotreCleGCPCustomSearchIci
GOOGLE_CSE_CX_ID=VotreIdentifiantMoteurDeRechercheCxIci

# Réseaux Sociaux (Optionnel pour Tweepy / X)
TWITTER_BEARER_TOKEN=VotreTokenTwitterDevIci
```

---

## 5. Spécifications Réseau & Connectivité (Contexte RDC)

*   **Scraping Incrémental de Midi & Minuit :** Le robot s'éveille à 00h00 et 12h00 pour interroger le web. Assure-toi que la machine ou le serveur est connecté à Internet à ces moments précis pendant environ 10 à 15 minutes.
*   **Optimisation de la bande passante :** Pour l'extraction YouTube, le script utilise des paramètres d'élite via `yt-dlp` pour rejeter le flux vidéo (lourd) et ne télécharger que la piste audio compressée en mono 128 kbps. Un procès de 4 heures est ainsi réduit à un fichier léger de 60 à 80 Mo, préservant ainsi ton forfait internet.
*   **X-Ray Indirect Execution :** Ne modifie pas la fréquence des cron-jobs en dessous de 2 vagues par jour. Les plateformes comme LinkedIn bloquent les connexions si un robot simule des milliers de clics à la minute. Le passage par l'indexation indirecte des moteurs de recherche configurée dans notre script élimine ce risque.
