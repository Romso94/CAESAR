Build agent:
- `docker build -t agent-client ./server`

Launch agent:
- `$env:SERVER_HOST="192.168.1.132"; $env:WEBSOCKET_PORT="8765"; $env:WEBSOCKET_SCHEME="ws"; docker-compose up -d`


Sur Windows Docker Desktop, l'agent utilise automatiquement l'IP de l'hôte Windows
au lieu de scanner l'interface du conteneur Linux.