from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from functools import wraps
import controlador_BD

app = Flask(__name__)
app.secret_key = "chave_secreta"

# Código especial que, quando informado corretamente no cadastro, define o
# departamento do novo usuário como "Admin" em vez do padrão "Membro".
CODIGO_ESPECIAL_ADMIN = "&Mm7951@!"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

controlador_BD.criarTabela()

def verificar(func):
    @wraps(func)
    def verificarLogado(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home"))
        return func(*args, **kwargs)
    return verificarLogado

def verificar_adm(func):
    @wraps(func)
    def verificarLogado(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home"))

        if not session.get("user", {}).get("isAdmin"):
            msg = "Acesso negado."
            return render_template("logado.html", mensagem=msg)

        return func(*args, **kwargs)
    return verificarLogado


def autenticar(func): 
    @wraps(func)
    def autenticar_usuario(*args, **kwargs):
        codigo = request.form.get("codigoUsuario") or request.form.get("matricula")
        senha = request.form.get("senhaUsuario") or request.form.get("senha")

        if not codigo or not senha:
            msg = "Por favor, preencha o código e a senha."
            return render_template("home.html", mensagem=msg)

        try:
            codigo = int(codigo)
        except ValueError:
            msg = "O código deve conter apenas números."
            return render_template("home.html", mensagem=msg)

        logado = controlador_BD.autenticar(codigo, senha)
        
        if logado:
            session["usuario"] = codigo 
            session["codigo"] = codigo

            return func(*args, **kwargs)
        else:
            msg = "Usuário ou senha incorretos."
            return render_template("home.html", mensagem=msg)


    return autenticar_usuario

@app.route('/')
def home():
    if "usuario" in session:
        return redirect(url_for("rotaLogado"))
    postagens = controlador_BD.listarPostagens()
    return render_template("home.html", logado=False, postagens=postagens)

@app.route('/autenticar', methods=['POST'])
def autenticar():

    codigo = request.form.get('codigoUsuario')
    senha = request.form.get('senhaUsuario')

    usuario_banco = controlador_BD.autenticar(codigo, senha)

    if usuario_banco:
        #eh_admin = True if usuario_banco['departamento'].lower() == 'admin' else False
        
        #avatar_gerado = f"https://ui-avatars.com/api/?name={usuario_banco['nome']}&background=8b5cf6&color=fff&rounded=true"

        session['user'] = {
            'name': usuario_banco['nome'],
            'codigo': usuario_banco['codigo'],
            'departamento': usuario_banco['departamento'],
            'isAdmin': True if usuario_banco['departamento'].lower() == 'admin' else False,
            'biografia': usuario_banco['biografia'] if 'biografia' in usuario_banco.keys() else "",
            'banner': usuario_banco['banner'] if ('banner' in usuario_banco.keys() and usuario_banco['banner']) else "",
            'avatar': usuario_banco['foto'] if ('foto' in usuario_banco.keys() and usuario_banco['foto']) else f"https://ui-avatars.com/api/?name={usuario_banco['nome']}&background=8b5cf6&color=fff&rounded=true"
        }
        
        
        return redirect('/logado')
    
    else:
        postagens = controlador_BD.listarPostagens()
        return render_template('home.html', login_mensagem="Código ou senha incorretos!", postagens=postagens)


controlador_BD.criarTabelaPostagensEComentarios()
controlador_BD.criarTabelaSeguidoresENotificacoes()

@app.route("/logado")
@verificar
def feed_logado():

    filmes = controlador_BD.listarFuncionario() 

    if hasattr(controlador_BD, 'listarFilmes'):
        filmes = controlador_BD.listarFilmes()
        
    postagens = controlador_BD.listarPostagens()
    return render_template("logado.html", filmes=filmes, postagens=postagens)

@app.route("/logado/nova_postagem", methods=["POST"])
@verificar
def nova_postagem():
    
    usuario_codigo = session['user']['codigo']
    usuario_nome = session['user']['name']
    usuario_avatar = session['user'].get('avatar')

    filme_id = request.form.get('filme_id')
    conteudo = request.form.get('conteudo')
    
    feito_por_ia = int(request.form.get('feito_por_ia', 0))
    modelo_ia = request.form.get('modelo_ia') if feito_por_ia else None
    prompt_ia = request.form.get('prompt_ia') if feito_por_ia else None

    # Tratamento de Imagens Unificado (Arquivo local ou URL externa)
    imagem_url = request.form.get('imagem_url', '').strip()
    file = request.files.get('imagem_arquivo')
    
    imagem_final = None
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagem_final = '/' + app.config['UPLOAD_FOLDER'] + '/' + filename
    elif imagem_url:
        imagem_final = imagem_url

    controlador_BD.inserirPostagem(
        usuario_codigo, usuario_nome, usuario_avatar, 
        filme_id, conteudo, imagem_final, 
        feito_por_ia, modelo_ia, prompt_ia
    )

    # --- NOVIDADE: GERA NOTIFICAÇÕES PARA QUEM SEGUE ESSE USUÁRIO ---
    controlador_BD.criarNotificacoesParaSeguidores(usuario_codigo, usuario_nome)

    return redirect(url_for('feed_logado'))

@app.route("/logado/excluir/<int:id_postagem>", methods=["POST"])
@verificar
def excluir_postagem(id_postagem):

    usuario_codigo = session['user']['codigo']
    is_admin = session['user']['isAdmin']
    
    controlador_BD.removerPostagem(id_postagem, usuario_codigo, is_admin)
    
    return redirect(request.referrer or url_for('feed_logado'))

@app.route("/salvar-biografia", methods=["POST"])
@verificar
def salvar_biografia():
    nova_bio = request.form.get("novaBiografia")
    usuario_codigo = session['user']['codigo']
    
    controlador_BD.atualizarBiografia(usuario_codigo, nova_bio)
    
    session['user']['biografia'] = nova_bio
    session.modified = True
    
    return redirect(url_for('rotaPerfil'))

@app.route("/logado/curtir/<int:id_postagem>", methods=["POST"])
@verificar
def curtir_feed(id_postagem):
    # Recupera o identificador único do usuário conectado na sessão
    usuario_codigo = session['user']['codigo']
    
    # Passa o ID da postagem e o código do usuário para controle único de curtidas
    resultado = controlador_BD.curtirPostagem(id_postagem, usuario_codigo)

    # Se a requisição veio via JavaScript (fetch/AJAX), respondemos em JSON
    # para que a página não precise recarregar nem perder a posição de rolagem.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True, curtiu=resultado['curtiu'], total=resultado['total'])

    return redirect(request.referrer or url_for('feed_logado'))

@app.route("/logado/curtidas/<int:id_postagem>")
@verificar
def listarCurtidasPostagem(id_postagem):
    """ Retorna em JSON a lista de usuários que curtiram a postagem (usado pelo pop-up de Status) """
    usuarios = controlador_BD.listarCurtidasDoPost(id_postagem)
    return jsonify(usuarios=usuarios)

@app.route("/logado/comentar/<int:id_postagem>", methods=["POST"])
@verificar
def comentar_feed(id_postagem):

    usuario_codigo = session['user']['codigo']
    usuario_nome = session['user']['name']
    conteudo = request.form.get('conteudo_comentario')

    if conteudo:
        controlador_BD.inserirComentario(id_postagem, usuario_codigo, usuario_nome, conteudo)
    return redirect(request.referrer or url_for('feed_logado'))

@app.route("/logado/comentario/editar/<int:id_comentario>", methods=["POST"])
@verificar
def editar_comentario(id_comentario):
    """ Permite que o autor do comentário edite seu próprio conteúdo.
        Ao editar, a data de publicação é substituída pela data da edição
        e o comentário passa a exibir 'editado (data)' no lugar da data original. """
    usuario_codigo = session['user']['codigo']
    novo_conteudo = (request.form.get('conteudo_comentario_editado') or '').strip()

    if novo_conteudo:
        controlador_BD.editarComentario(id_comentario, usuario_codigo, novo_conteudo)

    return redirect(request.referrer or url_for('feed_logado'))

@app.route("/logado/comentario/excluir/<int:id_comentario>", methods=["POST"])
@verificar
def excluir_comentario(id_comentario):
    """ Remove o comentário do site e do banco de dados.
        O próprio autor pode excluir seu comentário, e o admin pode excluir qualquer um. """
    usuario_codigo = session['user']['codigo']
    is_admin = session['user']['isAdmin']

    controlador_BD.excluirComentario(id_comentario, usuario_codigo, is_admin)

    return redirect(request.referrer or url_for('feed_logado'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route("/perfil")
@app.route("/perfil/<string:usuario_codigo>")
@verificar
def rotaPerfil(usuario_codigo=None):

    meu_codigo = session['user']['codigo']

    if usuario_codigo is None or str(usuario_codigo) == str(meu_codigo):
        codigo_alvo = meu_codigo
        eh_meu_perfil = True
    else:
        codigo_alvo = usuario_codigo
        eh_meu_perfil = False

    usuario_banco = controlador_BD.buscarFuncionario(codigo_alvo)

    if not usuario_banco:
        return redirect(url_for('rotaPerfil'))

    # Dicionário do usuário dono do perfil que está sendo exibido no momento
    perfil_user = {
        'name': usuario_banco['nome'],
        'codigo': usuario_banco['codigo'],
        'departamento': usuario_banco['departamento'],
        'isAdmin': True if usuario_banco['departamento'].lower() == 'admin' else False,
        'genero': usuario_banco['genero'] if ('genero' in usuario_banco.keys() and usuario_banco['genero']) else None,
        'biografia': usuario_banco['biografia'] if ('biografia' in usuario_banco.keys() and usuario_banco['biografia']) else "",
        'banner': usuario_banco['banner'] if ('banner' in usuario_banco.keys() and usuario_banco['banner']) else None,
        'avatar': usuario_banco['foto'] if ('foto' in usuario_banco.keys() and usuario_banco['foto']) else f"https://ui-avatars.com/api/?name={usuario_banco['nome']}&background=8b5cf6&color=fff&rounded=true"
    }

    postagens_usuario = controlador_BD.listarPostagensPorUsuario(codigo_alvo)

    # Métricas calculadas em tempo real com base no banco de dados
    total_posts = controlador_BD.contarPosts(codigo_alvo)
    total_seguidores = controlador_BD.contarSeguidores(codigo_alvo)
    total_seguindo = controlador_BD.contarSeguindo(codigo_alvo)

    ja_segue = controlador_BD.verificarSeSegue(meu_codigo, codigo_alvo)

    return render_template(
        "perfil.html",
        postagens=postagens_usuario,
        perfil_user=perfil_user,
        eh_meu_perfil=eh_meu_perfil,
        total_posts=total_posts,
        total_seguidores=total_seguidores,
        total_seguindo=total_seguindo,
        ja_segue=ja_segue
    )

@app.route("/perfil/<string:usuario_codigo>/seguidores")
@verificar
def listarSeguidoresPerfil(usuario_codigo):
    """ Retorna em JSON a lista de quem segue o usuário informado (pop-up de Seguidores) """
    usuarios = controlador_BD.listarSeguidoresDetalhado(usuario_codigo)
    return jsonify(usuarios=usuarios)

@app.route("/perfil/<string:usuario_codigo>/seguindo")
@verificar
def listarSeguindoPerfil(usuario_codigo):
    """ Retorna em JSON a lista de quem o usuário informado segue (pop-up de Seguindo) """
    usuarios = controlador_BD.listarSeguindoDetalhado(usuario_codigo)
    return jsonify(usuarios=usuarios)

# =====================================================================
# --- NOVIDADE: SEGUIR USUÁRIOS E NOTIFICAÇÕES ---
# =====================================================================

@app.route("/seguir/<string:seguido_id>", methods=["POST"])
@verificar
def seguir_usuario(seguido_id):
    usuario_codigo = session['user']['codigo']
    seguindo_agora = None

    if str(usuario_codigo) != str(seguido_id):
        seguindo_agora = controlador_BD.toggleSeguir(usuario_codigo, seguido_id)

    # Se a requisição veio via JavaScript (fetch/AJAX), respondemos em JSON
    # para que a página não precise recarregar nem perder a posição de rolagem.
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(success=True, seguindo=seguindo_agora)

    return redirect(request.referrer or url_for('feed_logado'))

@app.route("/notificacao/clicar/<int:id_notificacao>")
@verificar
def clicar_notificacao(id_notificacao):
    notificacao = controlador_BD.buscarNotificacao(id_notificacao)
    controlador_BD.marcarNotificacaoLida(id_notificacao)

    if notificacao:
        return redirect(url_for('rotaPerfil', usuario_codigo=notificacao['autor_codigo']))

    return redirect(url_for('feed_logado'))

@app.context_processor
def inject_dados_sociais():
    """ Disponibiliza as notificações e a lista de quem o usuário segue em qualquer template """
    if "user" in session:
        usuario_codigo = session['user']['codigo']
        notificacoes = controlador_BD.listarNotificacoes(usuario_codigo)
        lista_seguindo = controlador_BD.listarSeguindoIds(usuario_codigo)
        lista_curtidas = controlador_BD.listarCurtidasIds(usuario_codigo)
        return dict(notificacoes=notificacoes, lista_seguindo=lista_seguindo, lista_curtidas=lista_curtidas)
    return dict(notificacoes=[], lista_seguindo=[], lista_curtidas=[])


@app.route('/database')
@verificar_adm  
def rotaDatabase():
    filmes = controlador_BD.listarFilmes()
    estudios = controlador_BD.listarEstudios()
    return render_template("database.html", filmes=filmes, estudios=estudios)

@app.route('/database/novo_filme', methods=['POST'])
@verificar_adm  
def cadastrarFilme():
    titulo = request.form.get('titulo')
    data_lancamento = request.form.get('data_lancamento')
    sinopse = request.form.get('sinopse')
    estudio_id = request.form.get('estudio_id')

    # Tratamento de Imagens Unificado (Arquivo local ou URL externa),
    # igual ao que já é feito na edição de filme.
    imagem_url = request.form.get('imagem_url', '').strip()
    caminho_foto = None

    if 'imagem_arquivo' in request.files:
        file = request.files['imagem_arquivo']
        if file and file.filename != '':
            filename = secure_filename(f"filme_{file.filename}")
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho_salvar)
            caminho_foto = f"/{app.config['UPLOAD_FOLDER']}/{filename}"

    if not caminho_foto and imagem_url:
        caminho_foto = imagem_url

    if not titulo or not data_lancamento:
        return redirect(url_for('rotaDatabase'))
        
    controlador_BD.inserirFilme(titulo, data_lancamento, sinopse, estudio_id, caminho_foto)
    return redirect(url_for('rotaDatabase'))

@app.route('/database/novo_estudio', methods=['POST'])
@verificar_adm
def cadastrarEstudio():
    nome = request.form.get('nome')
    imagem_url = request.form.get('imagem_url')
    
    if not nome:
        return redirect(url_for('rotaDatabase'))
        
    caminho_foto = imagem_url
    
    if 'imagem_arquivo' in request.files:
        file = request.files['imagem_arquivo']
        if file and file.filename != '':
            filename = secure_filename(f"estudio_{file.filename}")
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho_salvar)
            caminho_foto = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
            
    if not caminho_foto:
        caminho_foto = f"https://ui-avatars.com/api/?name={nome}&background=8b5cf6&color=fff&rounded=true"
        
    controlador_BD.inserirEstudio(nome, caminho_foto)
    return redirect(url_for('rotaDatabase'))

@app.route('/database/editar_filme', methods=['POST'])
@verificar_adm
def editarFilme():
    id_filme = request.form.get('id')
    titulo = request.form.get('titulo')
    data_lancamento = request.form.get('data_lancamento')
    sinopse = request.form.get('sinopse')
    estudio_id = request.form.get('estudio_id')
    imagem_url = request.form.get('imagem_url')
    imagem_atual = request.form.get('imagem_atual') # Pega a imagem antiga se nenhuma nova for enviada
    
    caminho_foto = imagem_url if imagem_url else imagem_atual
    
    if 'imagem_arquivo' in request.files:
        file = request.files['imagem_arquivo']
        if file and file.filename != '':
            filename = secure_filename(f"filme_{file.filename}")
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho_salvar)
            caminho_foto = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
            
    if not caminho_foto:
        caminho_foto = "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400"
        
    controlador_BD.atualizarFilme(id_filme, titulo, data_lancamento, sinopse, estudio_id, caminho_foto)
    return redirect(url_for('rotaDatabase'))

@app.route('/database/editar_estudio', methods=['POST'])
@verificar_adm
def editarEstudio():
    id_estudio = request.form.get('id')
    nome = request.form.get('nome')
    imagem_url = request.form.get('imagem_url')
    imagem_atual = request.form.get('imagem_atual')
    
    caminho_foto = imagem_url if imagem_url else imagem_atual
    
    if 'imagem_arquivo' in request.files:
        file = request.files['imagem_arquivo']
        if file and file.filename != '':
            filename = secure_filename(f"estudio_{file.filename}")
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(caminho_salvar)
            caminho_foto = f"/{app.config['UPLOAD_FOLDER']}/{filename}"
            
    if not caminho_foto:
        caminho_foto = "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?q=80&w=400"
        
    controlador_BD.atualizarEstudio(id_estudio, nome, caminho_foto)
    return redirect(url_for('rotaDatabase'))

@app.route('/atualizar-perfil', methods=['POST'])
def atualizar_perfil():
    nome = request.form.get('nome')
    genero = request.form.get('genero')
    if genero == 'Outro':
        genero = request.form.get('genero_customizado')
        
    avatar_url = request.form.get('avatar_url')
    avatar_file = request.files.get('avatar')
    
    avatar_final = session['user']['avatar']

    # O upload de arquivo tem prioridade sobre a URL: se um arquivo for enviado, ele é
    # usado; caso contrário, se uma URL for informada, ela é usada; senão mantém a atual.
    if avatar_file and avatar_file.filename != '':
        nome_arquivo = secure_filename(avatar_file.filename)
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        avatar_file.save(caminho)
        avatar_final = '/' + caminho
    elif avatar_url and avatar_url.strip():
        avatar_final = avatar_url.strip()
        
    # --- NOVIDADE: RECUPERANDO DADOS E SALVANDO NO BANCO ---
    codigo_usuario = session['user']['codigo']
    biografia_atual = session['user'].get('biografia', '')
    
    # Chama o banco de dados para salvar de forma permanente
    controlador_BD.atualizar_perfil_usuario(codigo_usuario, nome, biografia_atual, avatar_final, genero)
    # -------------------------------------------------------

    # Atualizando a sessão visual
    session['user']['name'] = nome
    session['user']['genero'] = genero
    session['user']['avatar'] = avatar_final
    session.modified = True
    
    return redirect('/perfil')

# --- NOVIDADE: BANNER DO PERFIL (agora editado via pop-up próprio, com o botão de lápis) ---
@app.route('/atualizar-banner', methods=['POST'])
@verificar
def atualizar_banner():
    banner_url = request.form.get('banner_url', '').strip()
    codigo_usuario = session['user']['codigo']
    banner_final = banner_url if banner_url else session['user'].get('banner', '')

    controlador_BD.atualizarBanner(codigo_usuario, banner_final)

    session['user']['banner'] = banner_final
    session.modified = True

    return redirect(url_for('rotaPerfil'))
# -----------------------------------------------------------------------------------------

@app.route("/cadastrar", methods=['GET'])
def exibirCadastro():
    return render_template("cadastrar_usuario.html")

@app.route("/cadastrar", methods=['POST'])
def cadastrarFuncionario():
    matricula = request.form.get("codigo") 
    nome = request.form.get("nome")
    idade = int(request.form.get("idade") or 0)
    senha = request.form.get("senha")

    # O departamento NUNCA é lido diretamente do campo enviado pelo formulário
    # (esse campo é só visual). Quem decide se o usuário é "Admin" ou "Membro"
    # é sempre o servidor, comparando o código especial digitado no pop-up.
    codigo_especial = request.form.get("codigo_especial", "")
    departamento = "Admin" if codigo_especial == CODIGO_ESPECIAL_ADMIN else "Membro"

    controlador_BD.inserirFuncionario(nome, matricula, idade, departamento, senha)
    
    mensagem = f"Usuário {nome} adicionado com sucesso."
    return render_template("cadastrar_usuario.html", mensagem=mensagem)

@app.route("/listar", methods=['GET', 'POST'])
@verificar
def rotaListar():
    return render_template("listar.html", lista=controlador_BD.listarFuncionario())

@app.route("/listar2")
@verificar
def rotaListar2():
    funcionarios = controlador_BD.listarFuncionario()
    mensagem = ""
    for f in funcionarios:

        mensagem += f"""
            <tr>
            <td>{f['nome']}</td>
            <td>{f['idade']}</td>
            <td>{f['departamento']}</td>
            </tr> <br>
        """
    return render_template("listar2.html", mensagem=mensagem)


@app.route('/alterar-senha', methods=['POST'])
def atualizar_senha():
    if not session.get('user'):
        return redirect('/')
    
    codigo_manual = request.form.get('codigo_confirmacao')
    senha_atual = request.form.get('senha_atual')
    senha_nova = request.form.get('senha_nova')

    usuario_valido = controlador_BD.autenticar(codigo_manual, senha_atual)

    if usuario_valido:
        controlador_BD.alterarSenha(codigo_manual, senha_nova)

        if codigo_manual == session['user']['codigo']:
            session['user']['senha'] = senha_nova
            session.modified = True
            
        return render_template('perfil.html', mensagem="Sua senha foi alterada com sucesso no banco de dados!")
    else:
        return render_template('perfil.html', mensagem="Erro: Validação falhou! Código do usuário ou senha atual incorretos.")

@app.route("/painel_admin")
@verificar_adm
def painel_admin():
    return render_template("painel_admin.html")

@app.route("/admin/usuarios")
@verificar_adm
def admin_usuarios():
    usuarios = controlador_BD.listarUsuariosDetalhado()
    return render_template("admin_usuarios.html", usuarios=usuarios)

@app.route("/admin/usuarios/excluir/<codigo>", methods=["POST", "GET"])
@verificar_adm
def excluir_usuario(codigo):
    controlador_BD.removerUsuario(codigo)
    return redirect(url_for("admin_usuarios"))

def buscarFuncionario(codigo):
    if not codigo:
        return None
    funcionario = controlador_BD.buscarFuncionario(codigo)
    if funcionario:
        return funcionario
    return None

@app.after_request
def adicionar_cabecalhos_sem_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
