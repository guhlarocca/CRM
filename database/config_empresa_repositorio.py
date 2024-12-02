from .modelos import ConfiguracaoEmpresa
from .conexao_supabase import criar_cliente_supabase
from datetime import datetime
import logging

class ConfigEmpresaRepositorio:
    def __init__(self):
        self.supabase = criar_cliente_supabase()
        
    def obter_configuracao(self):
        """Obtém a configuração atual da empresa"""
        try:
            response = self.supabase.table('configuracoes_empresa').select('*').execute()
            if response.data and len(response.data) > 0:
                logging.info("Configuração existente encontrada")
                return response.data[0]
            
            logging.info("Nenhuma configuração encontrada, criando configuração padrão")
            # Se não existir configuração, cria uma com valores padrão
            config_padrao = {
                'nome_sistema': 'CRM Vendas',
                'logo_url': None,
                'primary_color': '#1a1c20',
                'secondary_color': '#292d33',
                'accent_color': '#00d9ff'
            }
            
            response = self.supabase.table('configuracoes_empresa').insert(config_padrao).execute()
            if response.data:
                logging.info("Configuração padrão criada com sucesso")
                return response.data[0]
                
            logging.error("Falha ao criar configuração padrão")
            return None
            
        except Exception as e:
            logging.error(f"Erro ao obter configuração: {str(e)}")
            return None

    def atualizar_configuracao(self, config_data):
        """Atualiza a configuração da empresa"""
        try:
            config_atual = self.obter_configuracao()
            if not config_atual:
                logging.error("Nenhuma configuração encontrada para atualizar")
                return None
            
            logging.info(f"Atualizando configurações: {config_data}")
            # Remover campos None do dicionário
            config_data = {k: v for k, v in config_data.items() if v is not None}
            
            response = self.supabase.table('configuracoes_empresa')\
                .update(config_data)\
                .eq('id', config_atual['id'])\
                .execute()
                
            if response.data and len(response.data) > 0:
                logging.info("Configurações atualizadas com sucesso")
                return response.data[0]
            
            logging.error("Nenhum dado retornado após atualização")
            return None
                
        except Exception as e:
            logging.error(f"Erro ao atualizar configurações: {str(e)}")
            return None

    def atualizar_logo(self, logo_url):
        """Atualiza apenas a URL da logo"""
        try:
            config_atual = self.obter_configuracao()
            if not config_atual:
                logging.error("Nenhuma configuração encontrada para atualizar logo")
                return None
                
            logging.info(f"Atualizando logo: {logo_url}")
            response = self.supabase.table('configuracoes_empresa')\
                .update({'logo_url': logo_url})\
                .eq('id', config_atual['id'])\
                .execute()
                
            if response.data and len(response.data) > 0:
                logging.info("Logo atualizada com sucesso")
                return response.data[0]
            
            logging.error("Nenhum dado retornado após atualização da logo")
            return None
                
        except Exception as e:
            logging.error(f"Erro ao atualizar logo: {str(e)}")
            return None
