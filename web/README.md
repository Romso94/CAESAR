# CAESAR - Frontend Web Application

Application web moderne pour CAESAR - Système de scan de vulnérabilité automatique.

## Structure du projet

```
web/
  frontend/          # Application React frontend
    src/
      components/    # Composants réutilisables
      pages/         # Pages de l'application
      index.css      # Styles globaux avec Tailwind CSS
      App.jsx        # Point d'entrée de l'application
      main.jsx       # Configuration React
```

## Pages disponibles

- **Login** (`/login`) - Page de connexion
- **Register** (`/register`) - Page d'inscription
- **Dashboard** (`/dashboard`) - Tableau de bord principal
- **Configuration Serveur** (`/server-config`) - Configuration des serveurs à scanner
- **Résultats de Scan** (`/scan-results`) - Visualisation des résultats de scan

## Installation

```bash
cd web/frontend
npm install
```

## Développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

## Build pour production

```bash
npm run build
```

Les fichiers de production seront dans le dossier `dist/`

## Technologies utilisées

- **React 18** - Bibliothèque UI
- **React Router** - Navigation
- **Vite** - Build tool moderne
- **Tailwind CSS** - Framework CSS utility-first
- **PostCSS & Autoprefixer** - Traitement CSS

## Design

L'application utilise un design moderne avec :
- Thème sombre professionnel
- Dégradés et effets glassmorphism
- Animations subtiles
- Design responsive
- Palette de couleurs cohérente (bleu/noir/gris)
