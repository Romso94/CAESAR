# Comment les pages sont faites — Explication simple

## L’idée en une phrase

**Une « page » dans ton app = un composant React** (un fichier comme `Dashboard.jsx`).  
**App.jsx** décide **quelle page afficher** selon l’URL.  
**Layout.jsx** est le **cadre commun** (header, menu, footer) dans lequel la page s’affiche.  
**`<Outlet />`** est l’**emplacement** où React met le contenu de la page choisie.

---

## 1. Une page = un composant

En React, il n’y a pas de « fichier HTML par page » comme sur un site classique.  
Chaque écran = **un composant** = une fonction qui retourne du JSX (du HTML-like).

Exemples :

- **Page d’accueil** → composant `Home` (fichier `Home.jsx`)
- **Page de connexion** → composant `Login` (fichier `Login.jsx`)
- **Page tableau de bord** → composant `Dashboard` (fichier `Dashboard.jsx`)
- **Page résultats de scan** → composant `ScanResults` (fichier `ScanResults.jsx`)

Donc : **une page = un composant dans `src/pages/`**.

---

## 2. Qui décide quelle page afficher ? → App.jsx (les routes)

C’est **App.jsx** qui fait le lien entre **l’URL** et **le composant à afficher**.

Il utilise **React Router** :

- Tu vas sur `http://localhost:3000/` → on affiche `<Home />`
- Tu vas sur `http://localhost:3000/login` → on affiche `<Login />`
- Tu vas sur `http://localhost:3000/dashboard` → on affiche `<Dashboard />`
- etc.

En gros, dans App.jsx on a quelque chose comme :

```jsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/login" element={<Login />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/server-config" element={<ServerConfig />} />
  <Route path="/scan-results" element={<ScanResults />} />
</Routes>
```

Donc : **App.jsx définit toutes les routes** (URL → composant de page).

---

## 3. Pourquoi un « Layout » ? (header + menu + footer communs)

Sur les pages **connectées** (Dashboard, Config serveur, Résultats de scan), tu veux toujours :

- le **même header** (logo CAESAR, bouton Déconnexion)
- le **même menu** (Dashboard, Configuration Serveur, Résultats de Scan)
- le **même footer**

Au lieu de recopier ce bloc dans chaque page, on a **un seul composant** qui contient ce cadre : **Layout.jsx**.

- **Layout** = le **cadre** (header + menu + zone pour le contenu + footer).
- **Le contenu qui change** = la page du moment (Dashboard, ScanResults, etc.).

Donc : **Layout fournit la structure commune** (logo, navigation, footer).

---

## 4. Où est affiché le contenu de la page ? → `<Outlet />`

Dans Layout, tu as une zone « vide » réservée au contenu :

```jsx
<main>
  <Outlet />
</main>
```

**`<Outlet />`** veut dire : « Ici, React Router va mettre le composant de la page correspondant à l’URL ».

- Si l’URL est `/dashboard` → à la place de `<Outlet />`, React affiche **Dashboard**.
- Si l’URL est `/scan-results` → à la place de `<Outlet />`, React affiche **ScanResults**.

Donc : **Layout fournit le cadre, et la zone de contenu est donnée par `<Outlet />`**.

---

## 5. Comment tout s’assemble dans App.jsx ?

Pour les pages **protégées** (il faut être connecté), on n’affiche pas directement la page ; on l’enveloppe dans **Layout** :

```jsx
<Route element={<ProtectedRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/server-config" element={<ServerConfig />} />
  <Route path="/scan-results" element={<ScanResults />} />
</Route>
```

Et `ProtectedRoute` fait ceci :

- Si **pas connecté** → redirection vers `/login`.
- Si **connecté** → on affiche **Layout**, et à l’intérieur de Layout, **Outlet** affiche la bonne page (Dashboard, ServerConfig ou ScanResults).

En résumé :

- **ProtectedRoute** = « Tu es connecté ? Sinon on redirige. Sinon on affiche Layout + la page. »
- **Layout** = header + menu + **`<Outlet />`** + footer.
- **La page** (Dashboard, ScanResults, etc.) est donc **à l’intérieur** de Layout, à la place de `<Outlet />`.

---

## 6. Exemple concret : tu vas sur /dashboard

1. L’URL est `http://localhost:3000/dashboard`.
2. **App.jsx** : la route correspondante est dans `ProtectedRoute`, avec `path="/dashboard"` et `element={<Dashboard />}`.
3. **ProtectedRoute** : tu es connecté → il affiche `<Layout><Outlet /></Layout>`.
4. **Layout** s’affiche : tu vois le header (CAESAR, Déconnexion), le menu (Dashboard, Config, Résultats).
5. Là où il y a `<Outlet />`, React met le composant de la route « enfant » qui matche : **Dashboard**.
6. Donc à l’écran tu as : **Header + Menu + contenu de Dashboard + Footer**.

Si tu cliques sur « Résultats de Scan » :

- L’URL devient `/scan-results`.
- **Layout ne change pas** (même header, même menu, même footer).
- **Seul `<Outlet />` change** : au lieu de Dashboard, c’est maintenant **ScanResults** qui s’affiche dans la zone du milieu.

---

## 7. Schéma récapitulatif

```
Tu vas sur /dashboard
        │
        ▼
┌─────────────────────────────────────┐
│  App.jsx (React Router)             │
│  "Route /dashboard → Dashboard"     │
│  + ProtectedRoute → Layout + Outlet │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Layout.jsx                         │
│  ┌─────────────────────────────┐   │
│  │  Header (logo, Déconnexion)  │   │
│  ├─────────────────────────────┤   │
│  │  Menu (Dashboard, Config…)  │   │
│  ├─────────────────────────────┤   │
│  │  <Outlet />                  │   │  ← Ici React met le composant
│  │  = contenu de Dashboard      │   │     de la page (ex: Dashboard)
│  ├─────────────────────────────┤   │
│  │  Footer                      │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 8. Résumé en 3 points

1. **Une page = un composant** dans `src/pages/` (ex. `Dashboard.jsx`).
2. **App.jsx** définit les **routes** (quelle URL affiche quel composant) et enveloppe les pages connectées dans **Layout**.
3. **Layout.jsx** affiche le **cadre commun** (header, menu, footer) et utilise **`<Outlet />`** pour afficher **le contenu de la page** choisie par l’URL.

Tu peux retenir : **Layout = le cadre, Outlet = l’emplacement de la page, et la page = le composant (Dashboard, ScanResults, etc.)**.
