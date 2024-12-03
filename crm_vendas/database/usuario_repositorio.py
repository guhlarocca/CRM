from .repositorio import Repositorio
import logging
import bcrypt

class UsuarioRepositorio(Repositorio):
    def criar_usuario(self, nome, email, senha):
        try:
            # Hash da senha usando bcrypt com custo 12 (padrão seguro)
            senha_bytes = senha.encode('utf-8')
            salt = bcrypt.gensalt(12)
            senha_hash = bcrypt.hashpw(senha_bytes, salt)
            
            # Armazenar o hash como string UTF-8
            senha_hash_str = senha_hash.decode('utf-8')
            
            self.cur.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nome, email, senha_hash_str))
            
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
            
            try:
                # Garantir que o hash esteja em formato bytes
                senha_bytes = senha.encode('utf-8')
                hash_bytes = hash_senha.encode('utf-8') if isinstance(hash_senha, str) else hash_senha
                
                # Verificar se o hash está no formato correto do bcrypt (começa com $2b$)
                if not hash_bytes.startswith(b'$2'):
                    logging.error("Hash de senha em formato inválido")
                    return False
                
                # Verificar a senha usando bcrypt
                senha_valida = bcrypt.checkpw(senha_bytes, hash_bytes)
                if senha_valida:
                    logging.info(f"Login bem-sucedido para {email}")
                    return True
                else:
                    logging.error("Senha incorreta")
                    return False
            except ValueError as e:
                logging.error(f"Erro ao verificar senha (possível formato inválido): {e}")
                return False
            except Exception as e:
                logging.error(f"Erro inesperado ao verificar senha: {e}")
                return False
            
        except Exception as e:
            logging.error(f"Erro crítico na verificação de senha: {e}", exc_info=True)
            return False

    def atualizar_senha(self, email, nova_senha):
        try:
            # Hash da nova senha usando bcrypt com custo 12
            senha_bytes = nova_senha.encode('utf-8')
            salt = bcrypt.gensalt(12)
            senha_hash = bcrypt.hashpw(senha_bytes, salt)
            senha_hash_str = senha_hash.decode('utf-8')
            
            self.cur.execute("""
                UPDATE usuarios 
                SET senha = %s 
                WHERE email = %s
            """, (senha_hash_str, email))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar senha: {e}")
            return False

    def atualizar_senha_por_id(self, user_id, nova_senha):
        try:
            # Hash da nova senha usando bcrypt
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())
            
            self.cur.execute("""
                UPDATE usuarios 
                SET senha = %s 
                WHERE id = %s
            """, (senha_hash.decode('utf-8'), user_id))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar senha por ID: {e}")
            return False

    def login(self, email, senha):
        """
        Método de login que verifica as credenciais do usuário
        
        :param email: Email do usuário
        :param senha: Senha do usuário
        :return: Objeto Usuario se login for bem-sucedido, None caso contrário
        """
        try:
            # Primeiro, verificar a senha
            if self.verificar_senha(email, senha):
                # Se a senha estiver correta, buscar o usuário
                self.cur.execute("""
                    SELECT 
                        id, nome, email, is_admin, profile_photo 
                    FROM usuarios 
                    WHERE email = %s
                """, (email,))
                
                usuario_data = self.cur.fetchone()
                
                if usuario_data:
                    from .modelos import Usuario  # Importação local para evitar ciclo de importação
                    
                    # Criar objeto Usuario
                    usuario = Usuario(
                        id=usuario_data[0],
                        nome=usuario_data[1],
                        email=usuario_data[2],
                        is_admin=usuario_data[3],
                        profile_photo=usuario_data[4] or 'default_profile.png'
                    )
                    
                    return usuario
            
            return None
        
        except Exception as e:
            logging.error(f"Erro no método login: {e}")
            return None

    def obter_por_id(self, user_id):
        """
        Método para obter usuário por ID, compatível com Flask-Login
        
        :param user_id: ID do usuário (pode ser string UUID ou inteiro)
        :return: Objeto Usuario ou None
        """
        try:
            # Não precisamos mais converter para inteiro pois agora é UUID
            self.cur.execute("""
                SELECT 
                    id, nome, email, is_admin, profile_photo, senha 
                FROM usuarios 
                WHERE id = %s
            """, (user_id,))
            
            usuario_data = self.cur.fetchone()
            
            if usuario_data:
                from .modelos import Usuario  # Importação local para evitar ciclo de importação
                
                # Criar objeto Usuario
                usuario = Usuario(
                    id=usuario_data[0],
                    nome=usuario_data[1],
                    email=usuario_data[2],
                    is_admin=usuario_data[3],
                    profile_photo=usuario_data[4] or 'default_profile.png',
                    senha=usuario_data[5]
                )
                
                return usuario
            
            return None
        
        except Exception as e:
            logging.error(f"Erro ao obter usuário por ID: {e}")
            return None

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

    def atualizar_foto_perfil(self, user_id, filename):
        """
        Atualiza a foto de perfil do usuário
        
        :param user_id: ID do usuário
        :param filename: Nome do arquivo da foto
        :return: Objeto Usuario atualizado ou None em caso de erro
        """
        try:
            self.cur.execute("""
                UPDATE usuarios 
                SET profile_photo = %s 
                WHERE id = %s
                RETURNING id, nome, email, is_admin, profile_photo, senha
            """, (filename, user_id))
            
            self.conn.commit()
            usuario_data = self.cur.fetchone()
            
            if usuario_data:
                from .modelos import Usuario
                usuario = Usuario(
                    id=usuario_data[0],
                    nome=usuario_data[1],
                    email=usuario_data[2],
                    is_admin=usuario_data[3],
                    profile_photo=usuario_data[4],
                    senha=usuario_data[5]
                )
                return usuario
            return None
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar foto de perfil: {e}")
            return None
