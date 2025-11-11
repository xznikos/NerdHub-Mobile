import sqlite3
import hashlib
import os

# CORREÇÃO: Caminho absoluto para o banco na mesma pasta
DB_PATH = os.path.join(os.path.dirname(__file__), "usuarios.db")

def conectar():
    """Conecta ao banco de usuários"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    """Cria todas as tabelas necessárias - ATUALIZADA COM MIGRAÇÃO"""
    conn = conectar()
    cur = conn.cursor()
    
    # Tabela de usuários
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)
    
    # Tabela de produtos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price TEXT NOT NULL,
        image TEXT,
        categoria TEXT,
        descricao TEXT DEFAULT 'Produto de alta qualidade para verdadeiros nerds! Este item é perfeito para colecionadores e fãs que buscam itens exclusivos e autênticos.'
    )
    """)

    conn.commit()
    
    # MIGRAÇÃO: Adiciona coluna descricao se não existir (para bancos antigos)
    try:
        cur.execute("SELECT descricao FROM produtos LIMIT 1")
    except sqlite3.OperationalError:
        print("🔄 Migrando banco: adicionando coluna 'descricao'...")
        cur.execute("""ALTER TABLE produtos ADD COLUMN descricao TEXT DEFAULT 
                    'Produto de alta qualidade para verdadeiros nerds! Este item é perfeito para colecionadores e fãs que buscam itens exclusivos e autênticos.'""")
        conn.commit()
        print("✅ Coluna 'descricao' adicionada com sucesso!")
    
    conn.close()
    print(f"✅ Todas as tabelas criadas/verificadas em: {DB_PATH}")
    
    # Cria tabela carrinho separadamente
    criar_tabela_carrinho()
    
    # Corrige caminhos de imagens (para migração de bancos antigos)
    corrigir_caminhos_imagens()
    
    # Carrega produtos iniciais se a tabela estiver vazia
    carregar_produtos_iniciais()

def criar_tabela_carrinho():
    """Cria tabela do carrinho se não existir"""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS carrinho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER DEFAULT 1,
        adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        UNIQUE(usuario_id, produto_id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Tabela carrinho criada/verificada")

def carregar_produtos_iniciais():
    """Carrega produtos iniciais na tabela se estiver vazia"""
    conn = conectar()
    cur = conn.cursor()
    
    # Verifica se já existem produtos
    cur.execute("SELECT COUNT(*) FROM produtos")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("🔄 Carregando produtos iniciais no banco...")
        
        produtos_iniciais = [
            # Produtos Gerais - CAMINHOS CORRIGIDOS PARA ANDROID
            ("FORZA - Xbox Series X", "R$ 179,00", "imagens/imagem_produtos_home/forza.jpg", "xbox"),
            ("LEGO Minecraft - Aventura", "R$ 1.349,90", "imagens/imagem_produtos_home/lego_minecraft.jpg", "lego"),
            ("PlayStation 5 Pro", "R$ 6.509,00", "imagens/imagem_produtos_home/ps5.jpg", "playstation"),
            ("PlayStation Portal", "R$ 1.349,90", "imagens/imagem_produtos_home/portal.jpg", "playstation"),
            ("Funko Pop! Star Wars", "R$ 389,90", "imagens/imagem_produtos_home/funko.jpg", "starwars"),
            ("Camiseta Marvel Avengers", "R$ 82,35", "imagens/imagem_produtos_home/camiseta_marvel.jpg", "marvel"),
            ("Pelúcia Chewbacca", "R$ 141,50", "imagens/imagem_produtos_home/chewbacca.jpg", "starwars"),
            ("LEGO Star Wars - 75257", "R$ 201,00", "imagens/imagem_produtos_home/lego_starwars.jpg", "starwars"),
            
            # Produtos Disney
            ("Pelúcia Mickey Mouse - Disney", "R$ 89,90", "imagens/imagem_produtos_home/mickey.jpg", "disney"),
            ("LEGO Disney Castle - 43222", "R$ 1.299,90", "imagens/imagem_produtos_home/lego_castle.jpg", "disney"),
            ("Funko Pop! Mickey Mouse - Disney", "R$ 79,90", "imagens/imagem_produtos_home/funko_mickey.jpg", "disney"),
            ("Camiseta Mickey Classic - Disney", "R$ 59,90", "imagens/imagem_produtos_home/camiseta_mickey.jpg", "disney"),
            
            # Produtos Marvel
            ("Action Figure Homem de Ferro", "R$ 129,90", "imagens/imagem_produtos_home/camiseta_marvel.jpg", "marvel"),
            ("Camiseta Avengers", "R$ 79,90", "imagens/imagem_produtos_home/camiseta_marvel.jpg", "marvel"),
            
            # Produtos Star Wars
            ("Action Figure Darth Vader", "R$ 149,90", "imagens/imagem_produtos_home/darth_vader.jpg", "starwars"),
            ("LEGO Millennium Falcon", "R$ 899,90", "imagens/imagem_produtos_home/millennium_falcon.jpg", "starwars"),
            
            # Produtos PlayStation
            ("Controle DualSense PS5", "R$ 449,00", "imagens/imagem_produtos_home/ps5.jpg", "playstation"),
            ("Headset PlayStation Pulse 3D", "R$ 599,00", "imagens/imagem_produtos_home/portal.jpg", "playstation"),
            
            # Produtos Xbox
            ("Controle Xbox Series X", "R$ 499,00", "imagens/imagem_produtos_home/forza.jpg", "xbox"),
            ("Headset Xbox Wireless", "R$ 699,00", "imagens/imagem_produtos_home/forza.jpg", "xbox"),
        ]
        
        for produto in produtos_iniciais:
            cur.execute("INSERT INTO produtos (title, price, image, categoria) VALUES (?, ?, ?, ?)", produto)
            print(f"   ✅ {produto[0]}")
        
        conn.commit()
        print(f"📦 {len(produtos_iniciais)} produtos carregados no banco")
    else:
        print(f"✅ {count} produtos já existem no banco")
    
    conn.close()

# =============================================================================
# FUNÇÕES DE USUÁRIOS - CORRIGIDAS
# =============================================================================

def hash_senha(senha_plain):
    """Gera o hash SHA-256 da senha em texto puro."""
    return hashlib.sha256(senha_plain.encode("utf-8")).hexdigest()

def cadastrar_usuario(nome, email, senha_plain):
    """Cadastra um novo usuário - CORRIGIDA"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        # CORREÇÃO: Usando hash desde o início
        senha_hash = hash_senha(senha_plain)
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha_hash))
            
        conn.commit()
        print(f"✅ Usuário cadastrado: {nome} - {email}")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ E-mail já cadastrado: {email}")
        return False
    except Exception as e:
        print(f"💥 Erro inesperado no cadastro: {e}")
        return False
    finally:
        conn.close()

def verificar_login(email, senha_plain):
    """Verifica se o login é válido - CORRIGIDA"""
    conn = conectar()
    cur = conn.cursor()
    
    senha_hash = hash_senha(senha_plain)
    print(f"🔐 Verificando login: {email}")
    print(f"🔐 Hash da senha fornecida: {senha_hash}")
    
    # CORREÇÃO: Busca direta com hash
    cur.execute("""
        SELECT id, nome, email, senha
        FROM usuarios
        WHERE email = ? AND senha = ?
    """, (email, senha_hash))
    
    usuario = cur.fetchone()
    conn.close()
    
    if usuario:
        print(f"✅ Login bem-sucedido! Usuário: {usuario[1]}")
        return (usuario[0], usuario[1], usuario[2])
    else:
        print("❌ Usuário não encontrado ou senha incorreta!")
        return None

def carregar_usuario_teste():
    """Carrega um usuário de teste - CORRIGIDA"""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM usuarios")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("👤 Criando usuário de teste...")
        usuario_teste = ("Usuário Teste", "teste@email.com", "123456")
        try:
            senha_hash = hash_senha(usuario_teste[2])
            cur.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", 
                       (usuario_teste[0], usuario_teste[1], senha_hash))
            conn.commit()
            print("✅ Usuário de teste criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao criar usuário de teste: {e}")
    
    conn.close()

def listar_usuarios():
    """Lista todos os usuários"""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios")
    usuarios = cur.fetchall()
    conn.close()
    
    print("=== 👥 USUÁRIOS NO BANCO ===")
    for usuario in usuarios:
        print(f"   👤 {usuario[1]} - {usuario[2]}")
    print("=============================")
    
    return usuarios

# =============================================================================
# FUNÇÕES PARA CARRINHO (NOVAS)
# =============================================================================

def adicionar_ao_carrinho_db(usuario_id, produto_id, quantidade=1):
    """Adiciona produto ao carrinho do usuário"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        # Usa INSERT OR REPLACE para atualizar quantidade se já existir
        cur.execute("""
            INSERT OR REPLACE INTO carrinho (usuario_id, produto_id, quantidade)
            VALUES (?, ?, COALESCE((SELECT quantidade FROM carrinho WHERE usuario_id = ? AND produto_id = ?) + 1, 1))
        """, (usuario_id, produto_id, usuario_id, produto_id))
        
        conn.commit()
        print(f"✅ Produto {produto_id} adicionado ao carrinho do usuário {usuario_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar ao carrinho: {e}")
        return False
    finally:
        conn.close()

def remover_do_carrinho_db(usuario_id, produto_id):
    """Remove produto do carrinho do usuário"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM carrinho WHERE usuario_id = ? AND produto_id = ?", 
                   (usuario_id, produto_id))
        conn.commit()
        print(f"✅ Produto {produto_id} removido do carrinho do usuário {usuario_id}")
        return True
    except Exception as e:
        print(f"❌ Erro ao remover do carrinho: {e}")
        return False
    finally:
        conn.close()

def obter_carrinho_usuario(usuario_id):
    """Retorna todos os itens do carrinho do usuário com informações completas"""
    conn = conectar()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.id, p.title, p.price, p.image, c.quantidade
        FROM carrinho c
        JOIN produtos p ON c.produto_id = p.id
        WHERE c.usuario_id = ?
        ORDER BY c.adicionado_em DESC
    """, (usuario_id,))
    
    itens = cur.fetchall()
    conn.close()
    
    print(f"🛒 Carrinho do usuário {usuario_id}: {len(itens)} itens")
    return itens

def limpar_carrinho_usuario(usuario_id):
    """Limpa todo o carrinho do usuário"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM carrinho WHERE usuario_id = ?", (usuario_id,))
        conn.commit()
        print(f"✅ Carrinho do usuário {usuario_id} limpo")
        return True
    except Exception as e:
        print(f"❌ Erro ao limpar carrinho: {e}")
        return False
    finally:
        conn.close()

# =============================================================================
# FUNÇÕES PARA PRODUTOS (AGORA COM BANCO DE DADOS)
# =============================================================================

def listar_produtos():
    """Retorna todos os produtos do banco"""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, image FROM produtos")
    produtos = cur.fetchall()
    conn.close()
    
    print(f"📦 {len(produtos)} produtos carregados do banco")
    return produtos

def listar_produtos_por_categoria(categoria):
    """Retorna produtos filtrados por categoria"""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, image FROM produtos WHERE categoria = ?", (categoria,))
    produtos = cur.fetchall()
    conn.close()
    
    print(f"📦 {len(produtos)} produtos da categoria '{categoria}'")
    return produtos

# Funções específicas por categoria (para compatibilidade com telas existentes)
def listar_produtos_disney():
    """Retorna produtos Disney do banco"""
    return listar_produtos_por_categoria("disney")

def listar_produtos_marvel():
    """Retorna produtos Marvel do banco"""
    return listar_produtos_por_categoria("marvel")

def listar_produtos_starwars():
    """Retorna produtos Star Wars do banco"""
    return listar_produtos_por_categoria("starwars")

def listar_produtos_playstation():
    """Retorna produtos PlayStation do banco"""
    return listar_produtos_por_categoria("playstation")

def listar_produtos_xbox():
    """Retorna produtos Xbox do banco"""
    return listar_produtos_por_categoria("xbox")

def buscar_produto_por_id(produto_id):
    """Busca produto pelo ID no banco - ATUALIZADA COM DESCRIÇÃO"""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price, image, categoria, descricao FROM produtos WHERE id = ?", (produto_id,))
    produto = cur.fetchone()
    conn.close()
    
    if produto:
        print(f"📦 Produto encontrado: {produto[1]}")
    else:
        print(f"❌ Produto {produto_id} não encontrado")
    
    return produto

def adicionar_produto(title, price, image, categoria="geral"):
    """Adiciona um novo produto ao banco"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO produtos (title, price, image, categoria) VALUES (?, ?, ?, ?)", 
                   (title, price, image, categoria))
        conn.commit()
        print(f"✅ Produto adicionado: {title}")
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar produto: {e}")
        return False
    finally:
        conn.close()

def corrigir_caminhos_imagens():
    """Corrige caminhos de imagens existentes no banco de dados"""
    conn = conectar()
    cur = conn.cursor()
    
    try:
        # Atualiza todos os caminhos que começam com 'nerd_hub.kv/imagens'
        cur.execute("""
            UPDATE produtos 
            SET image = REPLACE(image, 'nerd_hub.kv/imagens/', 'imagens/')
            WHERE image LIKE 'nerd_hub.kv/imagens/%'
        """)
        
        rows_affected = cur.rowcount
        conn.commit()
        
        if rows_affected > 0:
            print(f"✅ {rows_affected} caminhos de imagem corrigidos no banco")
        else:
            print("✅ Caminhos de imagem já estão corretos")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao corrigir caminhos: {e}")
        return False
    finally:
        conn.close()

# =============================================================================
# INICIALIZAÇÃO DO BANCO
# =============================================================================
if __name__ == "__main__":
    # Testa a conexão e cria tabelas
    print("🔄 Inicializando banco de dados...")
    criar_tabelas()
    carregar_usuario_teste()
    listar_usuarios()
    listar_produtos()
    print("✅ Banco de dados inicializado com sucesso!")