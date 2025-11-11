# paginas/cadastro.py
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.app import App

class CadastroScreen(Screen):
    mensagem = StringProperty("")

    def realizar_cadastro(self):
        nome = self.ids.nome_input.text.strip()
        email = self.ids.email_input.text.strip()
        senha = self.ids.senha_input.text.strip()

        if not nome or not email or not senha:
            self.mensagem = "Preencha todos os campos."
            return

        print(f"🖥️ Tela cadastro - Tentando cadastrar: {nome}, {email}")
        
        # Usa a função do App principal
        app = App.get_running_app()
        sucesso = app.cadastrar_usuario(nome, email, senha)
        
        if sucesso:
            self.mensagem = "✅ Cadastro realizado com sucesso!"
            self.limpar_campos()
            Clock.schedule_once(self.ir_para_login, 2.0)
        else:
            self.mensagem = "❌ E-mail já cadastrado. Tente outro."

    def limpar_campos(self):
        self.ids.nome_input.text = ""
        self.ids.email_input.text = ""
        self.ids.senha_input.text = ""

    def ir_para_login(self, *args):
        self.manager.current = "login"

    def voltar(self):
        if hasattr(self.manager, "voltar"):
            self.manager.voltar()
        else:
            self.manager.current = "home"