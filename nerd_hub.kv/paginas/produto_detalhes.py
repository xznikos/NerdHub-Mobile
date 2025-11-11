# paginas/produto_detalhes.py
"""
Tela de Detalhes do Produto
============================
Esta tela exibe informações completas sobre um produto específico,
incluindo imagem, nome, descrição, preço e botão para adicionar ao carrinho.

Funcionalidades:
- Carrega dados do produto do banco de dados usando o ID
- Exibe imagem em alta resolução
- Mostra descrição detalhada do produto
- Verifica login antes de adicionar ao carrinho
- Redireciona para login se necessário
- Integra com o sistema de carrinho existente
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from kivy.clock import Clock
from database import buscar_produto_por_id


class DetalhesProdutoScreen(Screen):
    """
    Tela de detalhes do produto
    
    Properties:
        produto_id (int): ID do produto a ser exibido
        titulo (str): Nome do produto
        preco (str): Preço formatado do produto
        imagem (str): Caminho da imagem do produto
        descricao (str): Descrição detalhada do produto
        categoria (str): Categoria do produto (disney, marvel, etc.)
    """
    
    # Propriedades que serão vinculadas ao arquivo .kv
    produto_id = NumericProperty(0)
    titulo = StringProperty("Carregando...")
    preco = StringProperty("R$ 0,00")
    imagem = StringProperty("imagens/imagem_produtos_home/forza.jpg")  # Caminho corrigido
    descricao = StringProperty("Carregando descrição do produto...")
    categoria = StringProperty("geral")
    
    def on_pre_enter(self, *args):
        """
        Executado antes da tela ser exibida.
        Carrega os dados do produto do banco de dados.
        """
        print(f"📱 Abrindo detalhes do produto ID: {self.produto_id}")
        self.carregar_produto()
    
    def carregar_produto(self):
        """
        Busca os dados do produto no banco de dados e atualiza a interface.
        
        Utiliza a função buscar_produto_por_id() do database.py para
        recuperar todas as informações do produto baseado no ID.
        """
        try:
            # Busca produto no banco de dados
            produto = buscar_produto_por_id(self.produto_id)
            
            if produto:
                # Produto encontrado - atualiza as propriedades
                self.titulo = produto[1]           # title
                self.preco = produto[2]            # price
                self.imagem = produto[3]           # image
                self.categoria = produto[4] if len(produto) > 4 else "geral"  # categoria
                
                # Descrição (com fallback se não existir)
                if len(produto) > 5 and produto[5]:
                    self.descricao = produto[5]
                else:
                    # Descrição padrão baseada na categoria
                    self.descricao = self.gerar_descricao_padrao()
                
                print(f"✅ Produto carregado: {self.titulo}")
                
            else:
                # Produto não encontrado - exibe mensagem de erro
                self.titulo = "Produto não encontrado"
                self.preco = "R$ 0,00"
                self.descricao = "Desculpe, não conseguimos encontrar este produto. Por favor, tente novamente."
                print(f"❌ Produto {self.produto_id} não encontrado no banco")
                
        except Exception as e:
            # Erro ao carregar produto
            print(f"💥 Erro ao carregar produto: {e}")
            self.titulo = "Erro ao carregar"
            self.descricao = f"Ocorreu um erro ao carregar o produto: {str(e)}"
    
    def gerar_descricao_padrao(self):
        """
        Gera uma descrição padrão baseada na categoria do produto.
        
        Returns:
            str: Descrição personalizada de acordo com a categoria
        """
        descricoes = {
            "disney": f"{self.titulo} - Um produto mágico da Disney para fãs de todas as idades! "
                     "Itens oficiais com a qualidade e encanto que só a Disney pode proporcionar. "
                     "Perfeito para colecionadores e entusiastas do universo Disney.",
            
            "marvel": f"{self.titulo} - Para verdadeiros heróis! Este item oficial Marvel "
                     "traz toda a ação e aventura do universo cinematográfico e dos quadrinhos. "
                     "Ideal para fãs dos Vingadores e do universo Marvel.",
            
            "starwars": f"{self.titulo} - Que a Força esteja com você! Produto oficial Star Wars "
                       "para colecionadores e fãs da saga galáctica mais épica de todos os tempos. "
                       "De uma galáxia muito, muito distante direto para você!",
            
            "playstation": f"{self.titulo} - Maximize sua experiência de jogo! Produto oficial PlayStation "
                          "com tecnologia de ponta e qualidade superior. Para gamers que buscam o melhor "
                          "em entretenimento e performance.",
            
            "xbox": f"{self.titulo} - Power Your Dreams! Produto oficial Xbox para elevar seu "
                   "gaming ao próximo nível. Tecnologia avançada e design inovador para uma "
                   "experiência de jogo incomparável.",
            
            "lego": f"{self.titulo} - Construa, brinque e exiba! Set LEGO oficial com peças de "
                   "alta qualidade e design detalhado. Perfeito para builders de todas as idades "
                   "que amam criar e colecionar.",
        }
        
        # Retorna descrição específica ou padrão
        return descricoes.get(
            self.categoria,
            f"{self.titulo} - Produto de alta qualidade para verdadeiros nerds! "
            "Este item é perfeito para colecionadores e fãs que buscam itens exclusivos e autênticos. "
            "Adicione ao seu carrinho e garanta já o seu!"
        )
    
    def adicionar_ao_carrinho(self):
        """
        Adiciona o produto ao carrinho do usuário.
        
        Fluxo:
        1. Verifica se o usuário está logado
        2. Se não estiver, exibe popup e redireciona para login
        3. Se estiver logado, adiciona o produto ao carrinho via App
        4. Exibe mensagem de confirmação
        
        Esta função integra com o sistema de carrinho existente no main.py
        """
        app = App.get_running_app()
        
        # Verificação de login
        if not app.usuario_logado:
            print("❌ Usuário não logado - tentativa de adicionar ao carrinho")
            app.mostrar_popup("Você precisa fazer login para adicionar produtos ao carrinho!")
            
            # Redireciona para tela de login após breve delay
            Clock.schedule_once(lambda dt: self.manager.mudar_tela("login"), 0.8)
            return
        
        # Usuário logado - monta informações do produto
        produto_info = {
            'id': self.produto_id,
            'title': self.titulo,
            'price': self.preco,
            'image': self.imagem
        }
        
        print(f"🛒 Adicionando ao carrinho: {self.titulo} (ID: {self.produto_id})")
        print(f"👤 Usuário: {app.usuario_logado['nome']}")
        
        # Chama a função de adicionar ao carrinho do App principal
        # Esta função já gerencia banco de dados e feedback ao usuário
        app.adicionar_ao_carrinho(produto_info)
    
    def voltar(self):
        """
        Volta para a tela anterior no histórico.
        
        Utiliza o sistema de histórico do Gerenciador (ScreenManager customizado)
        para retornar à tela de onde o usuário veio (geralmente Home ou categoria).
        """
        print("⬅️ Voltando da tela de detalhes")
        
        # Verifica se o gerenciador tem função de voltar
        if hasattr(self.manager, "voltar"):
            self.manager.voltar()
        else:
            # Fallback - volta para home
            self.manager.current = "home"
