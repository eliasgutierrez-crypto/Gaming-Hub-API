# Frontend for Gaming Hub

This directory contains a minimal Vue 3 + Vite + TailwindCSS frontend for the Gaming Hub API.

## Setup

1. Change to this folder:
   ```bash
   cd frontend
   ```

2. Install dependencies (requires Node.js 18+):
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000` and requests starting with `/api` are proxied to `http://localhost:8002` (your backend).

## Features

- Uses TailwindCSS for styling.
- Example component `GameList.vue` fetches `/api/games/top-rated` and displays results.

You can extend the UI by creating new components that call other endpoints (recommendations, stats, uploads, etc.).
