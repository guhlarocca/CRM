from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from repositorio import LeadRepositorio
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

def testar_lead():
    try:
        # Configurar conexão
        connection_string = (
            f'mssql+pyodbc://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@'
            f'{os.getenv("DB_SERVER")}/{os.getenv("DB_NAME")}?driver={os.getenv("DB_DRIVER")}'
        )
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Criar repositório
        lead_repo = LeadRepositorio(session)
        
        # Dados do lead de teste
        dados_lead = {
            'nome': 'Lead Teste Campos Novos',
            'email': 'teste.campos@exemplo.com',
            'telefone': '(11) 99999-9999',
            'empresa': 'Empresa Teste',
            'cargo': 'Cargo Teste',
            'estagio_atual': 'Enviado Email',
            'observacoes': 'Lead criado para teste dos novos campos',
            
            # Novos campos de email
            'email_comercial': 'comercial@exemplo.com',
            'email_comercial_02': 'comercial2@exemplo.com',
            'email_comercial_03': 'comercial3@exemplo.com',
            'email_financeiro': 'financeiro@exemplo.com',
            
            # Outros campos novos
            'telefone_comercial': '(11) 98888-8888',
            'cidade': 'São Paulo',
            'estado': 'SP',
            'contato_01': 'Contato Principal',
            'contato_02': 'Contato Secundário'
        }
        
        print("\n=== Iniciando teste de criação de Lead ===")
        print("Criando lead com os seguintes dados:")
        for campo, valor in dados_lead.items():
            print(f"{campo}: {valor}")
            
        # Criar o lead
        novo_lead = lead_repo.criar_lead(dados_lead)
        print("\nLead criado com sucesso!")
        print(f"ID do lead: {novo_lead.id}")
        
        # Verificar se o lead foi criado corretamente
        lead_criado = lead_repo.buscar_lead_por_id(novo_lead.id)
        print("\nVerificando dados do lead criado:")
        print(f"Nome: {lead_criado.nome}")
        print(f"Email: {lead_criado.email}")
        print(f"Email Comercial: {lead_criado.email_comercial}")
        print(f"Email Comercial 02: {lead_criado.email_comercial_02}")
        print(f"Email Comercial 03: {lead_criado.email_comercial_03}")
        print(f"Email Financeiro: {lead_criado.email_financeiro}")
        print(f"Telefone Comercial: {lead_criado.telefone_comercial}")
        print(f"Cidade: {lead_criado.cidade}")
        print(f"Estado: {lead_criado.estado}")
        print(f"Contato 01: {lead_criado.contato_01}")
        print(f"Contato 02: {lead_criado.contato_02}")
        
        # Remover o lead de teste
        print("\nRemovendo lead de teste...")
        lead_repo.remover_lead(novo_lead.id)
        
        # Verificar se foi removido
        lead_removido = lead_repo.buscar_lead_por_id(novo_lead.id)
        if lead_removido is None:
            print("Lead removido com sucesso!")
        else:
            print("ERRO: Lead não foi removido corretamente!")
            
        print("\n=== Teste concluído ===")
        
    except Exception as e:
        print(f"\nERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    testar_lead()
