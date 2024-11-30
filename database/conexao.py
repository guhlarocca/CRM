import os
import pyodbc
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class ConexaoBanco:
    def __init__(self):
        # Configurações de conexão
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_NAME')
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.driver = os.getenv('DB_DRIVER')
        self.auth_type = os.getenv('AUTH_TYPE')

    def get_connection_string(self):
        """Gera a string de conexão baseada no tipo de autenticação"""
        if self.auth_type == 'sql':
            return f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};'
        else:
            return f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'

    def get_sqlalchemy_url(self):
        """Retorna a URL de conexão no formato do SQLAlchemy"""
        if self.auth_type == 'sql':
            return f'mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver={self.driver.replace(" ", "+")}'
        else:
            return f'mssql+pyodbc://@{self.server}/{self.database}?driver={self.driver.replace(" ", "+")}&trusted_connection=yes'

    def criar_engine(self):
        """Cria e retorna um engine SQLAlchemy"""
        try:
            # Criar string de conexão direta
            conn_str = (
                'DRIVER={ODBC Driver 17 for SQL Server};'
                f'SERVER={self.server};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                'TrustServerCertificate=yes;'
            )
            
            url = f"mssql+pyodbc:///?odbc_connect={conn_str}"
            
            # Criar engine com configuração mínima
            engine = sa.create_engine(url)
            
            return engine
            
        except Exception as e:
            print(f"Erro detalhado ao criar engine: {e}")
            raise e

    def criar_sessao(self):
        """Cria uma sessão do SQLAlchemy"""
        engine = self.criar_engine()
        Session = sessionmaker(bind=engine)
        return Session()

    def testar_conexao(self):
        """Testa a conexão com o banco de dados"""
        try:
            engine = self.criar_engine()
            with engine.connect() as connection:
                # Tentar executar um comando simples
                result = connection.execute(sa.text("SELECT 1"))
                print("Conexão bem-sucedida!")
                return True
        except Exception as e:
            print(f"Erro de conexão: {e}")
            
            # Diagnóstico adicional
            import socket
            try:
                # Tentar resolver o nome do servidor
                ip = socket.gethostbyname(self.server)
                print(f"IP do servidor: {ip}")
            except socket.gaierror:
                print(f"Não foi possível resolver o nome do servidor: {self.server}")
            
            # Verificar portas comuns do SQL Server
            import socket
            ports_to_check = [1433, 1434]
            for port in ports_to_check:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.server, port))
                if result == 0:
                    print(f"Porta {port} está aberta")
                else:
                    print(f"Porta {port} está fechada")
                sock.close()
            
            return False
