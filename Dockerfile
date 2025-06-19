# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

# Variables d'environnement pour optimiser Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer git et les dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cloner le repository (remplacez par votre URL)
RUN git clone https://github.com/yannoushka74/Video_games_market.git .

# Si repository privé, utilisez plutôt cette approche avec des secrets :
# RUN --mount=type=ssh git clone git@github.com:votre-username/votre-repo-videogames.git .

# Copier les requirements si ils existent dans le repo
# Sinon, créer un requirements.txt basique
RUN echo "pandas>=2.0.0\nrequests>=2.31.0\nnumpy>=1.24.0" > requirements.txt

# Créer les wheels pour les dépendances
RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

# Stage de production
FROM python:3.11-slim AS production

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:$PATH"

# Installer tini pour la gestion des signaux
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

# Copier les wheels et les installer
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels requirements.txt

# Copier le code source depuis le builder
COPY --from=builder /app /app

# Si vous avez un script principal spécifique, sinon créer un script par défaut


# Changer vers l'utilisateur non-root
RUN chown -R appuser:appgroup /app
USER appuser

# Utiliser tini comme PID 1 pour une gestion propre des signaux
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py"]