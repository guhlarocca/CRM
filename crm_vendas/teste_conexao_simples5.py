import os
from dotenv import load_dotenv
import logging
import sys

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

def debug_env_vars():
    try:
        # Forçar encoding do sistema
        if sys.platform.startswith('win'):
            import locale
            sys.stdout.reconfigure(encoding=locale.getpreferredencoding())

        # Carregar variáveis
        load_dotenv()
        logging.info("Variáveis de ambiente carregadas")

        # Listar todas as variáveis relevantes
        env_vars = {
            'DB_HOST': os.getenv('DB_HOST'),
            'DB_PORT': os.getenv('DB_PORT'),
            'DB_NAME': os.getenv('DB_NAME'),
            'DB_USER': os.getenv('DB_USER'),
            'DB_PASS': os.getenv('DB_PASS')
        }

        # Verificar cada variável
        for var_name, var_value in env_vars.items():
            if var_value:
                try:
                    # Tentar decodificar o valor
                    encoded_value = var_value.encode('utf-8')
                    decoded_value = encoded_value.decode('utf-8')
                    logging.info(f"{var_name} está presente e pode ser codificado/decodificado corretamente")
                    # Mostrar os primeiros caracteres para debug
                    safe_value = var_value[:10] + '...' if len(var_value) > 10 else var_value
                    logging.info(f"{var_name} valor (primeiros caracteres): {safe_value}")
                except UnicodeError as e:
                    logging.error(f"Erro de codificação em {var_name}: {str(e)}")
                    # Mostrar bytes para debug
                    if var_value:
                        bytes_repr = var_value.encode('raw_unicode_escape')
                        logging.error(f"Bytes de {var_name}: {bytes_repr}")
            else:
                logging.warning(f"{var_name} não está definida")

    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        logging.error(f"Tipo do erro: {type(e)}")

if __name__ == "__main__":
    debug_env_vars()
