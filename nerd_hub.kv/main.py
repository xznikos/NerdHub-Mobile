# main.py
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
import os

from database import (
    criar_tabelas, verificar_login, cadastrar_usuario, 
    carregar_usuario_teste, listar_usuarios,
    listar_produtos, listar_produtos_disney, listar_produtos_marvel,
    listar_produtos_starwars, listar_produtos_playstation, 
    listar_produtos_xbox, buscar_produto_por_id
)

# Importação das telas
from paginas.playstation import PlaystationScreen
from paginas.disney import DisneyScreen
from paginas.marvel import MarvelScreen
from paginas.starwars import StarWarsScreen
from paginas.xbox import XboxScreen
from paginas.home import HomeScreen
from paginas.login import LoginScreen
from paginas.carrinho import CarrinhoScreen
from paginas.cadastro import CadastroScreen
from paginas.produto_detalhes import DetalhesProdutoScreen  # ADICIONADO - Tela de detalhes do produto

# Tamanho da janela (para teste no desktop)
Window.size = (420, 900)


# -------------------------------
#  GERENCIADOR DE TELAS
# -------------------------------
class Gerenciador(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.historico = []

    def mudar_tela(self, nome_tela):
        """Função original - mantém compatibilidade"""
        if self.current:
            self.historico.append(self.current)
        self.current = nome_tela

    def mudar_tela_com_login(self, nome_tela):
        """Nova função específica para telas que precisam de login"""
        app = App.get_running_app()
        
        if not app.usuario_logado:
            print(f"❌ Acesso negado à tela '{nome_tela}' - usuário não logado")
            app.mostrar_popup("Faça o login para continuar!")
            # Redireciona para login
            if self.current:
                self.historico.append(self.current)
            self.current = "login"
            return False
        
        # Se logado, muda para a tela normalmente
        if self.current:
            self.historico.append(self.current)
        self.current = nome_tela
        return True

    def voltar(self):
        if self.historico:
            self.current = self.historico.pop()
        else:
            self.current = "home"


# -------------------------------
#  APP PRINCIPAL
# -------------------------------
class NerdHubApp(App):
    usuario_logado = None  # Guarda usuário atual

    def build(self):
        # Inicializar banco de dados
        print("🚀 Iniciando aplicação NerdHub...")
        
        # ✅ APENAS cria as tabelas se não existirem (dados persistentes)
        criar_tabelas()
        carregar_usuario_teste()
        
        # Debug: listar usuários
        listar_usuarios()

        # Carregar telas KV
        Builder.load_file("telas/home.kv")
        Builder.load_file("telas/login.kv")
        Builder.load_file("telas/playstation.kv")
        Builder.load_file("telas/xbox.kv")
        Builder.load_file("telas/marvel.kv")
        Builder.load_file("telas/starwars.kv")
        Builder.load_file("telas/disney.kv")
        Builder.load_file("telas/carrinho.kv")
        Builder.load_file("telas/detalhes_produto.kv")  # ADICIONADO - Tela de detalhes
        Builder.load_file("telas/cadastro.kv")

        # Gerenciador de telas
        sm = Gerenciador()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(PlaystationScreen(name="playstation"))
        sm.add_widget(XboxScreen(name="xbox"))
        sm.add_widget(MarvelScreen(name="marvel"))
        sm.add_widget(StarWarsScreen(name="starwars"))
        sm.add_widget(DisneyScreen(name="disney"))
        sm.add_widget(CarrinhoScreen(name="carrinho"))
        sm.add_widget(DetalhesProdutoScreen(name="detalhes_produto"))  # ADICIONADO - Tela de detalhes
        sm.add_widget(CadastroScreen(name="cadastro"))

        return sm

    # -------------------------------
    #  POPUP
    # -------------------------------
    def mostrar_popup(self, mensagem):
        popup = Popup(
            title="Mensagem",
            content=Label(text=mensagem),
            size_hint=(None, None),
            size=(300, 200),
        )
        popup.open()

    # -------------------------------
    #  LOGIN E CADASTRO - CORRIGIDAS
    # -------------------------------
    def fazer_login(self, email, senha):
        """Usa a função do database.py para verificar login - CORRIGIDA"""
        print(f"🔐 Tentando login: {email}")
        print(f"🔐 Senha fornecida: {senha}")
        
        if not email or not senha:
            self.mostrar_popup("Preencha todos os campos!")
            return False
            
        usuario = verificar_login(email, senha)
        if usuario:
            self.usuario_logado = {
                'id': usuario[0],
                'nome': usuario[1], 
                'email': usuario[2]
            }
            print(f"✅ Login bem-sucedido! Usuário: {self.usuario_logado}")
            self.mostrar_popup(f"Bem-vindo, {usuario[1]}!")
            self.root.mudar_tela("home")
            return True
        else:
            print("❌ Falha no login - usuário não encontrado ou senha incorreta")
            self.mostrar_popup("E-mail ou senha incorretos.")
            return False

    def cadastrar_usuario(self, nome, email, senha):
        """Usa a função do database.py para cadastrar - CORRIGIDA"""
        print(f"📝 Tentando cadastrar: {nome}, {email}")
        print(f"📝 Senha fornecida: {senha}")
        
        if not nome or not email or not senha:
            self.mostrar_popup("Preencha todos os campos!")
            return False
            
        # Validação básica de email
        if "@" not in email or "." not in email:
            self.mostrar_popup("Por favor, insira um email válido!")
            return False
            
        sucesso = cadastrar_usuario(nome, email, senha)
        if sucesso:
            self.mostrar_popup("Cadastro realizado com sucesso!")
            print("✅ Usuário cadastrado com sucesso!")
            return True
        else:
            self.mostrar_popup("E-mail já cadastrado!")
            return False

    # -------------------------------
    #  FUNÇÕES DE NAVEGAÇÃO COM LOGIN
    # -------------------------------
    def ir_para_carrinho(self):
        """Função específica para ir para carrinho com verificação"""
        if not self.usuario_logado:
            self.mostrar_popup("Faça o login para acessar seu carrinho!")
            self.root.mudar_tela("login")
        else:
            self.root.mudar_tela("carrinho")

    def ir_para_tela_com_login(self, nome_tela):
        """Função genérica para ir para qualquer tela com verificação de login"""
        if not self.usuario_logado:
            self.mostrar_popup("Faça o login para continuar!")
            self.root.mudar_tela("login")
            return False
        else:
            self.root.mudar_tela(nome_tela)
            return True

    # -------------------------------
    #  CARRINHO - ATUALIZADAS
    # -------------------------------
    def adicionar_ao_carrinho(self, produto_info):
        """Função para adicionar produtos ao carrinho - ATUALIZADA"""
        print(f"🛒 Adicionar ao carrinho: {produto_info['title']}")
        print(f"🔐 Status: {'Logado' if self.usuario_logado else 'Não logado'}")
        
        # VERIFICAÇÃO IMEDIATA
        if not self.usuario_logado:
            print("❌ Usuário não logado - redirecionando para login")
            self.mostrar_popup("Você precisa fazer login para adicionar produtos.")
            Clock.schedule_once(lambda dt: self.root.mudar_tela("login"), 0.5)
            return
            
        # SE ESTIVER LOGADO - Adiciona ao carrinho NO BANCO DE DADOS
        print(f"✅ Usuário {self.usuario_logado['nome']} adicionando ao carrinho")
        try:
            # Adiciona ao banco de dados
            from database import adicionar_ao_carrinho_db
            sucesso = adicionar_ao_carrinho_db(
                self.usuario_logado['id'], 
                produto_info['id']
            )
            
            if sucesso:
                self.mostrar_popup("Produto adicionado ao carrinho!")
                # Atualiza a tela do carrinho se estiver aberta
                self.atualizar_tela_carrinho()
            else:
                self.mostrar_popup("Erro ao adicionar produto ao carrinho.")
                
        except Exception as e:
            print(f"💥 Erro ao adicionar ao carrinho: {e}")
            self.mostrar_popup("Erro ao adicionar produto.")

    def atualizar_tela_carrinho(self):
        """Atualiza a tela do carrinho se estiver visível"""
        try:
            carrinho_screen = self.root.get_screen("carrinho")
            if carrinho_screen:
                carrinho_screen.carregar_carrinho_usuario()
        except:
            pass  # Tela do carrinho não está carregada

    def obter_carrinho_usuario(self):
        """Retorna os itens do carrinho do usuário logado"""
        if not self.usuario_logado:
            return []
        
        from database import obter_carrinho_usuario
        return obter_carrinho_usuario(self.usuario_logado['id'])

    def remover_do_carrinho(self, produto_id):
        """Remove produto do carrinho do usuário"""
        if not self.usuario_logado:
            return False
        
        from database import remover_do_carrinho_db
        return remover_do_carrinho_db(self.usuario_logado['id'], produto_id)

    def limpar_carrinho(self):
        """Limpa todo o carrinho do usuário"""
        if not self.usuario_logado:
            return False
        
        from database import limpar_carrinho_usuario
        return limpar_carrinho_usuario(self.usuario_logado['id'])

    # -------------------------------
    #  DETALHES DO PRODUTO (COMENTADO POR ENQUANTO)
    # -------------------------------
    # def abrir_detalhes_produto(self, produto_id):
    #     tela_detalhes = self.root.get_screen("detalhes_produto")
    #     tela_detalhes.produto_id = produto_id
    #     self.root.mudar_tela("detalhes_produto")


if __name__ == "__main__":
    NerdHubApp().run()