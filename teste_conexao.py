import sys
sys.path.append('.')  # Adiciona o diretório atual ao path

from database.conexao import ConexaoBanco
from database.modelos import Lead
from database.repositorio import LeadRepositorio

def main():
    # Testar conexão
    conexao = ConexaoBanco()
    
    print(" Testando conexão com o banco de dados...")
    if conexao.testar_conexao():
        print(" Conexão estabelecida com sucesso!")
    else:
        print(" Falha na conexão com o banco de dados.")
        return

    # Criar sessão
    sessao = conexao.criar_sessao()
    repositorio = LeadRepositorio(sessao)

    try:
        # Criar um novo lead de teste
        dados_lead = {
            'nome': "João da Silva",
            'email': "joao.silva@exemplo.com",
            'telefone': "(11) 98765-4321",
            'empresa': "Empresa Teste",
            'cargo': "Gerente de Vendas",
            'estagio_atual': "Enviado Email",
            'observacoes': "Lead de teste para verificação do sistema"
        }

        print("\n Adicionando novo lead...")
        lead_criado = repositorio.adicionar_lead(dados_lead)
        print(f" Lead criado com ID: {lead_criado.id}")

        # Buscar o lead criado
        print("\n Buscando lead criado...")
        lead_encontrado = repositorio.obter_lead_por_id(lead_criado.id)
        print(f" Lead encontrado: {lead_encontrado}")

        # Atualizar o estágio do lead
        print("\n Atualizando estágio do lead...")
        lead_atualizado = repositorio.atualizar_estagio(lead_criado.id, "Retorno Agendado")
        print(f" Novo estágio: {lead_atualizado.estagio_atual}")

        # Listar todos os leads
        print("\n Listando todos os leads...")
        leads = repositorio.listar_leads()
        for lead in leads:
            print(f"- {lead.nome} (Estágio: {lead.estagio_atual})")

    except Exception as e:
        print(f" Erro durante os testes: {e}")
    finally:
        # Fechar a sessão
        sessao.close()

if __name__ == "__main__":
    main()
