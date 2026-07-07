import sqlite3 as sqlite


def criarTabela():
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS funcionarios(
                        codigo TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        departamento TEXT NOT NULL,
                        senha TEXT NOT NULL,
                        idade INTEGER NOT NULL
                    )
                ''')
    conexao.commit()
    conexao.close()
    
def inserirFuncionario(nome, codigo, idade, departamento, senha):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
                    INSERT INTO funcionarios (nome, codigo, idade, departamento, senha) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (nome, codigo, idade, departamento, senha))
    conexao.commit()
    conexao.close()

def listarFuncionario():
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row 
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM funcionarios ORDER BY nome")
    dados = cursor.fetchall()
    conexao.close()
    return dados

def autenticar(codigo, senha):
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute("""SELECT * FROM funcionarios WHERE codigo=? AND senha=?""", (codigo, senha))
    dado = cursor.fetchone()
    conexao.close()
    if dado:
        return dado
    else:
        return False
    
def buscarFuncionario(codigo):
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM funcionarios WHERE codigo = ?', (codigo,))
    funcionario = cursor.fetchone()
    conexao.close()
    return funcionario

def atualizar_perfil_usuario(codigo, novo_nome, nova_biografia, nova_foto, novo_genero):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute("""
        UPDATE funcionarios 
        SET nome = ?, biografia = ?, foto = ?, genero = ? 
        WHERE codigo = ?
    """, (novo_nome, nova_biografia, nova_foto, novo_genero, codigo))
    conexao.commit()
    conexao.close()


def alterarSenha(matricula, novaSenha):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('UPDATE funcionarios SET senha = ? WHERE codigo = ?', (novaSenha, matricula))
    conexao.commit()
    conexao.close()

def removerFuncionario(codigo):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM funcionarios WHERE codigo = ?', (codigo,))
    conexao.commit()
    conexao.close()

def removerPostagem(id_postagem, usuario_codigo, is_admin):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    
    if is_admin:
        # Administrador pode apagar qualquer postagem
        cursor.execute('DELETE FROM postagens WHERE id = ?', (id_postagem,))
        cursor.execute('DELETE FROM comentarios WHERE postagem_id = ?', (id_postagem,))
    else:
        # Usuário comum só apaga se for o dono
        cursor.execute('DELETE FROM postagens WHERE id = ? AND usuario_codigo = ?', (id_postagem, usuario_codigo))
        if cursor.rowcount > 0:
            cursor.execute('DELETE FROM comentarios WHERE postagem_id = ?', (id_postagem,))
            
    conexao.commit()
    conexao.close()

def atualizarBiografia(codigo, biografia):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    # Atualiza a coluna biografia do usuário na tabela funcionarios
    cursor.execute("UPDATE funcionarios SET biografia = ? WHERE codigo = ?", (biografia, codigo))
    conexao.commit()
    conexao.close()

def atualizarBanner(codigo_usuario, novo_banner):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute("UPDATE funcionarios SET banner = ? WHERE codigo = ?", (novo_banner, codigo_usuario))
    conexao.commit()
    conexao.close()

def criarTabela():
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS funcionarios(
                        codigo TEXT PRIMARY KEY,
                        nome TEXT NOT NULL,
                        departamento TEXT NOT NULL,
                        senha TEXT NOT NULL,
                        idade INTEGER NOT NULL
                    )
                ''')
    conexao.commit()
    conexao.close()
    
def inserirFuncionario(nome, codigo, idade, departamento, senha):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
                    INSERT INTO funcionarios (nome, codigo, idade, departamento, senha) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (nome, codigo, idade, departamento, senha))
    conexao.commit()
    conexao.close()

def listarFuncionario():
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row 
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM funcionarios ORDER BY nome")
    dados = cursor.fetchall()
    conexao.close()
    return dados

def autenticar(codigo, senha):
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute("""SELECT * FROM funcionarios WHERE codigo=? AND senha=?""", (codigo, senha))
    dado = cursor.fetchone()
    conexao.close()
    if dado:
        return dado
    else:
        return False
    
def buscarFuncionario(codigo):
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM funcionarios WHERE codigo = ?', (codigo,))
    funcionario = cursor.fetchone()
    conexao.close()
    return funcionario


def alterarSenha(matricula, novaSenha):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('UPDATE funcionarios SET senha = ? WHERE codigo = ?', (novaSenha, matricula))
    conexao.commit()
    conexao.close()

def removerFuncionario(codigo):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM funcionarios WHERE codigo = ?', (codigo,))
    conexao.commit()
    conexao.close()

def inicializar_novas_colunas():
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    try:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN biografia TEXT;")
    except sqlite.OperationalError:
        pass 
    try:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN foto TEXT;")
    except sqlite.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN banner TEXT DEFAULT ''")
        conexao.commit()
    except sqlite.OperationalError:
        pass
    # GARANTE A CRIAÇÃO DA COLUNA GENERO
    try:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN genero TEXT;")
    except sqlite.OperationalError:
        pass

    conexao.commit()
    conexao.close()

def criarTabelaPostagensEComentarios():
    """ Cria as estruturas de dados para o feed da rede social """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    
    # Tabela de Postagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postagens(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_codigo TEXT NOT NULL,
            usuario_nome TEXT NOT NULL,
            usuario_avatar TEXT,
            filme_id INTEGER,
            conteudo TEXT NOT NULL,
            imagem TEXT,
            feito_por_ia INTEGER DEFAULT 0,
            modelo_ia TEXT,
            prompt_ia TEXT,
            curtidas INTEGER DEFAULT 0,
            data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(filme_id) REFERENCES filmes(id)
        )
    ''')
    
    # Tabela de Comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postagem_id INTEGER NOT NULL,
            usuario_codigo TEXT NOT NULL,
            usuario_nome TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(postagem_id) REFERENCES postagens(id)
        )
    ''')

    # NOVA TABELA: Vincula uma única curtida por usuário em cada postagem externa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curtidas(
            postagem_id INTEGER,
            usuario_codigo TEXT,
            PRIMARY KEY (postagem_id, usuario_codigo),
            FOREIGN KEY(postagem_id) REFERENCES postagens(id)
        )
    ''')
    conexao.commit()
    conexao.close()


def criarTabelasCinema():
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    
    # Criar Tabela de Estúdios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            imagem TEXT NOT NULL
        )
    ''')
    
    # Criar Tabela de Filmes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filmes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data_lancamento TEXT NOT NULL,
            sinopse TEXT,
            imagem TEXT,
            estudio_id INTEGER,
            FOREIGN KEY(estudio_id) REFERENCES estudios(id)
        )
    ''')
    conexao.commit()
    conexao.close()
    # Executa a migração segura automática
    verificar_e_atualizar_coluna_filme()

def verificar_e_atualizar_coluna_filme():
    """ Garante que a coluna 'imagem' exista caso a tabela já tenha sido criada antes """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    try:
        cursor.execute("ALTER TABLE filmes ADD COLUMN imagem TEXT;")
        conexao.commit()
    except sqlite.OperationalError:
        pass # A coluna já existe, ignora o erro
    conexao.close()

def inserirFilme(titulo, data_lancamento, sinopse, estudio_id, imagem):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    if estudio_id == "":
        estudio_id = None
        
    cursor.execute('''
        INSERT INTO filmes (titulo, data_lancamento, sinopse, estudio_id, imagem) 
        VALUES (?, ?, ?, ?, ?)
    ''', (titulo, data_lancamento, sinopse, estudio_id, imagem))
    conexao.commit()
    conexao.close()

def listarFilmes():
    """ Retorna a lista de filmes com o nome do estúdio correspondente """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    # O LEFT JOIN busca o nome do estúdio na tabela 'estudios' usando o 'estudio_id'
    cursor.execute('''
        SELECT filmes.*, estudios.nome AS estudio_nome 
        FROM filmes 
        LEFT JOIN estudios ON filmes.estudio_id = estudios.id
        ORDER BY filmes.id DESC
    ''')
    dados = cursor.fetchall()
    conexao.close()
    return dados

def listarEstudios():
    """ Retorna todos os estúdios ordenados por nome """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM estudios ORDER BY nome")
    dados = cursor.fetchall()
    conexao.close()
    return dados

def inserirEstudio(nome, imagem):
    """ Insere um novo estúdio no banco de dados """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO estudios (nome, imagem) 
        VALUES (?, ?)
    ''', (nome, imagem))
    conexao.commit()
    conexao.close()

def atualizarFilme(id_filme, titulo, data_lancamento, sinopse, estudio_id, imagem):
    """ Atualiza os dados de um filme existente """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    if estudio_id == "":
        estudio_id = None
        
    cursor.execute('''
        UPDATE filmes 
        SET titulo = ?, data_lancamento = ?, sinopse = ?, estudio_id = ?, imagem = ?
        WHERE id = ?
    ''', (titulo, data_lancamento, sinopse, estudio_id, imagem, id_filme))
    conexao.commit()
    conexao.close()

def atualizarEstudio(id_estudio, nome, imagem):
    """ Atualiza os dados de um estúdio de cinema existente """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE estudios 
        SET nome = ?, imagem = ? 
        WHERE id = ?
    ''', (nome, imagem, id_estudio))
    conexao.commit()
    conexao.close()

def criarTabelaPostagensEComentarios():
    """ Cria as estruturas de dados para o feed da rede social """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    
    # Tabela de Postagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postagens(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_codigo TEXT NOT NULL,
            usuario_nome TEXT NOT NULL,
            usuario_avatar TEXT,
            filme_id INTEGER,
            conteudo TEXT NOT NULL,
            imagem TEXT,
            feito_por_ia INTEGER DEFAULT 0,
            modelo_ia TEXT,
            prompt_ia TEXT,
            curtidas INTEGER DEFAULT 0,
            data_postagem TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(filme_id) REFERENCES filmes(id)
        )
    ''')
    
    # Tabela de Comentários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postagem_id INTEGER NOT NULL,
            usuario_codigo TEXT NOT NULL,
            usuario_nome TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(postagem_id) REFERENCES postagens(id)
        )
    ''')

    # NOVA TABELA: Vincula uma única curtida por usuário em cada postagem externa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curtidas(
            postagem_id INTEGER,
            usuario_codigo TEXT,
            PRIMARY KEY (postagem_id, usuario_codigo),
            FOREIGN KEY(postagem_id) REFERENCES postagens(id)
        )
    ''')
    conexao.commit()
    conexao.close()

def inserirPostagem(usuario_codigo, usuario_nome, usuario_avatar, filme_id, conteudo, imagem, feito_por_ia, modelo_ia, prompt_ia):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    if filme_id == "":
        filme_id = None
    cursor.execute('''
        INSERT INTO postagens (usuario_codigo, usuario_nome, usuario_avatar, filme_id, conteudo, imagem, feito_por_ia, modelo_ia, prompt_ia, curtidas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (usuario_codigo, usuario_nome, usuario_avatar, filme_id, conteudo, imagem, feito_por_ia, modelo_ia, prompt_ia))
    conexao.commit()
    conexao.close()

def listarPostagens():
    """ Retorna as postagens ordenadas pelas mais recentes com seus respectivos comentários acoplados """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT p.*, f.titulo AS filme_titulo 
        FROM postagens p
        LEFT JOIN filmes f ON p.filme_id = f.id
        ORDER BY p.data_postagem DESC
    ''')
    postagens = [dict(row) for row in cursor.fetchall()]
    
    # Anexa os comentários pertencentes a cada postagem de forma aninhada
    for p in postagens:
        cursor.execute('''
            SELECT * FROM comentarios 
            WHERE postagem_id = ? 
            ORDER BY data_comentario ASC
        ''', (p['id'],))
        p['comentarios'] = [dict(row) for row in cursor.fetchall()]
        
    conexao.close()
    return postagens

def listarPostagensPorUsuario(usuario_codigo):
    """ Retorna apenas as postagens de um usuário específico com seus respectivos comentários """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    
    cursor.execute('''
        SELECT p.*, f.titulo AS filme_titulo 
        FROM postagens p
        LEFT JOIN filmes f ON p.filme_id = f.id
        WHERE p.usuario_codigo = ?
        ORDER BY p.data_postagem DESC
    ''', (usuario_codigo,))
    
    postagens = [dict(row) for row in cursor.fetchall()]
    
    # Anexa os comentários pertencentes a cada postagem
    for p in postagens:
        cursor.execute('''
            SELECT * FROM comentarios 
            WHERE postagem_id = ? 
            ORDER BY data_comentario ASC
        ''', (p['id'],))
        p['comentarios'] = [dict(row) for row in cursor.fetchall()]
        
    conexao.close()
    return postagens

def curtirPostagem(id_postagem, usuario_codigo):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    
    # Verifica se este usuário específico já curtiu esta postagem
    cursor.execute('SELECT 1 FROM curtidas WHERE postagem_id = ? AND usuario_codigo = ?', (id_postagem, usuario_codigo))
    ja_curtiu = cursor.fetchone()
    
    if not ja_curtiu:
        # Se não curtiu: registra o voto e adiciona 1 ao contador
        cursor.execute('INSERT INTO curtidas (postagem_id, usuario_codigo) VALUES (?, ?)', (id_postagem, usuario_codigo))
        cursor.execute('UPDATE postagens SET curtidas = curtidas + 1 WHERE id = ?', (id_postagem,))
        curtiu_agora = True
    else:
        # Se já curtiu: remove o registro e retira o voto (Descurtir)
        cursor.execute('DELETE FROM curtidas WHERE postagem_id = ? AND usuario_codigo = ?', (id_postagem, usuario_codigo))
        cursor.execute('UPDATE postagens SET curtidas = MAX(0, curtidas - 1) WHERE id = ?', (id_postagem,))
        curtiu_agora = False
        
    conexao.commit()

    # Recupera o total atualizado de curtidas para devolver ao front-end
    cursor.execute('SELECT curtidas FROM postagens WHERE id = ?', (id_postagem,))
    linha = cursor.fetchone()
    total_curtidas = linha[0] if linha else 0

    conexao.close()

    return {"curtiu": curtiu_agora, "total": total_curtidas}

def listarCurtidasIds(usuario_codigo):
    """ Retorna a lista (em string) dos IDs de postagens que o usuário específico já curtiu.
        Usado para exibir o coração aceso apenas para quem realmente curtiu cada postagem. """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT postagem_id FROM curtidas WHERE usuario_codigo = ?', (str(usuario_codigo),))
    dados = [str(row[0]) for row in cursor.fetchall()]
    conexao.close()
    return dados

def inserirComentario(postagem_id, usuario_codigo, usuario_nome, conteudo):
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO comentarios (postagem_id, usuario_codigo, usuario_nome, conteudo)
        VALUES (?, ?, ?, ?)
    ''', (postagem_id, usuario_codigo, usuario_nome, conteudo))
    conexao.commit()
    conexao.close()

def buscarComentario(id_comentario):
    """ Busca um comentário específico pelo ID """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM comentarios WHERE id = ?', (id_comentario,))
    dado = cursor.fetchone()
    conexao.close()
    return dado

def editarComentario(id_comentario, usuario_codigo, novo_conteudo):
    """ Edita o conteúdo de um comentário. Apenas o próprio dono pode editar (admin não pode editar
        comentário alheio, apenas excluir). A data do comentário é substituída pela data da edição
        e a flag 'editado' é ativada para exibirmos 'editado (data)' no lugar da data original. """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE comentarios 
        SET conteudo = ?, data_comentario = CURRENT_TIMESTAMP, editado = 1
        WHERE id = ? AND usuario_codigo = ?
    ''', (novo_conteudo, id_comentario, str(usuario_codigo)))
    conexao.commit()
    sucesso = cursor.rowcount > 0
    conexao.close()
    return sucesso

def excluirComentario(id_comentario, usuario_codigo, is_admin):
    """ Exclui um comentário do site e do banco de dados. O dono pode excluir o seu próprio
        comentário e o admin pode excluir qualquer comentário. """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    if is_admin:
        cursor.execute('DELETE FROM comentarios WHERE id = ?', (id_comentario,))
    else:
        cursor.execute('DELETE FROM comentarios WHERE id = ? AND usuario_codigo = ?',
                       (id_comentario, str(usuario_codigo)))
    conexao.commit()
    sucesso = cursor.rowcount > 0
    conexao.close()
    return sucesso

def inicializar_colunas_comentarios():
    """ Garante que a coluna 'editado' exista na tabela de comentários,
        mesmo que a tabela já tenha sido criada anteriormente. """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    try:
        cursor.execute("ALTER TABLE comentarios ADD COLUMN editado INTEGER DEFAULT 0;")
        conexao.commit()
    except sqlite.OperationalError:
        pass
    conexao.close()


# =====================================================================
# --- NOVIDADE: SISTEMA DE SEGUIDORES E NOTIFICAÇÕES ---
# =====================================================================

def criarTabelaSeguidoresENotificacoes():
    """ Cria a tabela de seguidores (quem segue quem) e a tabela de notificações """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()

    # Tabela de Seguidores: ID do usuário, ID do usuário que ele segue, data que começou a seguir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seguidores(
            usuario_id TEXT NOT NULL,
            seguido_id TEXT NOT NULL,
            data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (usuario_id, seguido_id)
        )
    ''')

    # Tabela de Notificações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificacoes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            autor_codigo TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            lida INTEGER DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conexao.commit()
    conexao.close()

def toggleSeguir(usuario_codigo, seguido_id):
    """ Segue ou deixa de seguir (alterna o estado) um usuário """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()

    cursor.execute('SELECT 1 FROM seguidores WHERE usuario_id = ? AND seguido_id = ?',
                   (str(usuario_codigo), str(seguido_id)))
    ja_segue = cursor.fetchone()

    if ja_segue:
        cursor.execute('DELETE FROM seguidores WHERE usuario_id = ? AND seguido_id = ?',
                       (str(usuario_codigo), str(seguido_id)))
        seguindo_agora = False
    else:
        cursor.execute('INSERT INTO seguidores (usuario_id, seguido_id) VALUES (?, ?)',
                       (str(usuario_codigo), str(seguido_id)))
        seguindo_agora = True

    conexao.commit()
    conexao.close()
    return seguindo_agora

def verificarSeSegue(usuario_codigo, seguido_id):
    """ Verifica se usuario_codigo já segue seguido_id """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT 1 FROM seguidores WHERE usuario_id = ? AND seguido_id = ?',
                   (str(usuario_codigo), str(seguido_id)))
    resultado = cursor.fetchone()
    conexao.close()
    return True if resultado else False

def listarSeguindoIds(usuario_codigo):
    """ Retorna a lista de códigos (texto) de todos que o usuário segue """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT seguido_id FROM seguidores WHERE usuario_id = ?', (str(usuario_codigo),))
    dados = [str(row[0]) for row in cursor.fetchall()]
    conexao.close()
    return dados

def contarSeguidores(usuario_codigo):
    """ Conta quantas pessoas seguem este usuário """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT COUNT(*) FROM seguidores WHERE seguido_id = ?', (str(usuario_codigo),))
    total = cursor.fetchone()[0]
    conexao.close()
    return total

def contarSeguindo(usuario_codigo):
    """ Conta quantas pessoas este usuário segue """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT COUNT(*) FROM seguidores WHERE usuario_id = ?', (str(usuario_codigo),))
    total = cursor.fetchone()[0]
    conexao.close()
    return total

def contarPosts(usuario_codigo):
    """ Conta quantas postagens o usuário já fez """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('SELECT COUNT(*) FROM postagens WHERE usuario_codigo = ?', (str(usuario_codigo),))
    total = cursor.fetchone()[0]
    conexao.close()
    return total

def criarNotificacoesParaSeguidores(usuario_codigo, usuario_nome):
    """ Sempre que o usuário publica algo novo, gera uma notificação para cada um de seus seguidores """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()

    cursor.execute('SELECT usuario_id FROM seguidores WHERE seguido_id = ?', (str(usuario_codigo),))
    seguidores = cursor.fetchall()

    mensagem = f"{usuario_nome} fez uma nova publicação"

    for (seguidor_id,) in seguidores:
        cursor.execute('''
            INSERT INTO notificacoes (usuario_id, autor_codigo, mensagem)
            VALUES (?, ?, ?)
        ''', (seguidor_id, str(usuario_codigo), mensagem))

    conexao.commit()
    conexao.close()

def listarNotificacoes(usuario_codigo):
    """ Retorna as notificações não lidas mais recentes de um usuário """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT * FROM notificacoes
        WHERE usuario_id = ? AND lida = 0
        ORDER BY data_criacao DESC
    ''', (str(usuario_codigo),))
    dados = cursor.fetchall()
    conexao.close()
    return dados

def buscarNotificacao(id_notificacao):
    """ Busca uma notificação específica pelo ID """
    conexao = sqlite.connect('database.sqlite')
    conexao.row_factory = sqlite.Row
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM notificacoes WHERE id = ?', (id_notificacao,))
    dado = cursor.fetchone()
    conexao.close()
    return dado

def marcarNotificacaoLida(id_notificacao):
    """ Marca uma notificação como lida """
    conexao = sqlite.connect('database.sqlite')
    cursor = conexao.cursor()
    cursor.execute('UPDATE notificacoes SET lida = 1 WHERE id = ?', (id_notificacao,))
    conexao.commit()
    conexao.close()


criarTabelasCinema()
inicializar_novas_colunas()
inicializar_colunas_comentarios()
