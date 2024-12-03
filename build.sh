#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependências do sistema necessárias para o psycopg2
apt-get update
apt-get install -y python3-dev libpq-dev build-essential

# Instalar dependências Python
pip install --upgrade pip
pip install -r requirements.txt
