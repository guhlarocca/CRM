#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências do sistema necessárias para o psycopg2
apt-get update
apt-get install -y \
    postgresql-server-dev-all \
    gcc \
    python3-dev

# Limpar cache do pip
pip cache purge

# Instalar dependências Python
pip install --no-cache-dir -r requirements.txt
