FROM python:3.12-slim-bookworm 

WORKDIR /app

# 1. Installation des dépendances Python et système (incluant libaio1)
COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y libaio1 wget && \
    # Ajout explicite d'oracledb pour résoudre ModuleNotFoundError
    pip install --no-cache-dir -r requirements.txt && \
    pip install oracledb && \ 
    rm -rf /var/lib/apt/lists/*
    
# 2. INTÉGRATION DU CLIENT ORACLE INSTANT CLIENT
COPY instantclient_19_29/ /usr/local/instantclient/

# 3. DÉFINITION DU CHEMIN DE LA LIBRAIRIE
ENV LD_LIBRARY_PATH=/usr/local/instantclient:$LD_LIBRARY_PATH

# 4. Création du lien symbolique (-f force le remplacement pour éviter "File exists")
RUN ln -sf /usr/local/instantclient/libclntsh.so.19.1 /usr/local/instantclient/libclntsh.so

# 5. Copie du code de l'application
COPY . .

CMD ["python","mcp_server.py"]