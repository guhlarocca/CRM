# CRM de Vendas

## Descrição
Sistema de Gerenciamento de Relacionamento com Clientes (CRM) focado no funil de vendas, desenvolvido em Python.

## Estágios do Funil de Vendas
- Enviado Email
- Sem retorno Email
- Retorno Agendado
- Linkedin
- Sem Retorno Linkedin
- WhatsApp
- Sem Retorno WhatsApp
- Email Despedida

## Tecnologias Utilizadas
- Python
- SQLAlchemy
- PyQt5
- SQL Server

## Configuração do Ambiente
1. Crie um ambiente virtual
2. Instale as dependências: `pip install -r requirements.txt`

## Configuração do Banco de Dados
Configurações de conexão com SQL Server no arquivo `.env`

## Instalação
```bash
git clone [url-do-repositorio]
cd crm_vendas
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Execução
```bash
python main.py
```
