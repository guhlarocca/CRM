from .repositorio import Repositorio
import logging
import bcrypt

class UsuarioRepositorio(Repositorio):
    def criar_usuario(self, nome, email, senha):
        try:
            # Hash da senha
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
            
            self.cur.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nome, email, senha_hash.decode('utf-8')))
            
            self.conn.commit()
            return self.cur.fetchone()[0]
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao criar usuário: {e}")
            return None

    def buscar_por_email(self, email):
        try:
            self.cur.execute("""
                SELECT 
                    id, 
                    nome, 
                    email, 
                    is_admin, 
                    profile_photo 
                FROM usuarios 
                WHERE email = %s
            """, (email,))
            usuario = self.cur.fetchone()
            
            if usuario:
                return {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2],
                    'is_admin': usuario[3],
                    'profile_photo': usuario[4] or 'default_profile.png'
                }
            return None
        except Exception as e:
            logging.error(f"Erro ao buscar usuário por email: {e}")
            return None

    def buscar_por_id(self, user_id):
        try:
            self.cur.execute("""
                SELECT id, nome, email
                FROM usuarios
                WHERE id = %s
            """, (user_id,))
            
            usuario = self.cur.fetchone()
            if usuario:
                return {
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2]
                }
            return None
            
        except Exception as e:
            logging.error(f"Erro ao buscar usuário por ID: {e}")
            return None

    def verificar_senha(self, email, senha):
        try:
            self.cur.execute("""
                SELECT id, nome, email, senha 
                FROM usuarios 
                WHERE email = %s
            """, (email,))
            
            usuario = self.cur.fetchone()
            
            if not usuario:
                logging.error(f"Usuário não encontrado: {email}")
                return False
            
            # Desempacotar os valores
            usuario_id, nome, email_bd, hash_senha = usuario
            
            # Verificar a senha
            if bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8')):
                logging.info(f"Login bem-sucedido para {email}")
                return True
            else:
                logging.error("Senha incorreta")
                return False
            
        except Exception as e:
            logging.error(f"Erro crítico na verificação de senha: {e}", exc_info=True)
            return False

    def atualizar_senha(self, email, nova_senha):
        try:
            # Hash da nova senha
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), salt)
            
            self.cur.execute("""
                UPDATE usuarios 
                SET senha = %s 
                WHERE email = %s
            """, (senha_hash.decode('utf-8'), email))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar senha: {e}")
            return False

    def listar_usuarios(self):
        try:
            self.cur.execute("SELECT id, nome, email FROM usuarios")
            usuarios = self.cur.fetchall()
            return [{'id': u[0], 'nome': u[1], 'email': u[2]} for u in usuarios]
        except Exception as e:
            logging.error(f"Erro ao listar usuários: {e}")
            return []

    def debug_usuarios(self):
        try:
            self.cur.execute("SELECT id, nome, email, senha FROM usuarios")
            usuarios = self.cur.fetchall()
            
            logging.info("Depuração de usuários:")
            for usuario in usuarios:
                logging.info(f"ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}, Senha (primeiros 10 chars): {usuario[3][:10]}")
            
            return usuarios
        except Exception as e:
            logging.error(f"Erro ao debugar usuários: {e}")
            return []
