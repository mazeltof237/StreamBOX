export const environment = {
  production: false,
  // En dev, on passe par le proxy Angular (proxy.conf.json) → backend Django sur :8000.
  apiBase: 'http://localhost:8000',
};
