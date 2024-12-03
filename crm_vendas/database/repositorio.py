from datetime import datetime
from .modelos import Time, Lead
import logging
import psycopg2
import os
from dotenv import load_dotenv

class Repositorio:
    def __init__(self):
        self.conn = criar_conexao()
        self.cur = self.conn.cursor()

    def __del__(self):
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

class TimeRepositorio(Repositorio):
    def criar_membro(self, nome, email, telefone, profile_photo='default_profile.png'):
        try:
            # Verificar se já existe
            self.cur.execute("SELECT id FROM time WHERE email = %s", (email,))
            if self.cur.fetchone():
                return False

            # Pegar o maior ID existente
            self.cur.execute("SELECT COALESCE(MAX(id), 0) FROM time")
            max_id = self.cur.fetchone()[0]
            novo_id = max_id + 1

            # Inserir novo membro com ID calculado e campos leads/vendas zerados
            self.cur.execute("""
                INSERT INTO time (id, nome, email, telefone, profile_photo, leads, vendas)
                VALUES (%s, %s, %s, %s, %s, 0, 0)
                RETURNING id
            """, (novo_id, nome, email, telefone, profile_photo))
            
            self.conn.commit()
            return novo_id
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao criar membro: {e}")
            raise e

    def listar_membros(self):
        try:
            self.cur.execute("""
                SELECT 
                    t.id, 
                    t.nome, 
                    t.email, 
                    t.telefone, 
                    t.profile_photo,  
                    COALESCE(COUNT(l.id), 0) as total_leads,
                    COALESCE(SUM(CASE WHEN l.venda_fechada = true THEN 1 ELSE 0 END), 0) as total_vendas
                FROM time t
                LEFT JOIN leads l ON t.id = l.vendedor_id
                GROUP BY t.id, t.nome, t.email, t.telefone, t.profile_photo
                ORDER BY t.nome
            """)
            
            membros = []
            for row in self.cur.fetchall():
                membro = {
                    'id': row[0],
                    'nome': row[1],
                    'email': row[2],
                    'telefone': row[3],
                    'profile_photo': row[4],  
                    'leads': row[5] or 0,  
                    'vendas': row[6] or 0   
                }
                membros.append(membro)
            
            return membros
            
        except Exception as e:
            logging.error(f"Erro ao listar membros: {e}")
            return []

    def buscar_membro_por_id(self, id):
        try:
            self.cur.execute("""
                SELECT id, nome, email, telefone, profile_photo
                FROM time
                WHERE id = %s
            """, (id,))
            
            row = self.cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nome': row[1],
                    'email': row[2],
                    'telefone': row[3],
                    'profile_photo': row[4]
                }
            return None
            
        except Exception as e:
            logging.error(f"Erro ao buscar membro: {e}")
            return None

    def atualizar_membro(self, id, nome, email, telefone, profile_photo):
        try:
            logging.info(f"Atualizando membro {id}")
            logging.info(f"Nome: {nome}")
            logging.info(f"Email: {email}")
            logging.info(f"Telefone: {telefone}")
            logging.info(f"Foto: {profile_photo}")
            
            self.cur.execute("""
                UPDATE time
                SET nome = %s, email = %s, telefone = %s, profile_photo = %s
                WHERE id = %s
            """, (nome, email, telefone, profile_photo, id))
            
            self.conn.commit()
            logging.info("Membro atualizado com sucesso no banco")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar membro: {e}")
            return False

    def excluir_membro(self, id):
        try:
            self.cur.execute("DELETE FROM time WHERE id = %s", (id,))
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao excluir membro: {e}")
            return False

    def verificar_membros_existentes(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM time")
            count = self.cur.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logging.error(f"Erro ao verificar membros: {e}")
            return False

class LeadRepositorio(Repositorio):
    def criar_lead(self, dados):
        try:
            # Log de depuração detalhado
            logging.info("Iniciando criação de lead")
            logging.info(f"Dados recebidos: {dados}")
            
            # Verificação de campos obrigatórios com logs detalhados
            if not dados.get('nome'):
                logging.error("Erro: Nome é obrigatório")
                return None
            
            if not dados.get('email'):
                logging.error("Erro: Email é obrigatório")
                return None
            
            if not dados.get('vendedor_id'):
                logging.error("Erro: Vendedor ID é obrigatório")
                return None
            
            # Log de verificação de conexão
            logging.info(f"Conexão disponível: {self.conn is not None}")
            logging.info(f"Cursor disponível: {self.cur is not None}")
            
            try:
                # Investigar a situação atual da sequência
                self.cur.execute("SELECT MAX(id) FROM leads")
                max_id = self.cur.fetchone()[0]
                logging.info(f"Máximo ID atual na tabela: {max_id}")
                
                # Inicializar a sequência explicitamente
                self.cur.execute(f"SELECT setval('leads_id_seq', {max_id}, true)")
                logging.info(f"Sequência inicializada para: {max_id}")
                
                # Determinar o valor de venda_fechada
                venda_fechada = dados.get('venda_fechada', False)
                logging.info(f"Valor de venda_fechada: {venda_fechada}")
                
                self.cur.execute("""
                    INSERT INTO leads (
                        nome, empresa, cargo, email, telefone,
                        estagio_atual, vendedor_id, data_criacao,
                        email_comercial, email_comercial_02, email_comercial_03,
                        email_financeiro, telefone_comercial, 
                        cidade, estado, venda_fechada
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    dados.get('nome'),
                    dados.get('empresa'),
                    dados.get('cargo'),
                    dados.get('email'),
                    dados.get('telefone'),
                    dados.get('estagio_atual', 'Novo'),
                    dados.get('vendedor_id'),
                    datetime.now(),
                    dados.get('email_comercial'),
                    dados.get('email_comercial_02'),
                    dados.get('email_comercial_03'),
                    dados.get('email_financeiro'),
                    dados.get('telefone_comercial'),
                    dados.get('cidade'),
                    dados.get('estado'),
                    venda_fechada
                ))
                
                lead_id = self.cur.fetchone()[0]
                
                # Log de sucesso
                logging.info(f"Lead criado com sucesso. ID: {lead_id}")
                
                self.conn.commit()
                return lead_id
            
            except psycopg2.Error as db_error:
                # Log de erro específico do banco de dados
                logging.error(f"Erro de banco de dados ao criar lead: {db_error}")
                logging.error(f"Detalhes do erro: {db_error.pgerror}")
                logging.error(f"Código do erro: {db_error.pgcode}")
                self.conn.rollback()
                return None
            
        except Exception as e:
            # Log de erro geral
            logging.error(f"Erro inesperado ao criar lead: {e}", exc_info=True)
            
            # Tentar fazer rollback
            try:
                self.conn.rollback()
            except:
                logging.error("Erro ao fazer rollback da transação")
            
            return None

    def listar_leads(self):
        try:
            self.cur.execute("""
                SELECT 
                    l.id, 
                    l.nome, 
                    l.empresa, 
                    l.cargo, 
                    l.email, 
                    l.telefone, 
                    l.estagio_atual, 
                    l.vendedor_id, 
                    l.data_criacao,
                    t.nome as vendedor_nome
                FROM leads l
                LEFT JOIN time t ON l.vendedor_id = t.id
                ORDER BY l.data_criacao DESC
            """)
            
            leads = []
            for row in self.cur.fetchall():
                lead = {
                    'id': row[0],
                    'nome': row[1],
                    'empresa': row[2],
                    'cargo': row[3],
                    'email': row[4],
                    'telefone': row[5],
                    'estagio_atual': row[6],
                    'vendedor_id': row[7],
                    'data_criacao': row[8],
                    'vendedor_nome': row[9]
                }
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logging.error(f"Erro ao listar leads: {e}")
            return []

    def buscar_lead_por_id(self, id):
        try:
            self.cur.execute("""
                SELECT 
                    l.id, 
                    l.nome, 
                    l.empresa, 
                    l.cargo, 
                    l.email, 
                    l.telefone, 
                    l.estagio_atual, 
                    l.vendedor_id, 
                    l.data_criacao,
                    t.nome as vendedor_nome,
                    l.venda_fechada,
                    l.email_comercial,
                    l.email_comercial_02,
                    l.email_comercial_03,
                    l.email_financeiro,
                    l.telefone_comercial,
                    l.cidade,
                    l.estado,
                    l.contato_01,
                    l.contato_02,
                    l.observacoes
                FROM leads l
                LEFT JOIN time t ON l.vendedor_id = t.id
                WHERE l.id = %s
            """, (id,))
            
            row = self.cur.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nome': row[1],
                    'empresa': row[2],
                    'cargo': row[3],
                    'email': row[4],
                    'telefone': row[5],
                    'estagio_atual': row[6],
                    'vendedor_id': row[7],
                    'data_criacao': row[8],
                    'vendedor_nome': row[9],
                    'venda_fechada': row[10],
                    'email_comercial': row[11],
                    'email_comercial_02': row[12],
                    'email_comercial_03': row[13],
                    'email_financeiro': row[14],
                    'telefone_comercial': row[15],
                    'cidade': row[16],
                    'estado': row[17],
                    'contato_01': row[18],
                    'contato_02': row[19],
                    'observacoes': row[20]
                }
            return None
            
        except Exception as e:
            logging.error(f"Erro ao buscar lead: {e}")
            return None

    def atualizar_lead(self, id, dados):
        try:
            self.cur.execute("""
                UPDATE leads
                SET nome = %s,
                    empresa = %s,
                    cargo = %s,
                    email = %s,
                    telefone = %s,
                    estagio_atual = %s,
                    vendedor_id = %s,
                    venda_fechada = %s,
                    email_comercial = %s,
                    email_comercial_02 = %s,
                    email_comercial_03 = %s,
                    email_financeiro = %s,
                    telefone_comercial = %s,
                    cidade = %s,
                    estado = %s,
                    contato_01 = %s,
                    contato_02 = %s,
                    observacoes = %s
                WHERE id = %s
                RETURNING id
            """, (
                dados.get('nome'),
                dados.get('empresa'),
                dados.get('cargo'),
                dados.get('email'),
                dados.get('telefone'),
                dados.get('estagio_atual'),
                dados.get('vendedor_id'),
                dados.get('venda_fechada', False),
                dados.get('email_comercial'),
                dados.get('email_comercial_02'),
                dados.get('email_comercial_03'),
                dados.get('email_financeiro'),
                dados.get('telefone_comercial'),
                dados.get('cidade'),
                dados.get('estado'),
                dados.get('contato_01'),
                dados.get('contato_02'),
                dados.get('observacoes'),
                id
            ))
            
            updated = self.cur.fetchone() is not None
            self.conn.commit()
            return updated
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar lead: {e}")
            return False

    def excluir_lead(self, id):
        try:
            self.cur.execute("DELETE FROM leads WHERE id = %s", (id,))
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao excluir lead: {e}")
            return False

    def atualizar_estagio(self, lead_id, novo_estagio):
        try:
            self.cur.execute("""
                UPDATE leads
                SET estagio_atual = %s
                WHERE id = %s
                RETURNING id
            """, (novo_estagio, lead_id))
            
            updated = self.cur.fetchone() is not None
            self.conn.commit()
            return updated
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Erro ao atualizar estágio: {e}")
            return False

    def contar_total_leads(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM leads")
            return self.cur.fetchone()[0]
        except Exception as e:
            logging.error(f"Erro ao contar leads: {e}")
            return 0

    def contar_vendas(self):
        try:
            self.cur.execute("SELECT COUNT(*) FROM leads WHERE venda_fechada = true")
            return self.cur.fetchone()[0]
        except Exception as e:
            logging.error(f"Erro ao contar vendas: {e}")
            return 0

    def agrupar_leads_por_status(self):
        try:
            self.cur.execute("""
                SELECT status, COUNT(*) as total
                FROM leads
                GROUP BY status
            """)
            
            return dict(self.cur.fetchall())
            
        except Exception as e:
            logging.error(f"Erro ao agrupar leads: {e}")
            return {}

    def listar_leads_recentes(self, limite=5):
        try:
            self.cur.execute("""
                SELECT 
                    l.id, 
                    l.nome, 
                    l.empresa, 
                    l.estagio_atual, 
                    l.data_criacao, 
                    t.nome as vendedor_nome
                FROM leads l
                LEFT JOIN time t ON l.vendedor_id = t.id
                ORDER BY l.data_criacao DESC
                LIMIT %s
            """, (limite,))
            
            leads = []
            for row in self.cur.fetchall():
                lead = {
                    'id': row[0],
                    'nome': row[1],
                    'empresa': row[2],
                    'estagio_atual': row[3],
                    'data_criacao': row[4],
                    'vendedor_nome': row[5]
                }
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logging.error(f"Erro ao listar leads recentes: {e}")
            return []

    def contar_leads_por_estado(self):
        try:
            self.cur.execute("""
                SELECT estado, COUNT(*) as total
                FROM leads
                GROUP BY estado
            """)
            
            return dict(self.cur.fetchall())
            
        except Exception as e:
            logging.error(f"Erro ao contar leads por estado: {e}")
            return {}

    def contar_leads_por_regiao(self):
        try:
            # Definir regiões e seus estados
            regioes = {
                'Norte': ['AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO'],
                'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
                'Centro-Oeste': ['DF', 'GO', 'MT', 'MS'],
                'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
                'Sul': ['PR', 'RS', 'SC']
            }
            
            # Buscar contagem por estado
            self.cur.execute("""
                SELECT estado, COUNT(*) as total
                FROM leads
                GROUP BY estado
            """)
            
            leads_por_estado = dict(self.cur.fetchall())
            
            # Calcular total por região
            leads_por_regiao = {regiao: 0 for regiao in regioes.keys()}
            for estado, quantidade in leads_por_estado.items():
                if estado:  # Ignorar estado nulo/vazio
                    for regiao, estados in regioes.items():
                        if estado.upper() in estados:
                            leads_por_regiao[regiao] += quantidade
                            break
            
            return leads_por_regiao
            
        except Exception as e:
            logging.error(f"Erro ao contar leads por região: {e}")
            return {
                'Norte': 0,
                'Nordeste': 0,
                'Centro-Oeste': 0,
                'Sudeste': 0,
                'Sul': 0
            }

    def contar_leads_por_vendedor(self, vendedor_id):
        try:
            self.cur.execute("""
                SELECT COUNT(*) 
                FROM leads 
                WHERE vendedor_id = %s
            """, (vendedor_id,))
            
            return self.cur.fetchone()[0]
        except Exception as e:
            logging.error(f"Erro ao contar leads por vendedor: {e}")
            return 0

    def contar_leads_por_estagio(self):
        try:
            # Definir todos os estágios possíveis
            estagios_possiveis = [
                'Não Iniciado',
                'Enviado Email',
                'Sem retorno Email',
                'Retorno Agendado',
                'Linkedin',
                'Sem Retorno Linkedin',
                'WhatsApp',
                'Sem Retorno WhatsApp',
                'Email Despedida'
            ]
            
            # Consulta para contar leads por estágio
            self.cur.execute("""
                WITH estagios AS (
                    SELECT unnest(%s::text[]) AS estagio
                )
                SELECT 
                    e.estagio, 
                    COALESCE(COUNT(l.id), 0) as total
                FROM estagios e
                LEFT JOIN leads l ON l.estagio_atual = e.estagio
                GROUP BY e.estagio
                ORDER BY total DESC
            """, (estagios_possiveis,))
            
            leads_por_estagio = {}
            for row in self.cur.fetchall():
                leads_por_estagio[row[0]] = row[1]
            
            return leads_por_estagio
            
        except Exception as e:
            logging.error(f"Erro ao contar leads por estágio: {e}")
            return {}

    def pesquisar_leads(self, termo_busca):
        try:
            termo = f"%{termo_busca}%"
            self.cur.execute("""
                SELECT DISTINCT
                    l.id, 
                    l.nome, 
                    l.empresa, 
                    l.cargo, 
                    l.email, 
                    l.telefone, 
                    l.estagio_atual, 
                    l.vendedor_id, 
                    l.data_criacao,
                    t.nome as vendedor_nome
                FROM leads l
                LEFT JOIN time t ON l.vendedor_id = t.id
                WHERE 
                    LOWER(l.nome) LIKE LOWER(%s) OR
                    LOWER(l.email) LIKE LOWER(%s) OR
                    LOWER(l.empresa) LIKE LOWER(%s) OR
                    LOWER(l.cargo) LIKE LOWER(%s) OR
                    LOWER(COALESCE(t.nome, '')) LIKE LOWER(%s)
                ORDER BY l.data_criacao DESC
            """, (termo, termo, termo, termo, termo))
            
            leads = []
            for row in self.cur.fetchall():
                lead = {
                    'id': row[0],
                    'nome': row[1],
                    'empresa': row[2],
                    'cargo': row[3],
                    'email': row[4],
                    'telefone': row[5],
                    'estagio_atual': row[6],
                    'vendedor_id': row[7],
                    'data_criacao': row[8],
                    'vendedor_nome': row[9]
                }
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logging.error(f"Erro ao pesquisar leads: {e}")
            return []

    def buscar_por_estagio(self, estagio):
        try:
            self.cur.execute("""
                SELECT 
                    l.id, 
                    l.nome, 
                    l.empresa, 
                    l.cargo, 
                    l.email, 
                    l.telefone, 
                    l.estagio_atual,
                    l.vendedor_id,
                    l.data_criacao,
                    t.nome as vendedor_nome,
                    t.profile_photo as vendedor_profile_photo
                FROM leads l
                LEFT JOIN time t ON l.vendedor_id = t.id
                WHERE l.estagio_atual = %s
                ORDER BY l.data_criacao DESC
            """, (estagio,))
            
            leads = []
            for row in self.cur.fetchall():
                lead = {
                    'id': row[0],
                    'nome': row[1],
                    'empresa': row[2],
                    'cargo': row[3],
                    'email': row[4],
                    'telefone': row[5],
                    'estagio_atual': row[6],
                    'vendedor_id': row[7],
                    'data_criacao': row[8],
                    'vendedor': {
                        'nome': row[9],
                        'profile_photo': row[10]
                    } if row[9] else None
                }
                leads.append(lead)
            
            return leads
            
        except Exception as e:
            logging.error(f"Erro ao buscar leads por estágio: {e}")
            return []

def criar_conexao():
    try:
        # Carregar variáveis de ambiente
        load_dotenv()

        # Configurações de conexão
        conn_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '6543'),
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'client_encoding': 'LATIN1'
        }

        logging.info(f"Tentando conectar em: {conn_params['host']}:{conn_params['port']} como {conn_params['user']}")
        
        conn = psycopg2.connect(**conn_params)
        return conn
    except Exception as e:
        logging.error(f"Erro detalhado ao criar conexão: {e}")
        logging.error(f"Configurações de conexão: {conn_params}")
        return None

def main():
    conn = criar_conexao()
    if conn:
        time_repo = TimeRepositorio()
        lead_repo = LeadRepositorio()
        
        # Exemplos de uso
        time_repo.criar_membro("João", "joao@example.com", "123456789")
        lead_repo.criar_lead({
            'nome': "João",
            'empresa': "Empresa X",
            'cargo': "Vendedor",
            'email': "joao@example.com",
            'telefone': "123456789",
            'estagio_atual': "Novo",
            'vendedor_id': 1,
            'email_comercial': 'joao.comercial@example.com',
            'email_comercial_02': 'joao.comercial02@example.com',
            'email_comercial_03': 'joao.comercial03@example.com',
            'email_financeiro': 'joao.financeiro@example.com',
            'telefone_comercial': '987654321',
            'cidade': 'São Paulo',
            'estado': 'SP'
        })
        
        membros = time_repo.listar_membros()
        leads = lead_repo.listar_leads()
        
        print(membros)
        print(leads)
        
        conn.close()

if __name__ == "__main__":
    main()
