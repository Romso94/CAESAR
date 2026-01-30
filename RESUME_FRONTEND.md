# Résumé du Frontend CAESAR

## Vue d'ensemble

Le frontend de CAESAR est une **application web monopage (SPA)** construite avec **React**. Elle permet aux utilisateurs de s'inscrire, se connecter, configurer des serveurs à scanner et consulter des rapports de vulnérabilité.

---

## 1. Technologies utilisées

| Technologie | Version | Rôle |
|-------------|---------|------|
| **React** | 18.2.0 | Bibliothèque pour construire l'interface (composants, état, rendu) |
| **React Router DOM** | 6.20.0 | Navigation entre les pages (routes, liens, redirections) |
| **Vite** | 5.0.8 | Outil de build et serveur de développement (rapide, moderne) |
| **Tailwind CSS** | 3.3.6 | Framework CSS pour le style (classes utilitaires) |
| **PostCSS** | 8.4.32 | Traitement du CSS (intégration Tailwind) |
| **Autoprefixer** | 10.4.16 | Ajout des préfixes navigateurs dans le CSS |

### En quoi c’est codé ?

- **Langage** : **JavaScript** (syntaxe ES6+)
- **Fichiers** : **JSX** (`.jsx`) = JavaScript + balises HTML dans le même fichier
- **Style** : **Tailwind CSS** (classes dans le HTML) + **CSS** dans `index.css` pour les bases et composants réutilisables
- **Pas de TypeScript** : tout est en JavaScript

---

## 2. Structure du projet

```
web/frontend/
├── index.html              # Point d'entrée HTML (une seule page)
├── package.json            # Dépendances et scripts npm
├── vite.config.js          # Configuration Vite (port 3000, plugin React)
├── tailwind.config.js      # Couleurs, animations (primary, dark, fade-in)
├── postcss.config.js       # PostCSS + Tailwind
└── src/
    ├── main.jsx            # Point d'entrée React (montage de l'app dans #root)
    ├── App.jsx             # Composant racine : routes + auth + Layout
    ├── index.css           # Styles globaux + Tailwind + composants (.card, .btn-primary…)
    ├── components/         # Composants réutilisables
    │   └── Layout.jsx      # En-tête, menu, zone de contenu, footer
    ├── pages/              # Une page = un composant par écran
    │   ├── Home.jsx        # Page d'accueil (landing)
    │   ├── Login.jsx       # Connexion
    │   ├── Register.jsx     # Inscription
    │   ├── Dashboard.jsx   # Tableau de bord après connexion
    │   ├── ServerConfig.jsx # Configuration des serveurs
    │   ├── ScanResults.jsx # Résultats de scan (rapport d'exemple)
    │   └── UsersList.jsx   # Liste des utilisateurs (non utilisée actuellement)
    └── services/
        └── api.js          # Appels HTTP vers le backend (auth)
```

---

## 3. Comment les pages sont faites

### Principe général

- **Une page = un composant React** dans `src/pages/`.
- Chaque composant est une **fonction** qui retourne du **JSX** (HTML-like).
- Le **style** vient de **Tailwind** : classes du type `className="flex items-center bg-dark-800 ..."`.
- Les **données** viennent du **state** (`useState`) ou du **backend** via `services/api.js`.

### Rôle de chaque fichier clé

| Fichier | Rôle |
|---------|------|
| **main.jsx** | Importe React, ReactDOM, `App.jsx` et `index.css`, puis rend `<App />` dans `document.getElementById('root')`. |
| **App.jsx** | Définit toutes les **routes** (React Router), gère l’**authentification** (état + vérification du token), affiche un **écran de chargement**, et enveloppe les pages protégées dans **Layout**. |
| **Layout.jsx** | Structure commune des pages connectées : **header** (logo, déconnexion), **navigation** (Dashboard, Config serveur, Résultats de scan), **contenu** (`<Outlet />` = page courante), **footer**. |
| **index.css** | Base Tailwind (`@tailwind base/components/utilities`), style du `body`, et **composants CSS** : `.card`, `.btn-primary`, `.btn-secondary`, `.input-field`. |

### Routes

- **Publiques** : `/` (Home), `/login`, `/register`.
- **Protégées** (il faut être connecté) : `/dashboard`, `/server-config`, `/scan-results`.
- Si non connecté et qu’on essaie d’accéder à une page protégée → redirection vers `/login`.
- Si connecté et qu’on va sur `/login` ou `/register` → redirection vers `/dashboard`.

---

## 4. Fonctionnalités par page

### Home (`Home.jsx`)

- **Contenu** : Texte de présentation CAESAR, grille de fonctionnalités, section « À propos », boutons « Commencer » / « Se connecter ».
- **Technique** : Composant fonctionnel, pas d’état, uniquement du JSX et des liens `<Link>` vers `/register` et `/login`.
- **Style** : Tailwind (grilles, cartes, dégradés, boutons).

### Login (`Login.jsx`)

- **Contenu** : Formulaire email + mot de passe, lien « S’inscrire », message d’erreur.
- **Technique** : `useState` pour les champs du formulaire et l’erreur, `useNavigate` pour rediriger après connexion. Au submit : appel **API** `authAPI.login()`, stockage du **token** et des infos user dans **localStorage**, puis `onLogin()` et `navigate('/dashboard')`.
- **Style** : `.input-field`, `.btn-primary`, structure centrée, header avec lien retour.

### Register (`Register.jsx`)

- **Contenu** : Formulaire nom, email, mot de passe, confirmation mot de passe, lien « Se connecter ».
- **Technique** : Même principe que Login : `useState`, validation basique (champs remplis, mots de passe identiques, longueur), appel **API** `authAPI.register()`, stockage token + user, `onLogin()` et `navigate('/dashboard')`.
- **Style** : Même charte que Login.

### Dashboard (`Dashboard.jsx`)

- **Contenu** : Titre, cartes de stats (scans, vulnérabilités, serveurs, taux de sécurité), « Actions rapides », liste des derniers scans, guide de démarrage.
- **Technique** : Données en dur (tableaux d’objets). Liens `<Link>` vers `/server-config` et `/scan-results`. Pas d’appel API pour l’instant.
- **Style** : Grille de cartes, couleurs par type de stat, effet hover.

### ServerConfig (`ServerConfig.jsx`)

- **Contenu** : Formulaire pour ajouter un serveur (nom, host, port, type SSH/HTTPS/HTTP, username, password, description), liste des serveurs ajoutés avec bouton supprimer.
- **Technique** : `useState` pour le formulaire et la liste des serveurs. Tout est **local** (pas d’API) : ajout/suppression dans le state. Messages succès/erreur.
- **Style** : Grille formulaire + liste, labels, `.input-field`, `.btn-primary`.

### ScanResults (`ScanResults.jsx`)

- **Contenu** : Un **rapport de scan d’exemple** : un scan avec infos serveur, durée, stats (critique / élevé / moyen / faible), résumé exécutif, puis liste détaillée de vulnérabilités (titre, sévérité, CVE, CVSS, description, recommandation).
- **Technique** : Données en dur dans des objets/tableaux (ex. `exampleScan`, `mockVulnerabilities`). Une « liste de scans » avec un seul scan sélectionnable. Pas d’appel API.
- **Style** : Cartes, badges de sévérité (couleurs), tableaux, blocs « Recommandation ».

---

## 5. Authentification et API

### Côté frontend

- **Token JWT** : stocké dans `localStorage` sous la clé `caesar_token`.
- **User** : stocké dans `localStorage` sous la clé `caesar_user` (objet JSON).
- Au chargement de l’app, **App.jsx** lit le token et appelle **`authAPI.getMe()`** pour vérifier qu’il est valide. Si oui → utilisateur considéré connecté, sinon → suppression du token/user et déconnexion.
- **Connexion / Inscription** : Login et Register appellent `authAPI.login()` et `authAPI.register()`, puis stockent token et user et mettent à jour l’état d’auth dans `App.jsx`.

### Service API (`services/api.js`)

- **Base URL** : `import.meta.env.VITE_API_URL` ou `http://localhost:5000/api`.
- **Fonction générique** : `fetchAPI(endpoint, options)` qui ajoute le header `Authorization: Bearer <token>` si un token est présent, envoie le body en JSON, et lance une erreur si la réponse n’est pas `ok`.
- **authAPI** :
  - `register(userData)` → POST `/auth/register`
  - `login(email, password)` → POST `/auth/login`
  - `getMe()` → GET `/auth/me`
  - `getUsers()` → GET `/auth/users` (non utilisé dans les pages affichées actuellement).

---

## 6. Design et style

### Tailwind

- **Utility-first** : pas de CSS custom par composant, tout avec des classes (flex, grid, padding, couleurs, etc.).
- **Config** (`tailwind.config.js`) :
  - **Couleurs** : `primary` (bleu), `dark` (gris foncé) pour fond et bordures.
  - **Animations** : `fade-in`, `slide-up` (keyframes + classes).

### index.css

- **@tailwind** : base, components, utilities.
- **body** : fond en dégradé (`from-dark-900 via-dark-800 to-dark-900`), police, anti-aliasing.
- **Composants réutilisables** :
  - **.card** : fond semi-transparent, bordure, ombre, coins arrondis.
  - **.btn-primary** : bouton bleu dégradé, hover, légère translation.
  - **.btn-secondary** : bouton gris, bordure.
  - **.input-field** : champ full width, fond, bordure, focus ring bleu.

### Thème

- **Thème sombre** : fonds `dark-800`, `dark-900`, texte clair, accents bleu `primary`.
- **Responsive** : utilisation de `sm:`, `md:`, `lg:` pour grilles et espacements.
- **Cohérence** : mêmes composants (.card, .btn-*, .input-field) sur toutes les pages.

---

## 7. Récapitulatif des fonctionnalités

| Fonctionnalité | Où c’est fait | Comment |
|----------------|---------------|--------|
| Affichage des pages | React + React Router | Routes dans `App.jsx`, composants dans `pages/`. |
| Navigation | React Router | `<Router>`, `<Routes>`, `<Route>`, `<Link>`, `<Navigate>`, `<Outlet>`. |
| Connexion / Inscription | Login.jsx, Register.jsx, api.js | Formulaires, `authAPI.login/register`, localStorage, redirection. |
| Vérification de la session | App.jsx | `useEffect` + `authAPI.getMe()` au chargement. |
| Pages réservées aux connectés | App.jsx | `<ProtectedRoute>` qui redirige vers `/login` si pas connecté. |
| Layout commun (header, menu, footer) | Layout.jsx | Composant avec `<Outlet />` pour le contenu de la route. |
| Style global | index.css + Tailwind | Body, .card, .btn-*, .input-field, palette. |
| Style par composant | Tailwind | Classes directement dans le JSX. |
| Appels backend | services/api.js | `fetch` + token dans les headers, `authAPI`. |
| Données « métier » (serveurs, scan) | State local | `useState` dans ServerConfig et ScanResults, pas de persistance backend pour l’instant. |

---

## 8. En résumé

- **Langages** : JavaScript (ES6+), JSX, CSS (Tailwind + quelques règles dans `index.css`).
- **Framework** : React 18.
- **Build / dev** : Vite.
- **Routing** : React Router v6.
- **UI** : Tailwind CSS + composants CSS personnalisés dans `index.css`.
- **Pages** : Un composant par écran dans `pages/`, rendu via des routes dans `App.jsx`.
- **Auth** : Token JWT et user en localStorage, vérification avec `getMe()`, routes protégées dans `App.jsx`.
- **API** : Centralisée dans `services/api.js` avec `fetch` et en-tête `Authorization`.

Tout le front est donc codé en **JavaScript/JSX**, stylé avec **Tailwind** et un peu de **CSS**, et structuré en **composants React** et **routes** pour une SPA claire et maintenable.
