# paginas/login.py
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.app import App

class LoginScreen(Screen):
    mensagem = StringProperty("")

    def realizar_login(self):
        email = self.ids.email_input.text.strip()
        senha = self.ids.senha_input.text.strip()

        if not email or not senha:
            self.mensagem = "Preencha todos os campos."
            return

        print(f"🖥️ Tela login - Tentando login: {email}")
        
        # Usa a função do App principal para manter consistência
        app = App.get_running_app()
        sucesso = app.fazer_login(email, senha)
        
        if sucesso:
            self.mensagem = "✅ Login realizado com sucesso!"
            self.limpar_campos()
        else:
            self.mensagem = "❌ E-mail ou senha incorretos."

    def limpar_campos(self):
        self.ids.email_input.text = ""
        self.ids.senha_input.text = ""

    def ir_para_cadastro(self):
        self.manager.current = "cadastro"

    def voltar(self):
        if hasattr(self.manager, "voltar"):
            self.manager.voltar()
        else:
            self.manager.current = "home"