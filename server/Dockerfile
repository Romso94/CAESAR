FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    WEBSOCKET_HOST=0.0.0.0 \
    WEBSOCKET_PORT=8765

WORKDIR /app

# Copier les fichiers depuis le répertoire courant (server/)
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Créer la structure server/ et copier le code + assets front
RUN mkdir -p ./server
COPY serveur.py ./server/serveur.py
COPY templates ./server/templates
COPY static ./server/static
RUN touch ./server/__init__.py

# Ajout de l'entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose HTTP API + WebSocket
EXPOSE 8000 8765

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "server.serveur"]
