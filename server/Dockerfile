FROM python:3.11-slim

# Installer nmap
RUN apt-get update && apt-get install -y nmap && apt-get clean

WORKDIR /agent

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

CMD ["python", "agent.py"]