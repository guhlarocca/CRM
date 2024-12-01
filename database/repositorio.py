from sqlalchemy.orm import Session, joinedload
from sqlalchemy import update, delete, func, case
from database.modelos import Lead, EstagioFunil, Time
from datetime import datetime
import calendar

class TimeRepositorio:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def criar_membro(self, nome, email, telefone, profile_photo='default_profile.png'):
        try:
            print("\n--- INÍCIO CRIAÇÃO DE MEMBRO NO REPOSITÓRIO ---")
            print(f"Dados recebidos:")
            print(f"Nome: {nome}")
            print(f"Email: {email}")
            print(f"Telefone: {telefone}")
            print(f"Profile Photo: {profile_photo}")
            
            # Verificar se o email já existe
            print("\nVerificando se membro já existe...")
            try:
                membro_existente = self.sessao.query(Time).filter_by(email=email).first()
            except Exception as query_error:
                print(f"ERRO na consulta de membro existente: {query_error}")
                import traceback
                traceback.print_exc()
                return None
            
            if membro_existente:
                print(f"ERRO: Email {email} já está em uso!")
                print(f"Membro existente - ID: {membro_existente.id}, Nome: {membro_existente.nome}")
                return None
            
            # Criar novo membro
            print("\nCriando novo membro...")
            try:
                novo_membro = Time(
                    nome=nome, 
                    email=email,
                    telefone=telefone,
                    profile_photo=profile_photo,
                    data_criacao=datetime.now(),
                    leads=0,
                    vendas=0
                )
            except Exception as membro_error:
                print(f"ERRO ao criar objeto Time: {membro_error}")
                import traceback
                traceback.print_exc()
                return None
            
            print("\nAdicionando membro à sessão...")
            try:
                self.sessao.add(novo_membro)
            except Exception as add_error:
                print(f"ERRO ao adicionar membro à sessão: {add_error}")
                import traceback
                traceback.print_exc()
                return None
            
            print("\nCommitando alterações...")
            try:
                self.sessao.commit()
                self.sessao.refresh(novo_membro)
            except Exception as commit_error:
                print(f"ERRO ao commitar alterações: {commit_error}")
                import traceback
                traceback.print_exc()
                self.sessao.rollback()
                return None
            
            print("\n--- MEMBRO CRIADO COM SUCESSO ---")
            print(f"ID: {novo_membro.id}")
            print(f"Nome: {novo_membro.nome}")
            print(f"Email: {novo_membro.email}")
            print(f"Telefone: {novo_membro.telefone}")
            print(f"Profile Photo: {novo_membro.profile_photo}")
            
            return novo_membro
            
        except Exception as e:
            print("\n--- ERRO CRÍTICO NA CRIAÇÃO DE MEMBRO ---")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
            
            # Rollback da sessão
            self.sessao.rollback()
            
            return None

    def listar_membros(self):
        """Lista todos os membros do time com suas estatísticas"""
        try:
            print("\n--- INÍCIO Listar Membros ---")
            
            # Verificar se a sessão está ativa
            if not self.sessao:
                print("ERRO: Sessão do banco de dados não inicializada!")
                return []
            
            # Garantir que haja pelo menos um membro
            membros_existentes = self.sessao.query(Time).count()
            if membros_existentes == 0:
                print("Nenhum membro encontrado. Criando membro padrão...")
                try:
                    novo_membro = Time(
                        nome="Vendedor Padrão",
                        email="vendedor_padrao@empresa.com",
                        telefone="(11) 99999-9999",
                        profile_photo='default_profile.png',
                        data_criacao=datetime.now(),
                        leads=0,
                        vendas=0
                    )
                    self.sessao.add(novo_membro)
                    self.sessao.commit()
                except Exception as create_error:
                    print(f"ERRO ao criar membro padrão: {create_error}")
                    self.sessao.rollback()
                    return []
            
            # Buscar todos os membros
            try:
                membros = self.sessao.query(Time).all()
            except Exception as query_error:
                print(f"ERRO ao buscar membros: {query_error}")
                import traceback
                traceback.print_exc()
                return []
            
            # Converter membros para dicionários
            resultado = []
            for membro in membros:
                try:
                    membro_dict = {
                        'id': membro.id,
                        'nome': membro.nome or 'Vendedor Sem Nome',
                        'email': membro.email or 'sem_email@empresa.com',
                        'telefone': membro.telefone or 'Não informado',
                        'profile_photo': membro.profile_photo or 'default_profile.png',
                        'data_criacao': membro.data_criacao.strftime('%d/%m/%Y') if membro.data_criacao else 'Data não definida',
                        'leads': membro.leads or 0,
                        'vendas': membro.vendas or 0
                    }
                    resultado.append(membro_dict)
                except Exception as membro_error:
                    print(f"ERRO ao processar membro: {membro_error}")
                    import traceback
                    traceback.print_exc()
            
            print(f"\n--- FIM Listar Membros ---")
            print(f"Total de membros processados: {len(resultado)}")
            
            return resultado
        
        except Exception as e:
            print(f"\n--- ERRO CRÍTICO ao listar membros ---")
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            return []

    def buscar_membro_por_id(self, id):
        try:
            print(f"\n--- INÍCIO Buscar Membro por ID ---")
            print(f"ID procurado: {id}")
            
            # Verificar se a sessão está ativa
            if not self.sessao:
                print("ERRO: Sessão do banco de dados não inicializada!")
                return None
            
            # Buscar membro
            membro = self.sessao.query(Time).filter_by(id=id).first()
            
            # Log de resultado
            if membro:
                print("Membro encontrado:")
                print(f"ID: {membro.id}")
                print(f"Nome: {membro.nome}")
                print(f"Email: {membro.email}")
                print(f"Telefone: {membro.telefone}")
                print(f"Foto de Perfil: {membro.profile_photo}")
            else:
                print(f"Nenhum membro encontrado com ID {id}")
            
            return membro
        
        except Exception as e:
            print(f"\n--- ERRO ao buscar membro por ID ---")
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            return None

    def atualizar_estatisticas(self, membro_id):
        try:
            membro = self.buscar_membro_por_id(membro_id)
            if not membro:
                print(f"Membro {membro_id} não encontrado")
                return False
            
            # Buscar contagem de leads e vendas
            leads = self.sessao.query(Lead).filter_by(vendedor_id=membro_id).all()
            
            total_leads = len(leads)
            total_vendas = len([lead for lead in leads if lead.venda_fechada])
            
            print(f"Estatísticas para membro {membro_id} - {membro.nome}:")
            print(f"Total de leads: {total_leads}")
            print(f"Total de vendas: {total_vendas}")
            
            # Atualizar campos do membro
            membro.leads = total_leads
            membro.vendas = total_vendas
            
            # Commit das alterações
            self.sessao.commit()
            print(f"Estatísticas atualizadas para membro {membro_id}")
            return True
            
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao atualizar estatísticas: {e}")
            return False

    def atualizar_membro(self, membro_id, nome, email, telefone, profile_photo=None):
        try:
            membro = self.sessao.query(Time).filter_by(id=membro_id).first()
            if not membro:
                return None
        
            membro.nome = nome
            membro.email = email
            membro.telefone = telefone
        
            # Atualizar foto de perfil APENAS se uma nova foto for fornecida
            if profile_photo and profile_photo != 'default_profile.png' and profile_photo != membro.profile_photo:
                print(f"Atualizando foto de perfil: {profile_photo}")
                membro.profile_photo = profile_photo
            else:
                print("Mantendo foto de perfil existente")
        
            self.sessao.commit()
            return membro
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao atualizar membro: {e}")
            return None

    def incrementar_vendas(self, membro_id):
        try:
            membro = self.buscar_membro_por_id(membro_id)
            if not membro:
                print(f"Membro {membro_id} não encontrado")
                return False
            
            membro.vendas += 1
            
            # Commit das alterações
            self.sessao.commit()
            print(f"Vendas incrementadas para membro {membro_id}")
            return True
            
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao incrementar vendas: {e}")
            return False

    def decrementar_vendas(self, membro_id):
        try:
            membro = self.buscar_membro_por_id(membro_id)
            if not membro:
                print(f"Membro {membro_id} não encontrado")
                return False
            
            # Garantir que o valor não fique negativo
            membro.vendas = max(0, membro.vendas - 1)
            
            # Commit das alterações
            self.sessao.commit()
            print(f"Vendas decrementadas para membro {membro_id}. Novo valor: {membro.vendas}")
            return True
            
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao decrementar vendas: {e}")
            import traceback
            traceback.print_exc()
            return False

    def contar_total_times(self):
        try:
            total = self.sessao.query(func.count(Time.id)).scalar()
            print(f"Total de membros no time: {total}")
            return total
        except Exception as e:
            print(f"Erro ao contar total de times: {e}")
            return 0

    def verificar_membros_existentes(self):
        """Verifica se existem membros no banco de dados"""
        try:
            print("\n--- Verificação de Membros Existentes ---")
            
            # Verificar se a sessão está ativa
            print("Verificando estado da sessão...")
            if not self.sessao:
                print("ERRO: Sessão não inicializada!")
                return False
            
            # Preparar consulta
            print("Preparando consulta de membros...")
            try:
                membros_query = self.sessao.query(Time)
            except Exception as query_prep_error:
                print(f"ERRO ao preparar consulta: {query_prep_error}")
                import traceback
                traceback.print_exc()
                return False
            
            # Executar consulta
            try:
                membros = membros_query.all()
            except Exception as query_error:
                print(f"ERRO na consulta de membros: {query_error}")
                import traceback
                traceback.print_exc()
                return False
            
            # Verificar resultado da consulta
            if not membros:
                print("Nenhum membro encontrado no banco de dados!")
                return False
            
            # Imprimir detalhes dos membros
            print(f"Encontrados {len(membros)} membros:")
            for membro in membros:
                try:
                    print(f"ID: {membro.id}, Nome: {membro.nome}, Email: {membro.email}, Telefone: {membro.telefone}, Profile Photo: {membro.profile_photo}")
                except Exception as membro_print_error:
                    print(f"ERRO ao imprimir detalhes do membro: {membro_print_error}")
            
            return True
        
        except Exception as e:
            print(f"Erro crítico ao verificar membros existentes: {e}")
            import traceback
            traceback.print_exc()
            return False

    def atualizar_estatisticas_membros(self, membros_time):
        """Atualiza estatísticas de leads e vendas para cada membro do time"""
        try:
            print("\n--- INÍCIO Atualizar Estatísticas Membros ---")
            
            # Verificar se membros_time está vazio
            if not membros_time:
                print("AVISO: membros_time está vazio!")
                return []
            
            # Inicializar repositório de leads
            lead_repo = LeadRepositorio(self.sessao)
            
            # Atualizar estatísticas de cada membro
            for membro in membros_time:
                print(f"\nProcessando membro: {membro}")
                
                # Verificar se o membro tem 'id'
                if 'id' not in membro:
                    print(f"ERRO: Membro sem 'id': {membro}")
                    continue
                
                # Contar leads e vendas
                leads = lead_repo.contar_leads_por_vendedor(membro['id'])
                vendas = lead_repo.contar_vendas_por_vendedor(membro['id'])
                
                print(f"Membro {membro['nome']} - Leads: {leads}, Vendas: {vendas}")
                
                # Atualizar dicionário do membro
                membro['leads'] = leads
                membro['vendas'] = vendas
                
                # Atualizar o registro do membro no banco de dados
                try:
                    membro_db = self.sessao.query(Time).filter_by(id=membro['id']).first()
                    if membro_db:
                        membro_db.leads = leads
                        membro_db.vendas = vendas
                    else:
                        print(f"ERRO: Membro não encontrado no banco de dados - ID: {membro['id']}")
                except Exception as db_error:
                    print(f"Erro ao atualizar membro no banco de dados: {db_error}")
                    import traceback
                    traceback.print_exc()
            
            # Commit das alterações
            try:
                self.sessao.commit()
                print("Alterações commitadas com sucesso!")
            except Exception as commit_error:
                print(f"Erro ao commitar alterações: {commit_error}")
                self.sessao.rollback()
                import traceback
                traceback.print_exc()
            
            print("\n--- FIM Atualizar Estatísticas Membros ---")
            return membros_time
        
        except Exception as e:
            print(f"Erro crítico ao atualizar estatísticas dos membros: {e}")
            import traceback
            traceback.print_exc()
            return []

    def excluir_membro(self, membro_id):
        try:
            print(f"\n--- INÍCIO Excluir Membro ---")
            print(f"ID do Membro a ser excluído: {membro_id}")
            
            # Verificar se a sessão está ativa
            if not self.sessao:
                print("ERRO: Sessão do banco de dados não inicializada!")
                return False
            
            # Buscar o membro
            membro = self.sessao.query(Time).filter_by(id=membro_id).first()
            
            if not membro:
                print(f"Membro com ID {membro_id} não encontrado")
                return False
            
            # Verificar se o membro tem leads associados
            from .modelos import Lead
            leads_associados = self.sessao.query(Lead).filter_by(vendedor_id=membro_id).count()
            
            if leads_associados > 0:
                print(f"ERRO: Não é possível excluir o membro. Existem {leads_associados} leads associados.")
                return False
            
            # Excluir o membro
            self.sessao.delete(membro)
            self.sessao.commit()
            
            print(f"Membro {membro_id} excluído com sucesso!")
            return True
        
        except Exception as e:
            self.sessao.rollback()
            print(f"\n--- ERRO ao excluir membro ---")
            print(f"Erro: {e}")
            import traceback
            traceback.print_exc()
            return False

class LeadRepositorio:
    def __init__(self, sessao=None):
        self.sessao = sessao or criar_sessao()

    def adicionar_lead(self, dados_lead: dict):
        """Adiciona um novo lead ao banco de dados"""
        try:
            # Criar instância de Lead com os dados fornecidos
            novo_lead = Lead(**dados_lead)
            
            # Definir data de criação e última interação se não fornecidas
            if not novo_lead.data_criacao:
                novo_lead.data_criacao = datetime.now()
            if not novo_lead.ultima_interacao:
                novo_lead.ultima_interacao = datetime.now()
            
            # Adicionar e commitar
            self.sessao.add(novo_lead)
            self.sessao.commit()
            return novo_lead
        except Exception as e:
            self.sessao.rollback()
            raise e

    def criar_lead(self, dados):
        """
        Cria um novo lead no banco de dados
        """
        try:
            print(f"\n=== Criando Novo Lead ===")
            print(f"Dados recebidos: {dados}")
            
            novo_lead = Lead(
                nome=dados['nome'],
                email=dados['email'],
                telefone=dados.get('telefone'),
                empresa=dados.get('empresa'),
                cargo=dados.get('cargo'),
                estagio_atual=dados.get('estagio_atual', 'Não Iniciado'),
                vendedor_id=dados.get('vendedor_id')
            )
            
            self.sessao.add(novo_lead)
            
            # Atualizar contador de leads do vendedor
            if novo_lead.vendedor_id:
                vendedor = self.sessao.query(Time).filter_by(id=novo_lead.vendedor_id).first()
                if vendedor:
                    vendedor.leads = vendedor.leads + 1
            
            self.sessao.commit()
            print(f"Lead criado com sucesso! ID: {novo_lead.id}")
            return novo_lead
            
        except Exception as e:
            print(f"Erro ao criar lead: {e}")
            import traceback
            traceback.print_exc()
            self.sessao.rollback()
            raise

    def obter_lead_por_id(self, lead_id: int):
        """Busca um lead pelo ID"""
        return self.sessao.query(Lead).filter(Lead.id == lead_id).first()

    def buscar_lead_por_id(self, lead_id):
        try:
            lead = self.sessao.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise ValueError(f"Lead com ID {lead_id} não encontrado")
            
            # Log detalhado de todos os campos ao buscar lead
            print(f"\n--- DETALHES DO LEAD {lead_id} ---")
            for column in lead.__table__.columns:
                print(f"{column.name}: {getattr(lead, column.name)}")
            
            return lead
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao buscar lead: {e}")
            raise e

    def obter_lead_por_email(self, email):
        """Busca um lead pelo email"""
        return self.sessao.query(Lead).filter(Lead.email == email).first()

    def listar_leads(self, estagio: str = None):
        """Lista todos os leads, opcionalmente filtrados por estágio"""
        try:
            print(f"\n=== Listando Leads ===")
            print(f"Filtro de estágio: {estagio}")
            
            # Verificar se a sessão está válida
            if not self.sessao:
                print("ERRO: Sessão do banco de dados não inicializada!")
                return []
            
            # Usar joinedload para carregar o relacionamento com vendedor
            query = self.sessao.query(Lead).options(
                joinedload(Lead.vendedor)  # Garantir que o vendedor seja carregado
            )
            
            if estagio:
                query = query.filter(Lead.estagio_atual == estagio)
            
            # Ordenar por ID decrescente (mais recentes primeiro)
            query = query.order_by(Lead.id.desc())
            
            # Limitar o número de resultados para melhorar performance
            query = query.limit(500)
            
            # Executar a query e capturar exceções
            try:
                leads = query.all()
                
                # Log detalhado de cada lead
                print("\n--- DETALHES DOS LEADS ---")
                for lead in leads:
                    print(f"\nLead ID: {lead.id}")
                    for column in lead.__table__.columns:
                        valor = getattr(lead, column.name)
                        print(f"{column.name}: {valor}")
                
                return leads
            except Exception as query_error:
                print(f"ERRO ao executar query de leads: {query_error}")
                import traceback
                traceback.print_exc()
                return []
            
        except Exception as e:
            print(f"ERRO geral ao listar leads: {e}")
            import traceback
            traceback.print_exc()
            return []

    def atualizar_lead(self, lead):
        try:
            # Guardar o vendedor_id antigo para atualizar estatísticas
            vendedor_id_antigo = lead.vendedor_id
            
            # Atualizar última interação
            lead.ultima_interacao = datetime.now()
            
            # Refresh do lead para garantir dados atualizados
            self.sessao.refresh(lead)
            
            # Commit das alterações
            self.sessao.commit()
            
            print(f"\nLead {lead.id} atualizado:")
            print(f"Nome: {lead.nome}")
            print(f"Vendedor ID: {lead.vendedor_id}")
            
            # Atualizar estatísticas dos vendedores envolvidos
            time_repo = TimeRepositorio(self.sessao)
            
            # Atualizar estatísticas do vendedor antigo se houver
            if vendedor_id_antigo:
                time_repo.atualizar_estatisticas(vendedor_id_antigo)
            
            # Atualizar estatísticas do novo vendedor se houver e for diferente do antigo
            if lead.vendedor_id and lead.vendedor_id != vendedor_id_antigo:
                time_repo.atualizar_estatisticas(lead.vendedor_id)
                
            return lead
        except Exception as e:
            self.sessao.rollback()
            print(f"Erro ao atualizar lead: {e}")
            raise e

    def excluir_lead(self, lead_id):
        lead = self.sessao.query(Lead).get(lead_id)
        if lead:
            # Atualiza estatísticas do vendedor
            if lead.vendedor:
                lead.vendedor.leads -= 1
                if lead.venda_fechada:
                    lead.vendedor.vendas -= 1
            
            self.sessao.delete(lead)
            self.sessao.commit()
            return True
        return False

    def atualizar_estagio(self, lead_id: int, novo_estagio: str):
        """Atualiza o estágio do funil de um lead"""
        try:
            lead = self.obter_lead_por_id(lead_id)
            if lead:
                lead.estagio_atual = novo_estagio
                lead.ultima_interacao = datetime.now()
                self.sessao.commit()
            return lead
        except Exception as e:
            self.sessao.rollback()
            raise e

    def remover_lead(self, lead_id: int):
        """Remove um lead do banco de dados"""
        try:
            # Buscar o lead com opção de joinedload para evitar problemas de sessão
            lead = self.sessao.query(Lead).options(joinedload(Lead.vendedor)).filter(Lead.id == lead_id).first()
            
            if not lead:
                print(f"Lead com ID {lead_id} não encontrado.")
                return None
            
            # Guardar o vendedor_id e status de venda fechada para atualizar estatísticas
            vendedor_id = lead.vendedor_id
            venda_fechada = lead.venda_fechada
            
            # Log detalhado
            print("\n--- REMOVENDO LEAD ---")
            print(f"Lead ID: {lead.id}")
            print(f"Nome: {lead.nome}")
            print(f"Vendedor ID: {vendedor_id}")
            print(f"Venda Fechada: {venda_fechada}")
            
            # Remover o lead
            self.sessao.delete(lead)
            
            # Commit da transação
            self.sessao.commit()
            
            # Atualizar estatísticas do vendedor
            if vendedor_id:
                time_repo = TimeRepositorio(self.sessao)
                
                # Atualizar estatísticas gerais do vendedor
                time_repo.atualizar_estatisticas(vendedor_id)
                
                # Se o lead tinha venda fechada, subtrair uma venda
                if venda_fechada:
                    time_repo.decrementar_vendas(vendedor_id)
            
            print(f"Lead {lead_id} removido com sucesso.")
            return lead
        
        except Exception as e:
            # Rollback em caso de erro
            self.sessao.rollback()
            print(f"Erro ao remover lead {lead_id}: {e}")
            import traceback
            traceback.print_exc()
            raise

    def buscar_leads_por_nome(self, nome: str):
        """Busca leads por nome (busca parcial)"""
        return self.sessao.query(Lead).filter(Lead.nome.ilike(f'%{nome}%')).all()

    def buscar_leads_por_email(self, email: str):
        """Busca leads por email (busca parcial)"""
        return self.sessao.query(Lead).filter(Lead.email.ilike(f'%{email}%')).all()

    def contar_total_leads(self):
        try:
            return self.sessao.query(Lead).count()
        except Exception as e:
            print(f"Erro ao contar total de leads: {e}")
            return 0

    def contar_leads_por_estagio(self, estagio):
        """Conta o número de leads em um determinado estágio"""
        try:
            return self.sessao.query(Lead).filter(Lead.estagio_atual == estagio).count()
        except Exception as e:
            print(f"Erro ao contar leads por estágio {estagio}: {e}")
            return 0

    def contar_leads_em_andamento(self):
        try:
            estagios_andamento = [
                'Enviado Email', 
                'Sem retorno Email', 
                'Retorno Agendado', 
                'Linkedin', 
                'Sem Retorno Linkedin', 
                'WhatsApp', 
                'Sem Retorno WhatsApp'
            ]
            return self.sessao.query(Lead).filter(Lead.estagio_atual.in_(estagios_andamento)).count()
        except Exception as e:
            print(f"Erro ao contar leads em andamento: {e}")
            return 0

    def contar_leads_fechados(self):
        try:
            return self.sessao.query(Lead).filter_by(venda_fechada=True).count()
        except Exception as e:
            print(f"Erro ao contar leads fechados: {e}")
            return 0

    def listar_leads_recentes(self, limite=5):
        try:
            leads = self.sessao.query(Lead).options(joinedload(Lead.vendedor)).order_by(Lead.data_criacao.desc()).limit(limite).all()
            
            # Converter leads para dicionário
            leads_recentes = []
            for lead in leads:
                vendedor_dict = None
                if lead.vendedor:
                    vendedor_dict = {
                        'id': lead.vendedor.id,
                        'nome': lead.vendedor.nome,
                        'profile_photo': lead.vendedor.profile_photo or 'default_profile.png'
                    }

                lead_dict = {
                    'nome': lead.nome,
                    'email': lead.email,
                    'telefone': lead.telefone,
                    'data_criacao': lead.data_criacao,
                    'venda_fechada': lead.venda_fechada,
                    'estagio': lead.estagio_atual,
                    'vendedor': vendedor_dict
                }
                leads_recentes.append(lead_dict)
            
            return leads_recentes
        except Exception as e:
            print(f"Erro ao listar leads recentes: {e}")
            import traceback
            traceback.print_exc()
            return []

    def fechar_venda(self, lead_id):
        """Marca um lead como venda fechada"""
        try:
            lead = self.sessao.query(Lead).filter_by(id=lead_id).first()
            if not lead:
                return False
            
            lead.venda_fechada = True
            lead.data_venda = datetime.now()
            
            # Atualizar contador de vendas do vendedor
            if lead.vendedor_id:
                vendedor = self.sessao.query(Time).filter_by(id=lead.vendedor_id).first()
                if vendedor:
                    vendedor.vendas = vendedor.vendas + 1
            
            self.sessao.commit()
            return True
        except Exception as e:
            print(f"Erro ao fechar venda: {e}")
            self.sessao.rollback()
            return False

    def editar_lead(self, lead_id, dados):
        try:
            # Log inicial dos dados recebidos
            print("\n--- DADOS RECEBIDOS PARA EDIÇÃO ---")
            for key, value in dados.items():
                print(f"{key}: {value}")
            
            lead = self.sessao.query(Lead).get(lead_id)
            if not lead:
                raise ValueError("Lead não encontrado")
            
            # Campos de contato
            contato_campos = [
                'contato_01', 
                'contato_02', 
                'cidade', 
                'estado', 
                'email_comercial', 
                'email_comercial_02', 
                'email_comercial_03', 
                'email_financeiro', 
                'telefone_comercial'
            ]
            
            # Atualizar campos de contato
            for campo in contato_campos:
                valor = dados.get(campo)
                # Só atualiza se o valor for diferente de None
                if valor is not None:
                    setattr(lead, campo, valor)
                    print(f"Atualizando {campo}: {valor}")
            
            # Outros campos padrão
            lead.nome = dados.get('nome', lead.nome)
            lead.email = dados.get('email', lead.email)
            lead.telefone = dados.get('telefone', lead.telefone)
            lead.empresa = dados.get('empresa', lead.empresa)
            lead.cargo = dados.get('cargo', lead.cargo)
            lead.estagio_atual = dados.get('estagio_atual', lead.estagio_atual)
            lead.observacoes = dados.get('observacoes', lead.observacoes)
            lead.vendedor_id = dados.get('vendedor_id', lead.vendedor_id)
            
            # Processar venda_fechada
            venda_fechada = dados.get('venda_fechada', lead.venda_fechada)
            if isinstance(venda_fechada, str):
                venda_fechada = venda_fechada.lower() == 'true'
            else:
                venda_fechada = bool(venda_fechada)
            lead.venda_fechada = venda_fechada
            
            # Atualizar última interação
            lead.ultima_interacao = datetime.now()
            
            # Log detalhado antes do commit
            print("\n--- ESTADO FINAL DO LEAD ANTES DO COMMIT ---")
            for column in lead.__table__.columns:
                valor = getattr(lead, column.name)
                print(f"{column.name}: {valor}")
            
            # Commit das alterações
            self.sessao.commit()
            
            print("\n--- LEAD EDITADO COM SUCESSO ---")
            return lead
        
        except Exception as e:
            print(f"\nERRO ao editar lead: {e}")
            import traceback
            traceback.print_exc()
            self.sessao.rollback()
            raise e

    def contar_leads(self):
        """Conta o número total de leads"""
        try:
            return self.sessao.query(Lead).count()
        except Exception as e:
            print(f"Erro ao contar leads: {e}")
            return 0

    def contar_vendas(self):
        """Conta o número total de vendas fechadas"""
        try:
            return self.sessao.query(Lead).filter(Lead.venda_fechada == True).count()
        except Exception as e:
            print(f"Erro ao contar vendas: {e}")
            return 0

    def contar_leads_por_vendedor(self, vendedor_id):
        """Contar total de leads por vendedor"""
        try:
            total_leads = self.sessao.query(Lead).filter(Lead.vendedor_id == vendedor_id).count()
            print(f"Debug - Total de Leads para Vendedor {vendedor_id}: {total_leads}")
            return total_leads
        except Exception as e:
            print(f"Erro ao contar leads do vendedor {vendedor_id}: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def contar_vendas_por_vendedor(self, vendedor_id):
        """Contar total de vendas fechadas por vendedor"""
        try:
            total_vendas = self.sessao.query(Lead).filter(
                Lead.vendedor_id == vendedor_id,
                Lead.venda_fechada == True
            ).count()
            print(f"Debug - Total de Vendas para Vendedor {vendedor_id}: {total_vendas}")
            return total_vendas
        except Exception as e:
            print(f"Erro ao contar vendas do vendedor {vendedor_id}: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def agrupar_leads_por_status(self):
        """Agrupa leads por seu estágio atual"""
        try:
            # Consulta para contar leads por estágio
            resultados = self.sessao.query(
                Lead.estagio_atual,
                func.count(Lead.id).label('total')
            ).group_by(Lead.estagio_atual).all()
            
            # Criar dicionário com todos os estágios possíveis inicializados com 0
            todos_estagios = {
                'Não Iniciado': 0,
                'Enviado Email': 0,
                'Sem retorno Email': 0,
                'Retorno Agendado': 0,
                'Linkedin': 0,
                'Sem Retorno Linkedin': 0,
                'WhatsApp': 0,
                'Sem Retorno WhatsApp': 0,
                'Email Despedida': 0
            }
            
            # Atualizar contagens para os estágios que têm leads
            for estagio, total in resultados:
                if estagio in todos_estagios:
                    todos_estagios[estagio] = total
            
            print("Debug - Contagem de leads por estágio:")
            for estagio, total in todos_estagios.items():
                print(f"{estagio}: {total}")
            
            return todos_estagios
            
        except Exception as e:
            print(f"Erro ao agrupar leads por status: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def listar_leads_nao_fechados(self):
        """Lista todos os leads que não são vendas fechadas"""
        try:
            # Usar joinedload para carregar o relacionamento com vendedor
            query = self.sessao.query(Lead).options(joinedload(Lead.vendedor))
            
            # Filtrar leads que não estão no estágio 'Email Despedida'
            query = query.filter(Lead.estagio_atual != 'Email Despedida')
            
            # Ordenar por ID decrescente (mais recentes primeiro)
            query = query.order_by(Lead.id.desc())
            
            return query.all()
            
        except Exception as e:
            print(f"Erro ao listar leads não fechados: {e}")
            return []
        except Exception as e:
            print(f"Erro ao listar leads não fechados: {e}")
            return []

    def buscar_por_estagio(self, estagio: str):
        """
        Busca todos os leads em um determinado estágio
        """
        try:
            return (
                self.sessao.query(Lead)
                .filter(Lead.estagio_atual == estagio)
                .order_by(Lead.data_criacao.desc())
                .all()
            )
        except Exception as e:
            print(f"Erro ao buscar leads por estágio: {e}")
            return []

    def contar_leads_por_estado(self):
        """
        Conta o número de leads por estado
        :return: Dicionário com estados e quantidade de leads
        """
        try:
            # Usar func.count para contar leads por estado
            resultado = self.sessao.query(
                Lead.estado, 
                func.count(Lead.id).label('total_leads')
            ).group_by(Lead.estado).all()
            
            # Converter resultado para dicionário
            leads_por_estado = {
                estado or 'Não Informado': total 
                for estado, total in resultado
            }
            
            return leads_por_estado
        except Exception as e:
            print(f"Erro ao contar leads por estado: {e}")
            return {}
