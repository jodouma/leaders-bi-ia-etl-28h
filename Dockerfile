FROM python:3.13-slim

WORKDIR /workspace/projet

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Le dossier complet du cours est monté par Compose. Aucune dépendance pip.
CMD ["python", "--version"]
