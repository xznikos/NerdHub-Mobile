from kivy.uix.screenmanager import Screen
from kivy.app import App
from database import listar_produtos

class HomeScreen(Screen):
    def on_pre_enter(self):
        """Carrega produtos quando a tela está prestes a ser mostrada"""
        self.carregar_produtos()

    def carregar_produtos(self):
        """Carrega produtos do BANCO DE DADOS"""
        try:
            produtos = listar_produtos()
            
            grid = self.ids.products_grid
            grid.clear_widgets()

            for produto in produtos:
                from kivy.factory import Factory
                card = Factory.ProductCard()
                card.produto_id = produto[0]
                card.title = produto[1]
                card.price = produto[2]
                card.image = produto[3]
                # NÃO é mais necessário fazer bind aqui - a navegação está no arquivo .kv
                grid.add_widget(card)
                
            print(f"✅ {len(produtos)} produtos carregados do banco")
            
        except Exception as e:
            print(f"❌ Erro ao carregar produtos: {e}")

    def ir_para_tela(self, tela):
        """Navega para outras telas usando o sistema de histórico"""
        self.manager.mudar_tela(tela)

    def ir_para_carrinho(self):
        """Nova função: Verifica se usuário está logado antes de ir para carrinho"""
        app = App.get_running_app()
        
        if app.usuario_logado:
            # Usuário está logado - vai para carrinho normalmente
            print(f"✅ Usuário {app.usuario_logado['nome']} acessando carrinho")
            self.manager.mudar_tela("carrinho")
        else:
            # Usuário não está logado - mostra mensagem e vai para login
            print("❌ Usuário não logado - redirecionando para login")
            app.mostrar_popup("Faça o login para acessar seu carrinho!")
            # Redireciona para tela de login após um breve delay
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.manager.mudar_tela("login"), 0.5)
    
    def ir_para_detalhes(self, produto_id):
        """
        NOVA FUNÇÃO: Navega para a tela de detalhes do produto.
        
        Esta função é chamada quando o usuário clica em um card de produto.
        Ela configura o ID do produto na tela de detalhes e navega para ela.
        
        Args:
            produto_id (int): ID do produto a ser exibido
        """
        print(f"🔍 Abrindo detalhes do produto ID: {produto_id}")
        
        try:
            # Obtém a tela de detalhes do produto
            tela_detalhes = self.manager.get_screen("detalhes_produto")
            
            # Define o ID do produto que será carregado
            tela_detalhes.produto_id = produto_id
            
            # Navega para a tela de detalhes usando o sistema de histórico
            self.manager.mudar_tela("detalhes_produto")
            
        except Exception as e:
            print(f"❌ Erro ao abrir detalhes do produto: {e}")
            # Exibe popup de erro ao usuário
            app = App.get_running_app()
            app.mostrar_popup("Erro ao abrir detalhes do produto. Tente novamente.")