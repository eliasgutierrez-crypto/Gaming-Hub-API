# Frontend de Gaming Hub

Esta carpeta contiene un frontend mínimo con Vue 3 + Vite + TailwindCSS para la API de Gaming Hub.

## Instalación

1. Sitúate en este directorio:
   ```bash
   cd frontend
   ```

2. Instala las dependencias (requiere Node.js 18+):
   ```bash
   npm install
   ```

3. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```

   La aplicación estará disponible en `http://localhost:3000` y las peticiones que empiecen por `/api` se reenvían a `http://localhost:8002` (tu backend).

## Características

- Usa TailwindCSS para el estilo.
- El componente de ejemplo `GameList.vue` consulta `/api/games/top-rated` y muestra los resultados.

Puedes ampliar la interfaz creando nuevos componentes que consuman otros endpoints (recomendaciones, estadísticas, subidas, etc.).
