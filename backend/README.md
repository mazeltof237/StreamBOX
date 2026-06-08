# StreamBOX — Backend (Django + DRF)

API REST sécurisée par JWT pour la plateforme StreamBOX.

## Stack
- Django 5 · Django REST Framework · SimpleJWT
- PostgreSQL (prod) / SQLite (dev) via `dj-database-url`
- Gunicorn + WhiteNoise (prod)
- CORS headers

## Lancement local

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # éditer si besoin
python manage.py migrate
python manage.py seed_data        # films + comptes démo
python manage.py runserver        # http://localhost:8000
```

API : http://localhost:8000/api/
Admin Django : http://localhost:8000/admin/

## Variables d'environnement

Voir `.env.example`. Principales :
- `DJANGO_DEBUG` (0/1)
- `DJANGO_SECRET_KEY`
- `ALLOWED_HOSTS` (séparé par virgules)
- `DATABASE_URL` (PostgreSQL, vide = SQLite local)
- `CORS_ALLOWED_ORIGINS` (URL du frontend Angular)

## Comptes de démo (créés par `seed_data`)
- Utilisateur : `demo` / `demo12345`
- Admin : `admin` / `admin12345`

## Déploiement Render

Voir le `README.md` à la racine, section **Déploiement Render**.
