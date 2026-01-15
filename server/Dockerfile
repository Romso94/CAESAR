FROM python:3.11-slim

# Installer nmap et iproute2 (pour détecter l'IP de l'hôte)
RUN apt-get update && apt-get install -y nmap iproute2 && apt-get clean

WORKDIR /agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python", "agent.py"]