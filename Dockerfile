# Dockerfile pour développement local (sans registre externe)
FROM python:3.11-slim

# Variables d'environnement pour optimiser Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# # Option 1: Si vous avez les fichiers localement (dans le même répertoire)
# # Copier les fichiers depuis le contexte de build local
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY main.py ./


#Option 2: Si vous voulez cloner depuis Git (commentez l'option 1 et décommentez celle-ci)
ARG GIT_REPO_URL=https://github.com/yannoushka74/Video_games_market.git
RUN git clone $GIT_REPO_URL . && pip install --no-cache-dir -r requirements.txt

# Créer un utilisateur non-root pour la sécurité
RUN addgroup --system --gid 1001 appgroup && adduser --system --uid 1001 --gid 1001 appuser

# Ajuster les permissions
RUN chown -R appuser:appgroup /app && chmod +x main.py

# Passer à l'utilisateur non-root
USER appuser

# Point d'entrée
CMD ["python", "main.py"]