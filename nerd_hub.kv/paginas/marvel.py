# paginas/disney.py
from kivy.uix.screenmanager import Screen
from database import listar_produtos_marvel

class MarvelScreen(Screen):
    def on_pre_enter(self):
        """Carrega produtos Marvel quando a tela está prestes a ser mostrada"""
        self.carregar_produtos()

    def carregar_produtos(self):
        """Carrega produtos Marvel do BANCO DE DADOS"""
        try:
            produtos = listar_produtos_marvel()
            
            grid = self.ids.produtos_grid
            grid.clear_widgets()

            for produto in produtos:
                from kivy.factory import Factory
                card = Factory.ProductCard()
                card.produto_id = produto[0]
                card.title = produto[1]
                card.price = produto[2]
                card.image = produto[3]
                grid.add_widget(card)
                
            print(f"✅ {len(produtos)} produtos Marvel carregados do banco")
            
        except Exception as e:
            print(f"❌ Erro ao carregar produtos Marvel: {e}")

    def voltar(self):
        """Volta para a tela anterior"""
        self.manager.voltar()