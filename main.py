import sys
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from database.repositorio import LeadRepositorio
from database.conexao import ConexaoBanco

class CRMApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.title("CRM Vendas")
        self.geometry("1200x800")

        # Inicializar conexão com banco de dados
        conexao = ConexaoBanco()
        self.sessao = conexao.criar_sessao()
        self.repositorio = LeadRepositorio(self.sessao)

        # Criar abas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Aba de Cadastro
        self.cadastro_tab = self.tabview.add("Cadastro de Leads")
        self.setup_cadastro_tab()

        # Aba de Listagem
        self.listagem_tab = self.tabview.add("Listagem de Leads")
        self.setup_listagem_tab()

        # Carregar dados iniciais
        self.carregar_leads()

    def setup_cadastro_tab(self):
        # Layout de cadastro
        layout_frame = ctk.CTkFrame(self.cadastro_tab)
        layout_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Nome
        ctk.CTkLabel(layout_frame, text="Nome:").pack(pady=(10, 0))
        self.nome_input = ctk.CTkEntry(layout_frame, width=400)
        self.nome_input.pack(pady=(0, 10))

        # Email
        ctk.CTkLabel(layout_frame, text="Email:").pack(pady=(10, 0))
        self.email_input = ctk.CTkEntry(layout_frame, width=400)
        self.email_input.pack(pady=(0, 10))

        # Telefone
        ctk.CTkLabel(layout_frame, text="Telefone:").pack(pady=(10, 0))
        self.telefone_input = ctk.CTkEntry(layout_frame, width=400)
        self.telefone_input.pack(pady=(0, 10))

        # Empresa
        ctk.CTkLabel(layout_frame, text="Empresa:").pack(pady=(10, 0))
        self.empresa_input = ctk.CTkEntry(layout_frame, width=400)
        self.empresa_input.pack(pady=(0, 10))

        # Cargo
        ctk.CTkLabel(layout_frame, text="Cargo:").pack(pady=(10, 0))
        self.cargo_input = ctk.CTkEntry(layout_frame, width=400)
        self.cargo_input.pack(pady=(0, 10))

        # Estágio
        ctk.CTkLabel(layout_frame, text="Estágio:").pack(pady=(10, 0))
        self.estagio_combo = ctk.CTkComboBox(layout_frame, values=[
            "Enviado Email",
            "Sem retorno Email",
            "Retorno Agendado",
            "Linkedin",
            "Sem Retorno Linkedin",
            "WhatsApp",
            "Sem Retorno WhatsApp",
            "Email Despedida"
        ], width=400)
        self.estagio_combo.pack(pady=(0, 10))

        # Observações
        ctk.CTkLabel(layout_frame, text="Observações:").pack(pady=(10, 0))
        self.obs_input = ctk.CTkTextbox(layout_frame, width=400, height=100)
        self.obs_input.pack(pady=(0, 10))

        # Botão Salvar
        self.salvar_btn = ctk.CTkButton(layout_frame, text="Salvar Lead", command=self.salvar_lead)
        self.salvar_btn.pack(pady=20)

    def setup_listagem_tab(self):
        # Frame principal
        layout_frame = ctk.CTkFrame(self.listagem_tab)
        layout_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Tabela de leads usando Treeview
        columns = ("ID", "Nome", "Email", "Telefone", "Empresa", "Cargo", "Estágio", "Data Criação", "Última Interação")
        
        # Criar um frame para a scrollbar
        tree_frame = ctk.CTkFrame(layout_frame)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Adicionar scrollbar vertical
        tree_scroll = ctk.CTkScrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        # Criar Treeview
        self.tabela_leads = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set)
        
        # Configurar cabeçalhos
        for col in columns:
            self.tabela_leads.heading(col, text=col)
            self.tabela_leads.column(col, width=100, anchor="center")
        
        # Configurar scrollbar
        tree_scroll.configure(command=self.tabela_leads.yview)
        
        # Adicionar Treeview ao frame
        self.tabela_leads.pack(side="left", fill="both", expand=True)

        # Botões de ação
        botoes_frame = ctk.CTkFrame(layout_frame)
        botoes_frame.pack(pady=10)

        atualizar_btn = ctk.CTkButton(botoes_frame, text="Atualizar Lista", command=self.carregar_leads)
        atualizar_btn.pack(side="left", padx=10)

        excluir_btn = ctk.CTkButton(botoes_frame, text="Excluir Selecionado", command=self.excluir_lead)
        excluir_btn.pack(side="left", padx=10)

    def salvar_lead(self):
        try:
            # Coletar dados do formulário
            lead_data = {
                'nome': self.nome_input.get(),
                'email': self.email_input.get(),
                'telefone': self.telefone_input.get(),
                'empresa': self.empresa_input.get(),
                'cargo': self.cargo_input.get(),
                'estagio_atual': self.estagio_combo.get(),
                'observacoes': self.obs_input.get("1.0", "end-1c"),
                'ultima_interacao': datetime.now()
            }
            
            # Validar campos obrigatórios
            if not lead_data['nome']:
                tk.messagebox.showerror("Erro", "O campo Nome é obrigatório!")
                return
            
            if not lead_data['email']:
                tk.messagebox.showerror("Erro", "O campo Email é obrigatório!")
                return
            
            # Salvar no banco
            self.repositorio.adicionar_lead(lead_data)
            
            # Limpar formulário
            self.limpar_formulario()
            
            # Atualizar tabela
            self.carregar_leads()
            
            tk.messagebox.showinfo("Sucesso", "Lead cadastrado com sucesso!")
            
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao salvar lead: {str(e)}")

    def limpar_formulario(self):
        self.nome_input.delete(0, "end")
        self.email_input.delete(0, "end")
        self.telefone_input.delete(0, "end")
        self.empresa_input.delete(0, "end")
        self.cargo_input.delete(0, "end")
        self.estagio_combo.set("")
        self.obs_input.delete("1.0", "end")

    def carregar_leads(self):
        # Limpar tabela
        for i in self.tabela_leads.get_children():
            self.tabela_leads.delete(i)

        # Buscar leads do banco
        leads = self.repositorio.listar_leads()
        
        # Preencher dados
        for lead in leads:
            self.tabela_leads.insert("", "end", values=(
                lead.id, 
                lead.nome, 
                lead.email, 
                lead.telefone, 
                lead.empresa, 
                lead.cargo, 
                lead.estagio_atual, 
                lead.data_criacao, 
                lead.ultima_interacao
            ))

    def excluir_lead(self):
        # Obter lead selecionado
        selected_item = self.tabela_leads.selection()
        if not selected_item:
            tk.messagebox.showerror("Erro", "Selecione um lead para excluir")
            return

        # Obter ID do lead
        lead_id = self.tabela_leads.item(selected_item)['values'][0]
        
        try:
            # Excluir lead do banco
            self.repositorio.remover_lead(lead_id)
            
            # Atualizar tabela
            self.carregar_leads()
            
            tk.messagebox.showinfo("Sucesso", "Lead excluído com sucesso!")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao excluir lead: {str(e)}")

def main():
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    app = CRMApp()
    app.mainloop()

if __name__ == "__main__":
    main()
