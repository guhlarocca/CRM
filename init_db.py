from database.conexao import ConexaoBanco
from database.modelos import Base, Usuario
from database.usuario_repositorio import UsuarioRepositorio
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

def init_database():
    # Criar conexão com o banco
    conexao = ConexaoBanco()
    engine = sa.create_engine(conexao.get_sqlalchemy_url())
    
    # Criar todas as tabelas
    Base.metadata.create_all(engine)
    
    # Criar sessão
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Criar repositório de usuários
    usuario_repo = UsuarioRepositorio(session)
    
    # Verificar se já existe um usuário admin
    admin_existente = usuario_repo.buscar_por_email('guh.larocca@gmail.com')
    
    if not admin_existente:
        # Criar usuário admin
        usuario_repo.criar_usuario(
            nome='Gustavo Larocca',
            email='guh.larocca@gmail.com',
            senha='Larocca@1234',
            is_admin=True
        )
        print("Usuário admin criado com sucesso!")
    else:
        print("Usuário admin já existe!")
    
    session.close()

if __name__ == '__main__':
    init_database()
