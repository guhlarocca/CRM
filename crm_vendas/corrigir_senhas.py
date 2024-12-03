import bcrypt
import logging
import os
from dotenv import load_dotenv
import psycopg2

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def corrigir_senhas():
    # Configurações de conexão
    conninfo = (
        f"host={os.getenv('DB_HOST')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'postgres')} "
        f"user={os.getenv('DB_USER')} "
        f"password={os.getenv('DB_PASS')} "
        "sslmode=require"
    )
    
    try:
        # Conectar ao banco
        with psycopg2.connect(conninfo) as conn:
            with conn.cursor() as cur:
                # Buscar todos os usuários
                cur.execute("SELECT id, email, senha FROM usuarios")
                usuarios = cur.fetchall()
                
                for user_id, email, senha_atual in usuarios:
                    try:
                        logger.info(f"\nProcessando usuário: {email}")
                        logger.info(f"Hash atual: {senha_atual}")
                        
                        # Forçar atualização da senha independente do formato
                        senha_temporaria = "Senha@123"
                        senha_bytes = senha_temporaria.encode('utf-8')
                        salt = bcrypt.gensalt(12)
                        novo_hash = bcrypt.hashpw(senha_bytes, salt)
                        novo_hash_str = novo_hash.decode('utf-8')
                        
                        logger.info(f"Novo hash gerado: {novo_hash_str}")
                        
                        # Atualizar a senha no banco
                        cur.execute("""
                            UPDATE usuarios 
                            SET senha = %s 
                            WHERE id = %s
                        """, (novo_hash_str, user_id))
                        
                        # Verificar se a senha foi atualizada
                        cur.execute("SELECT senha FROM usuarios WHERE id = %s", (user_id,))
                        senha_verificacao = cur.fetchone()[0]
                        logger.info(f"Hash após atualização: {senha_verificacao}")
                        
                        # Testar se a senha pode ser verificada
                        try:
                            senha_valida = bcrypt.checkpw(
                                senha_temporaria.encode('utf-8'),
                                senha_verificacao.encode('utf-8')
                            )
                            logger.info(f"Teste de verificação da senha: {'SUCESSO' if senha_valida else 'FALHA'}")
                        except Exception as e:
                            logger.error(f"Erro ao verificar nova senha: {e}")
                        
                        logger.info(f"Senha atualizada para o usuário {email}")
                        logger.info(f"Nova senha temporária para {email}: Senha@123")
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar usuário {email}: {str(e)}")
                        continue
                
                conn.commit()
                logger.info("\nProcesso de correção de senhas concluído")
                
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("Iniciando processo de correção de senhas...")
    if corrigir_senhas():
        logger.info("Processo concluído com sucesso!")
        logger.info("Senha temporária definida para todos os usuários: Senha@123")
        logger.info("Por favor, solicite que os usuários alterem suas senhas no próximo login.")
    else:
        logger.error("Erro ao executar o processo de correção")
