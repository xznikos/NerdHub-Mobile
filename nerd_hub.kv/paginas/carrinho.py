# paginas/carrinho.py - ATUALIZADO
from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App

class CarrinhoScreen(Screen):
    itens = ListProperty([])

    def on_pre_enter(self):
        """Carrega o carrinho do usuário ao entrar na tela"""
        app = App.get_running_app()
        
        if not app.usuario_logado:
            print("❌ Acesso não autorizado ao carrinho - redirecionando para login")
            app.mostrar_popup("Faça o login para acessar seu carrinho!")
            self.manager.current = "login"
            return
        
        # Carrega o carrinho do usuário específico
        self.carregar_carrinho_usuario()

    def carregar_carrinho_usuario(self):
        """Carrega o carrinho do usuário logado do banco de dados"""
        app = App.get_running_app()
        
        if not app.usuario_logado:
            self.itens = []
            return
        
        # Obtém itens do banco de dados
        itens_db = app.obter_carrinho_usuario()
        
        # Converte para o formato esperado pela interface
        self.itens = []
        for item in itens_db:
            self.itens.append({
                'id': item[0],
                'title': item[1],
                'price': item[2],
                'image': item[3],
                'quantidade': item[4]
            })
        
        self.atualizar_lista()
        self.atualizar_total()

    def on_itens(self, instance, value):
        self.atualizar_lista()
        self.atualizar_total()

    def atualizar_lista(self):
        layout = self.ids.carrinho_lista
        layout.clear_widgets()

        if not self.itens:
            empty_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(200),
                padding=dp(20),
                spacing=dp(10)
            )
            empty_box.add_widget(Label(
                text="Seu carrinho está vazio",
                font_size='18sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center',
                valign='middle'
            ))
            empty_box.add_widget(Label(
                text="Adicione produtos incríveis!",
                font_size='14sp',
                color=(0.7, 0.7, 0.7, 1),
                halign='center',
                valign='middle'
            ))
            layout.add_widget(empty_box)
            if hasattr(self, 'ids') and 'total_label' in self.ids:
                self.ids.total_label.text = "Total: R$ 0,00"
            return

        from kivy.factory import Factory
        for produto in self.itens:
            card = Factory.CarrinhoCard()
            card.produto = type('Produto', (), {
                'id': produto.get("id", 0),
                'title': produto.get("title", ""),
                'price': produto.get("price", ""),
                'image': produto.get("image", "imagens/imagem_produtos_home/forza.jpg"),
                'quantidade': produto.get("quantidade", 1)
            })()
            card.remover_callback = self.remover_item
            layout.add_widget(card)

        self.atualizar_total()

    def remover_item(self, produto):
        """Remove item do carrinho no banco de dados"""
        app = App.get_running_app()
        
        if app.remover_do_carrinho(produto.id):
            # Remove da lista local
            for item in self.itens[:]:
                if item.get('id') == produto.id:
                    self.itens.remove(item)
                    break
            
            self.atualizar_lista()
            app.mostrar_popup("Produto removido do carrinho!")
        else:
            app.mostrar_popup("Erro ao remover produto!")

    def atualizar_total(self):
        total = 0.0

        for produto in self.itens:
            preco_str = produto.get("price", "R$ 0,00")
            quantidade = produto.get("quantidade", 1)
            try:
                preco_limpo = preco_str.replace("R$", "").strip()
                preco_limpo = preco_limpo.replace(".", "").replace(",", ".")
                valor = float(preco_limpo)
                total += valor * quantidade
            except ValueError:
                print(f"Erro ao converter preço: {preco_str}")

        if hasattr(self, 'ids') and 'total_label' in self.ids:
            self.ids.total_label.text = f"Total: R$ {total:,.2f}".replace(".", "#").replace(",", ".").replace("#", ",")

    def limpar_carrinho(self):
        """Limpa todo o carrinho"""
        app = App.get_running_app()
        
        if app.limpar_carrinho():
            self.itens = []
            self.atualizar_lista()
            app.mostrar_popup("Carrinho limpo!")
        else:
            app.mostrar_popup("Erro ao limpar carrinho!")

    def voltar(self):
        if hasattr(self.manager, "voltar"):
            self.manager.voltar()