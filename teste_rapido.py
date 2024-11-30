from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from database.repositorio import LeadRepositorio

def teste_lead():
    # Carregar variáveis de ambiente e criar conexão
    load_dotenv()
    connection_string = (
        f'mssql+pyodbc://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
        f'{os.getenv("DB_SERVER")}/{os.getenv("DB_NAME")}?driver={os.getenv("DB_DRIVER")}'
    )
    engine = create_engine(connection_string)
    Session = sessionmaker(bind=engine)
    sessao = Session()
    
    lead_repo = LeadRepositorio(sessao)
    
    try:
        # 1. Criar lead de teste
        dados_lead = {
            'nome': 'Lead Teste Campos',
            'email': 'teste@exemplo.com',
            'telefone': '(11) 99999-9999',
            'empresa': 'Empresa Teste',
            'cargo': 'Cargo Teste',
            'email_comercial': 'comercial@exemplo.com',
            'email_comercial_02': 'comercial2@exemplo.com',
            'email_comercial_03': 'comercial3@exemplo.com',
            'email_financeiro': 'financeiro@exemplo.com',
            'telefone_comercial': '(11) 98888-8888',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'contato_01': 'João Silva',
            'contato_02': 'Maria Santos',
            'estagio_atual': 'Enviado Email'
        }
        
        print("\n=== Criando lead de teste ===")
        novo_lead = lead_repo.criar_lead(dados_lead)
        print(f"Lead criado com ID: {novo_lead.id}")
        
        # 2. Verificar se foi criado corretamente
        print("\n=== Verificando dados do lead ===")
        lead = lead_repo.buscar_lead_por_id(novo_lead.id)
        print(f"Nome: {lead.nome}")
        print(f"Email: {lead.email}")
        print(f"Email Comercial: {lead.email_comercial}")
        print(f"Email Comercial 02: {lead.email_comercial_02}")
        print(f"Email Comercial 03: {lead.email_comercial_03}")
        print(f"Email Financeiro: {lead.email_financeiro}")
        print(f"Cidade: {lead.cidade}")
        print(f"Estado: {lead.estado}")
        print(f"Contatos: {lead.contato_01} / {lead.contato_02}")
        
        # 3. Remover o lead
        print("\n=== Removendo lead de teste ===")
        lead_repo.remover_lead(novo_lead.id)
        
        # 4. Verificar se foi removido
        lead_removido = lead_repo.buscar_lead_por_id(novo_lead.id)
        if lead_removido is None:
            print("Lead removido com sucesso!")
        else:
            print("ERRO: Lead não foi removido!")
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        sessao.close()

if __name__ == '__main__':
    teste_lead()
