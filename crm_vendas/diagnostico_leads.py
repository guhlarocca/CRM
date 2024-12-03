from database.conexao import ConexaoBanco
from database.repositorio import LeadRepositorio
from sqlalchemy import func

def diagnosticar_leads():
    # Criar conexão e sessão
    conexao = ConexaoBanco()
    sessao = conexao.criar_sessao()
    
    try:
        # Repositório de leads
        lead_repo = LeadRepositorio(sessao)
        
        # Consulta direta para verificar os estágios
        print("\n--- DIAGNÓSTICO DE LEADS ---")
        
        # Contagem total de leads
        total_leads = sessao.query(func.count(Lead.id)).scalar()
        print(f"Total de Leads: {total_leads}")
        
        # Consulta detalhada de leads por estágio
        leads_por_estagio = sessao.query(
            Lead.estagio_atual, 
            func.count(Lead.id)
        ).group_by(Lead.estagio_atual).all()
        
        print("\nLeads por Estágio:")
        for estagio, contagem in leads_por_estagio:
            print(f"{estagio}: {contagem}")
        
        # Verificar leads específicos
        print("\nDetalhes dos Leads:")
        leads = sessao.query(Lead).all()
        for lead in leads:
            print(f"ID: {lead.id}, Nome: {lead.nome}, Estágio: {lead.estagio_atual}")
        
        print("\n--- FIM DO DIAGNÓSTICO ---")
    
    except Exception as e:
        print(f"Erro no diagnóstico: {e}")
    
    finally:
        sessao.close()

if __name__ == "__main__":
    from database.modelos import Lead  # Importação aqui para evitar problemas de ciclo
    diagnosticar_leads()
