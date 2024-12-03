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
            # Primeiro, tenta obter apenas as colunas básicas
            response = self.supabase.table('configuracoes_empresa').select('id,nome_sistema,logo_url').execute()
            
            if response.data and len(response.data) > 0:
                config = response.data[0]
                # Adiciona as cores padrão se não existirem
                config.setdefault('primary_color', '#1a1c20')
                config.setdefault('secondary_color', '#292d33')
                config.setdefault('accent_color', '#00d9ff')
                logging.info("Configuração existente encontrada")
                return config
            
            logging.info("Nenhuma configuração encontrada, criando configuração padrão")
            # Se não existir configuração, cria uma com valores padrão
            config_padrao = {
                'nome_sistema': 'CRM Vendas',
                'logo_url': None,
                'primary_color': '#1a1c20',
                'secondary_color': '#292d33',
                'accent_color': '#00d9ff'
            }
            
            # Filtra apenas as colunas que existem na tabela
            config_insert = {
                'nome_sistema': config_padrao['nome_sistema'],
                'logo_url': config_padrao['logo_url']
            }
            
            response = self.supabase.table('configuracoes_empresa').insert(config_insert).execute()
            if response.data:
                config = response.data[0]
                # Adiciona as cores padrão
                config.update({
                    'primary_color': config_padrao['primary_color'],
                    'secondary_color': config_padrao['secondary_color'],
                    'accent_color': config_padrao['accent_color']
                })
                logging.info("Configuração padrão criada com sucesso")
                return config
                
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
            # Mantém apenas as colunas que existem na tabela
            config_update = {
                'nome_sistema': config_data.get('nome_sistema'),
                'logo_url': config_data.get('logo_url')
            }
            
            # Remove campos None do dicionário
            config_update = {k: v for k, v in config_update.items() if v is not None}
            
            response = self.supabase.table('configuracoes_empresa')\
                .update(config_update)\
                .eq('id', config_atual['id'])\
                .execute()
                
            if response.data and len(response.data) > 0:
                config = response.data[0]
                # Mantém as cores padrão
                config.update({
                    'primary_color': config_data.get('primary_color', '#1a1c20'),
                    'secondary_color': config_data.get('secondary_color', '#292d33'),
                    'accent_color': config_data.get('accent_color', '#00d9ff')
                })
                logging.info("Configurações atualizadas com sucesso")
                return config
            
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
