# 🎬 StreamBOX — Plateforme de streaming fullstack

Plateforme de streaming type Netflix. Catalogue de films & séries (Inception, Interstellar, Breaking Bad, Stranger Things, Le Parrain, Joker, Parasite, Squid Game, Dune, Oppenheimer…), profils multiples (dont Kids), watchlist, recommandations, plans d'abonnement, paiements, dashboard admin, lecteur vidéo HLS.

- **Backend** : Django 5 + DRF + JWT → déployable sur **Render**
- **Frontend** : Angular 18 SPA → déployable sur **Vercel**

---

## 📁 Structure

```
StreamBOX/
├── backend/                ← Django REST API
│   ├── accounts/           ← Profils, plans, abonnements, paiements
│   ├── catalog/            ← Films, séries, épisodes, watchlist
│   ├── api/                ← Endpoints REST (DRF)
│   ├── streambox/          ← settings, urls, wsgi
│   ├── requirements.txt
│   ├── Procfile
│   ├── build.sh
│   ├── .env.example
│   └── manage.py
├── frontend/               ← Angular 18 SPA
│   ├── src/app/
│   │   ├── core/           ← Services, Interceptor JWT, Guards
│   │   ├── pages/          ← 15 pages (browse, detail, watch, admin…)
│   │   └── shared/         ← Nav, Card, Toast
│   ├── src/environments/
│   ├── proxy.conf.json
│   ├── vercel.json
│   ├── .env.example
│   └── package.json
├── render.yaml             ← Blueprint Render (backend)
└── README.md               ← Ce fichier
```

---

## ⚡ Démarrage rapide

Prérequis : **Python 3.10+**, **Node.js 18+**, **npm**.

### Terminal 1 — Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver        # http://localhost:8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm install
npm start                          # http://localhost:4200
```

Le proxy Angular redirige `/api` et `/media` vers Django sur `:8000`.

➡ Ouvrir **http://localhost:4200**

---

## 🔑 Comptes de démonstration (créés par `seed_data`)

| Compte | Identifiants | Description |
|--------|--------------|-------------|
| 🎬 Utilisateur | `demo` / `demo12345` | Premium, 2 profils (dont Kids) |
| 🛠 Admin | `admin` / `admin12345` | Superuser + dashboard `/admin` |

---

## 🔧 Variables d'environnement

### Backend (`backend/.env`)
```
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=<long-random>
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=                       # vide en local (SQLite), rempli sur Render
CORS_ALLOWED_ORIGINS=http://localhost:4200
```

### Frontend
Pas de `.env` injecté par Angular CLI. Éditer **`frontend/src/environments/environment.prod.ts`** avant le build prod :
```ts
apiBase: 'https://streambox-api.onrender.com'
```

---

## 🚀 Déploiement Render (backend)

1. Pousser ce projet sur **GitHub** (gestion manuelle de votre côté).
2. Sur **render.com** → **New → Blueprint** → sélectionner le repo.
   - Le `render.yaml` à la racine est détecté automatiquement.
   - *Ou manuellement* : **New → Web Service**, **Root Directory** = `backend`, **Build Command** = `./build.sh`, **Start Command** = `gunicorn streambox.wsgi:application --bind 0.0.0.0:$PORT --workers 3`.
3. Variables d'environnement Render (à régler dans l'UI) :
   - `DJANGO_DEBUG` = `0`
   - `DJANGO_SECRET_KEY` → cliquer **Generate**
   - `ALLOWED_HOSTS` = `.onrender.com` (ou votre domaine custom)
   - `CORS_ALLOWED_ORIGINS` = URL Vercel du frontend (ex `https://streambox.vercel.app`)
4. (Recommandé) **New → PostgreSQL** Render → relier la variable `DATABASE_URL` au service web.
5. Premier déploiement : `build.sh` exécute `pip install` + `migrate` + `seed_data` → API + comptes prêts.
6. Récupérer l'URL publique, ex : `https://streambox-api.onrender.com`.

**Vérification** : ouvrir `https://streambox-api.onrender.com/` → JSON `{"status":"ok"}`. Puis `/admin/` → page de login.

> ⚠ Plan gratuit Render : l'instance s'endort après 15 min d'inactivité (premier appel ≈ 30 s).

---

## 🌐 Déploiement Vercel (frontend)

1. Avant tout : éditer `frontend/src/environments/environment.prod.ts` avec l'URL Render obtenue ci-dessus.
2. Sur **vercel.com** → **Add New → Project** → importer le repo GitHub.
3. Configuration :
   - **Root Directory** : `frontend`
   - **Framework Preset** : *Other*
   - **Build Command** : `npm run build -- --configuration production` (déjà dans `vercel.json`)
   - **Output Directory** : `dist/streambox/browser` (déjà dans `vercel.json`)
   - **Install Command** : `npm install`
4. Variables d'environnement Vercel : aucune requise (la SPA Angular embarque la config au build).
5. Cliquer **Deploy**.
6. Récupérer l'URL Vercel, ex : `https://streambox.vercel.app`.
7. ⚠ **Retour sur Render** : ajouter cette URL à `CORS_ALLOWED_ORIGINS` puis redéployer.

**Vérification** : ouvrir l'URL Vercel → page d'accueil → se connecter avec `demo/demo12345` → le catalogue doit s'afficher.

---

## 🧪 Routes API principales

```
POST /api/auth/signup/        Inscription
POST /api/auth/login/         Login → access + refresh JWT
POST /api/auth/refresh/       Rafraîchir le JWT
GET  /api/auth/me/            Profil utilisateur courant
GET  /api/browse/             Catalogue (rangées par genre)
GET  /api/titles/             Liste des titres
GET  /api/titles/:slug/       Détail d'un titre
GET  /api/genres/             Liste des genres
GET  /api/profiles/           Profils utilisateur (CRUD)
GET  /api/watchlist/          Ma liste
GET  /api/history/            Historique de lecture
GET  /api/plans/              Plans d'abonnement
POST /api/subscribe/          S'abonner
GET  /api/billing/            Facturation
GET  /api/admin/dashboard/    Stats admin (admin only)
```

---

## 🛠 Dépannage

| Problème | Solution |
|----------|----------|
| CORS bloqué côté navigateur | Vérifier `CORS_ALLOWED_ORIGINS` sur Render — doit contenir l'URL Vercel exacte (sans `/` final) |
| 401 sur tous les appels API | Token JWT expiré — le frontend appelle `/api/auth/refresh/` automatiquement, sinon se relogger |
| Render 502 au premier appel | Plan free endormi — attendre 30 s |
| Vercel build échoue | Vérifier que `Root Directory` = `frontend` et que `environment.prod.ts` n'a pas d'erreur TS |
| `seed_data` n'est pas joué | Render → onglet **Shell** → `python manage.py seed_data` |

---

## 📦 Build local de production

```bash
# Backend
cd backend
DJANGO_DEBUG=0 gunicorn streambox.wsgi:application --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build -- --configuration production
# Servir dist/streambox/browser avec n'importe quel static server
```

---

Projet de fin de semestre — **Institut Universitaire Saint Jean** · L2 Développement Web · M. KINKEU Daniel · 2025-2026.
