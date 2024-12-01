from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Text, Boolean, Unicode, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import unicodedata
import re

Base = declarative_base()

class EstagioFunil(enum.Enum):
    NAO_INICIADO = "Não Iniciado"
    ENVIADO_EMAIL = "Enviado Email"
    SEM_RETORNO_EMAIL = "Sem retorno Email"
    RETORNO_AGENDADO = "Retorno Agendado"
    LINKEDIN = "Linkedin"
    SEM_RETORNO_LINKEDIN = "Sem Retorno Linkedin"
    WHATSAPP = "WhatsApp"
    SEM_RETORNO_WHATSAPP = "Sem Retorno WhatsApp"
    EMAIL_DESPEDIDA = "Email Despedida"

class Time(Base):
    __tablename__ = 'time'
    
    id = Column(Integer, primary_key=True)
    nome = Column(Unicode(100), nullable=False)
    email = Column(Unicode(120), unique=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now, nullable=False)
    profile_photo = Column(Unicode(255), nullable=True, default='default_profile.png')
    telefone = Column(Unicode(20), nullable=True)
    leads = Column(Integer, default=0)  # Total de leads atribuídos
    vendas = Column(Integer, default=0)  # Total de vendas fechadas
    
    # Relacionamento com leads
    leads_rel = relationship('Lead', back_populates='vendedor')
    
    def __repr__(self):
        return f"<Time(id={self.id}, nome='{self.nome}', email='{self.email}')>"

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(Unicode(100), nullable=False)
    email = Column(Unicode(100), unique=True)
    telefone = Column(Unicode(20))
    empresa = Column(Unicode(100))
    cargo = Column(Unicode(100))
    estagio_atual = Column(Unicode(50), nullable=False, default='Não Iniciado')
    venda_fechada = Column(Boolean, default=False, nullable=False)
    data_venda = Column(DateTime, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now, nullable=False)
    ultima_interacao = Column(DateTime, nullable=True)
    observacoes = Column(Unicode(500))
    vendedor_id = Column(Integer, ForeignKey('time.id', ondelete='SET NULL'), nullable=True)
    
    # Novos campos
    email_comercial = Column(Unicode(100), nullable=True)
    email_comercial_02 = Column(Unicode(100), nullable=True)
    email_comercial_03 = Column(Unicode(100), nullable=True)
    email_financeiro = Column(Unicode(100), nullable=True)
    telefone_comercial = Column(Unicode(20), nullable=True)
    cidade = Column(Unicode(100), nullable=True)
    estado = Column(Unicode(50), nullable=True)
    contato_01 = Column(Unicode(100), nullable=True)
    contato_02 = Column(Unicode(100), nullable=True)
    
    # Relacionamento com vendedor
    vendedor = relationship('Time', back_populates='leads_rel')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<Lead(nome='{self.nome}', email='{self.email}', estagio='{self.estagio_atual}')>"

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    nome = Column(Unicode(100), nullable=False)
    email = Column(Unicode(100), nullable=False, unique=True)
    senha = Column(Unicode(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    profile_photo = Column(Unicode(255), nullable=True, default='default_profile.png')

    @classmethod
    def normalizar_texto(cls, texto, max_length=100):
        """
        Método robusto para normalizar texto com tratamento de codificação
        """
        if not isinstance(texto, str):
            try:
                texto = str(texto)
            except Exception:
                texto = ''
        
        # Remover acentos
        texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
        
        # Remover caracteres não-alfanuméricos
        texto_normalizado = re.sub(r'[^a-zA-Z0-9\s\.\@]', '', texto_normalizado)
        
        # Truncar para o tamanho máximo
        return texto_normalizado[:max_length].strip()

    def __init__(self, *args, **kwargs):
        # Normalizar campos sensíveis
        if 'nome' in kwargs:
            kwargs['nome'] = self.normalizar_texto(kwargs['nome'], max_length=100)
        
        if 'email' in kwargs:
            kwargs['email'] = self.normalizar_texto(kwargs['email'], max_length=100)
        
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"
