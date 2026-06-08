# StreamBOX — Frontend (Angular 18 SPA)

Interface Netflix-like consommant l'API Django.

## Stack
- Angular 18 (standalone components, lazy loading)
- RxJS · HLS.js (lecteur vidéo) · Chart.js (dashboard admin)
- Guards (auth, profile, admin, subscription) + intercepteur JWT

## Lancement local

```bash
cd frontend
npm install
npm start                          # http://localhost:4200
```

Le proxy (`proxy.conf.json`) redirige `/api` et `/media` vers `http://localhost:8000`
(backend Django) — assurez-vous qu'il tourne en parallèle.

## Configuration

- `src/environments/environment.ts` — dev (apiBase vide → proxy)
- `src/environments/environment.prod.ts` — prod (apiBase = URL Render)

**Avant de builder pour la prod**, éditer `environment.prod.ts` :
```ts
apiBase: 'https://streambox-api.onrender.com'
```

## Build production

```bash
npm run build -- --configuration production
# Sortie : dist/streambox/browser
```

## Déploiement Vercel

Voir le `README.md` à la racine, section **Déploiement Vercel**.
