FROM python:3.11-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    nmap \
    iproute2 \
    procps \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installer exploitdb (searchsploit) depuis Git
RUN git clone https://gitlab.com/exploit-database/exploitdb.git /opt/exploit-database \
    && ln -sf /opt/exploit-database/searchsploit /usr/local/bin/searchsploit \
    && chmod +x /opt/exploit-database/searchsploit

WORKDIR /agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python", "-u", "agent.py"]