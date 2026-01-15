Build agent:
- `docker build -t agent-client ./server`

Launch agent:
- `docker run --network host agent-client`
- Ou avec docker-compose: `docker-compose up`

Note: L'agent détecte automatiquement l'IP de l'hôte Windows via `host.docker.internal`
ou la gateway Docker. Pour forcer une IP spécifique, utilisez la variable d'environnement:
- `docker run -e SCAN_TARGET=192.168.1.100 agent-client`
- Ou dans docker-compose.yml: `SCAN_TARGET=192.168.1.100`

Sur Windows Docker Desktop, l'agent utilise automatiquement l'IP de l'hôte Windows
au lieu de scanner l'interface du conteneur Linux.