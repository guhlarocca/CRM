import os
import sys

# Adiciona os diretórios necessários ao path do Python
base_dir = os.path.dirname(os.path.abspath(__file__))
crm_vendas_dir = os.path.join(base_dir, 'crm_vendas')
sys.path.insert(0, base_dir)
sys.path.insert(0, crm_vendas_dir)

from crm_vendas.app import app

if __name__ == "__main__":
    app.run()
