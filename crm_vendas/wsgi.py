import os
import sys

# Adiciona o diretório atual ao path do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import app

if __name__ == "__main__":
    app.run()
