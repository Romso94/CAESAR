Build agent:
- `docker build -t agent-client ./server`

Launch agent (Linux/WSL2):
- `docker run --network host agent-client`
- Ou avec docker-compose: `docker-compose up`

Note: Pour que nmap scanne l'interface de la machine hôte plutôt que celle du conteneur,
il est nécessaire d'utiliser le mode réseau host (`--network host`).
Sur Windows natif, utilisez WSL2 pour bénéficier du mode réseau host.