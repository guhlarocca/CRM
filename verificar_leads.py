from database.conexao import ConexaoBanco
from database.modelos import Lead
from sqlalchemy.orm import sessionmaker

def verificar_leads():
    try:
        conexao = ConexaoBanco()
        engine = conexao.criar_engine()
        Session = sessionmaker(bind=engine)
        sessao = Session()

        leads = sessao.query(Lead).all()
        print(f'Total de leads: {len(leads)}')
        
        if not leads:
            print('Nenhum lead encontrado.')
            return

        print('\nDetalhes dos Leads:')
        for lead in leads:
            print(f'ID: {lead.id}, Nome: {lead.nome}, Estágio Atual: {lead.estagio_atual}')

    except Exception as e:
        print(f'Erro ao verificar leads: {e}')
    finally:
        sessao.close()

if __name__ == '__main__':
    verificar_leads()
