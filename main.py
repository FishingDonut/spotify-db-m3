import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine

app = Flask(__name__)

# DB CONFIG START ----------------------------- |
# Connect to the 'spotify' database as defined in schema.sql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/spotify'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# DB CONFIG END ------------------------------- |

# Models Start ----------------------------- |

class Artista(db.Model):
    __tablename__ = 'Artista'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(45), nullable=False)
    descricao = db.Column(db.Text)
    seguidores = db.Column(db.Integer, default=0)
    ouvintes_mensais = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'seguidores': self.seguidores,
            'ouvintes_mensais': self.ouvintes_mensais
        }

class Album(db.Model):
    __tablename__ = 'Album'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(45), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    id_artista = db.Column(db.BigInteger, db.ForeignKey('Artista.id'), nullable=False)
    genero = db.Column(db.String(45))
    capa_url = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'ano': self.ano,
            'id_artista': self.id_artista,
            'genero': self.genero,
            'capa_url': self.capa_url
        }

class Musica(db.Model):
    __tablename__ = 'Musica'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)
    reproducoes = db.Column(db.Integer, default=0)
    letra = db.Column(db.Text)
    genero = db.Column(db.String(45))
    ano = db.Column(db.Integer, nullable=False)
    id_album = db.Column(db.BigInteger, db.ForeignKey('Album.id'), nullable=True)
    id_artista = db.Column(db.BigInteger, db.ForeignKey('Artista.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'duracao': self.duracao,
            'reproducoes': self.reproducoes,
            'letra': self.letra,
            'genero': self.genero,
            'ano': self.ano,
            'id_album': self.id_album,
            'id_artista': self.id_artista
        }

class Plano(db.Model):
    __tablename__ = 'Plano'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(15), nullable=False)
    modalidade = db.Column(db.String(15), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    descricao = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'modalidade': self.modalidade,
            'valor': float(self.valor) if self.valor is not None else 0.0,
            'descricao': self.descricao
        }

class Pagamento(db.Model):
    __tablename__ = 'Pagamento'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_plano = db.Column(db.BigInteger, db.ForeignKey('Plano.id'), nullable=False)
    data_assinatura = db.Column(db.Date, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Ativo')

    def to_dict(self):
        return {
            'id': self.id,
            'id_plano': self.id_plano,
            'data_assinatura': self.data_assinatura.isoformat() if self.data_assinatura else None,
            'vencimento': self.vencimento.isoformat() if self.vencimento else None,
            'status': self.status
        }

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    data_nascimento = db.Column(db.Date)
    pais = db.Column(db.String(45))
    id_pagamento = db.Column(db.BigInteger, db.ForeignKey('Pagamento.id'), nullable=True)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'pais': self.pais,
            'id_pagamento': self.id_pagamento,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class HistoricoReproducao(db.Model):
    __tablename__ = 'Historico_Reproducao'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('Usuario.id', ondelete='CASCADE'), nullable=False)
    id_musica = db.Column(db.BigInteger, db.ForeignKey('Musica.id', ondelete='CASCADE'), nullable=False)
    data_reproducao = db.Column(db.DateTime, default=db.func.current_timestamp())

# Model End ------------------------------- |

# Database Seeding Helper Start ------------- |

def init_db():
    """Reads schema.sql, cleans it, and executes statement-by-statement in MySQL."""
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    base_uri, _ = uri.rsplit('/', 1)
    
    # Connect directly to MySQL server without selecting database first
    temp_engine = create_engine(base_uri)
    
    with temp_engine.connect() as conn:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        statements = []
        current_stmt = []
        in_trigger = False
        
        for line in sql_script.split('\n'):
            # Strip SQL comments first
            line_clean = line
            if '--' in line:
                line_clean = line.split('--', 1)[0]
            elif '#' in line:
                line_clean = line.split('#', 1)[0]
                
            line_strip = line_clean.strip()
            if not line_strip:
                continue
                
            if 'DELIMITER //' in line_strip:
                in_trigger = True
                continue
            if 'DELIMITER ;' in line_strip:
                in_trigger = False
                if current_stmt:
                    statements.append('\n'.join(current_stmt))
                    current_stmt = []
                continue
                
            if in_trigger:
                line_no_delim = line_clean.replace('//', '')
                current_stmt.append(line_no_delim)
                if '//' in line_clean:
                    statements.append('\n'.join(current_stmt))
                    current_stmt = []
            else:
                current_stmt.append(line_clean)
                if line_strip.endswith(';'):
                    statements.append('\n'.join(current_stmt))
                    current_stmt = []
                    
        with conn.begin():
            for statement in statements:
                stmt_text = statement.strip()
                if stmt_text:
                    conn.execute(text(stmt_text))

# Database Seeding Helper End --------------- |

# Routes Start ----------------------------- |

@app.route('/')
def index():
    return render_template('index.html')

# --- HELPERS (PLANOS & PAGAMENTOS) ---

@app.route('/api/planos', methods=['GET'])
def get_planos():
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT id, tipo, modalidade, valor, descricao FROM Plano;
    planos = Plano.query.all()
    sql_log = "SELECT id, tipo, modalidade, valor, descricao FROM Plano;"
    return jsonify({
        'data': [p.to_dict() for p in planos],
        'sql': sql_log
    })

@app.route('/api/pagamentos', methods=['GET'])
def get_pagamentos():
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT Pagamento.id, Pagamento.id_plano, Pagamento.data_assinatura, Pagamento.vencimento, Pagamento.status, Plano.tipo FROM Pagamento JOIN Plano ON Pagamento.id_plano = Plano.id;
    pagamentos = db.session.query(Pagamento, Plano.tipo).join(Plano, Pagamento.id_plano == Plano.id).all()
    
    data = []
    for pag, tipo_plano in pagamentos:
        d = pag.to_dict()
        d['plano_tipo'] = tipo_plano
        data.append(d)
        
    sql_log = "SELECT Pagamento.id, Pagamento.id_plano, Pagamento.data_assinatura, Pagamento.vencimento, Pagamento.status, Plano.tipo FROM Pagamento JOIN Plano ON Pagamento.id_plano = Plano.id;"
    return jsonify({
        'data': data,
        'sql': sql_log
    })

# --- CRUD ARTISTA ---

@app.route('/api/artistas', methods=['GET'])
def get_artistas():
    search = request.args.get('search', '')
    if search:
        # COMENTÁRIO SQL ABSTRAÍDO:
        # SELECT * FROM Artista WHERE nome LIKE :search;
        artistas = Artista.query.filter(Artista.nome.like(f"%{search}%")).all()
        sql_log = f"SELECT * FROM Artista WHERE nome LIKE '%{search}%';"
    else:
        # COMENTÁRIO SQL ABSTRAÍDO:
        # SELECT * FROM Artista;
        artistas = Artista.query.all()
        sql_log = "SELECT * FROM Artista;"
        
    return jsonify({
        'data': [a.to_dict() for a in artistas],
        'sql': sql_log
    })

@app.route('/api/artistas', methods=['POST'])
def create_artista():
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao')
    seguidores = int(data.get('seguidores', 0) or 0)
    ouvintes_mensais = int(data.get('ouvintes_mensais', 0) or 0)
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    # COMENTÁRIO SQL ABSTRAÍDO:
    # INSERT INTO Artista (nome, descricao, seguidores, ouvintes_mensais) VALUES (:nome, :descricao, :seguidores, :ouvintes_mensais);
    artista = Artista(nome=nome, descricao=descricao, seguidores=seguidores, ouvintes_mensais=ouvintes_mensais)
    db.session.add(artista)
    db.session.commit()
    
    sql_log = f"INSERT INTO Artista (nome, descricao, seguidores, ouvintes_mensais) VALUES ('{nome}', '{descricao or ''}', {seguidores}, {ouvintes_mensais});"
    return jsonify({
        'data': artista.to_dict(),
        'sql': sql_log
    })

@app.route('/api/artistas/<int:id>', methods=['PUT'])
def update_artista(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Artista WHERE id = :id;
    artista = Artista.query.get_or_404(id)
    
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao')
    seguidores = int(data.get('seguidores', 0) or 0)
    ouvintes_mensais = int(data.get('ouvintes_mensais', 0) or 0)
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    artista.nome = nome
    artista.descricao = descricao
    artista.seguidores = seguidores
    artista.ouvintes_mensais = ouvintes_mensais
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # UPDATE Artista SET nome = :nome, descricao = :descricao, seguidores = :seguidores, ouvintes_mensais = :ouvintes_mensais WHERE id = :id;
    db.session.commit()
    
    sql_log = f"UPDATE Artista SET nome = '{nome}', descricao = '{descricao or ''}', seguidores = {seguidores}, ouvintes_mensais = {ouvintes_mensais} WHERE id = {id};"
    return jsonify({
        'data': artista.to_dict(),
        'sql': sql_log
    })

@app.route('/api/artistas/<int:id>', methods=['DELETE'])
def delete_artista(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Artista WHERE id = :id;
    artista = Artista.query.get_or_404(id)
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # DELETE FROM Artista WHERE id = :id;
    db.session.delete(artista)
    db.session.commit()
    
    sql_log = f"DELETE FROM Artista WHERE id = {id};"
    return jsonify({
        'status': 'success',
        'sql': sql_log
    })

# --- CRUD ALBUM ---

@app.route('/api/albuns', methods=['GET'])
def get_albuns():
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT Album.*, Artista.nome AS artista_nome FROM Album JOIN Artista ON Album.id_artista = Artista.id;
    albuns = db.session.query(Album, Artista.nome).join(Artista, Album.id_artista == Artista.id).all()
    
    data = []
    for alb, art_nome in albuns:
        d = alb.to_dict()
        d['artista_nome'] = art_nome
        data.append(d)
        
    sql_log = "SELECT Album.*, Artista.nome AS artista_nome FROM Album JOIN Artista ON Album.id_artista = Artista.id;"
    return jsonify({
        'data': data,
        'sql': sql_log
    })

@app.route('/api/albuns', methods=['POST'])
def create_album():
    data = request.json
    titulo = data.get('titulo')
    ano = int(data.get('ano', datetime.datetime.now().year))
    id_artista = data.get('id_artista')
    genero = data.get('genero')
    capa_url = data.get('capa_url')
    
    if not titulo or not id_artista:
        return jsonify({'error': 'Titulo e Artista são obrigatórios'}), 400
        
    # COMENTÁRIO SQL ABSTRAÍDO:
    # INSERT INTO Album (titulo, ano, id_artista, genero, capa_url) VALUES (:titulo, :ano, :id_artista, :genero, :capa_url);
    album = Album(titulo=titulo, ano=ano, id_artista=id_artista, genero=genero, capa_url=capa_url)
    db.session.add(album)
    db.session.commit()
    
    sql_log = f"INSERT INTO Album (titulo, ano, id_artista, genero, capa_url) VALUES ('{titulo}', {ano}, {id_artista}, '{genero or ''}', '{capa_url or ''}');"
    return jsonify({
        'data': album.to_dict(),
        'sql': sql_log
    })

@app.route('/api/albuns/<int:id>', methods=['PUT'])
def update_album(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Album WHERE id = :id;
    album = Album.query.get_or_404(id)
    
    data = request.json
    titulo = data.get('titulo')
    ano = int(data.get('ano', datetime.datetime.now().year))
    id_artista = data.get('id_artista')
    genero = data.get('genero')
    capa_url = data.get('capa_url')
    
    if not titulo or not id_artista:
        return jsonify({'error': 'Titulo e Artista são obrigatórios'}), 400
        
    album.titulo = titulo
    album.ano = ano
    album.id_artista = id_artista
    album.genero = genero
    album.capa_url = capa_url
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # UPDATE Album SET titulo = :titulo, ano = :ano, id_artista = :id_artista, genero = :genero, capa_url = :capa_url WHERE id = :id;
    db.session.commit()
    
    sql_log = f"UPDATE Album SET titulo = '{titulo}', ano = {ano}, id_artista = {id_artista}, genero = '{genero or ''}', capa_url = '{capa_url or ''}' WHERE id = {id};"
    return jsonify({
        'data': album.to_dict(),
        'sql': sql_log
    })

@app.route('/api/albuns/<int:id>', methods=['DELETE'])
def delete_album(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Album WHERE id = :id;
    album = Album.query.get_or_404(id)
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # DELETE FROM Album WHERE id = :id;
    db.session.delete(album)
    db.session.commit()
    
    sql_log = f"DELETE FROM Album WHERE id = {id};"
    return jsonify({
        'status': 'success',
        'sql': sql_log
    })

# --- CRUD MUSICA ---

@app.route('/api/musicas', methods=['GET'])
def get_musicas():
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT Musica.*, Artista.nome AS artista_nome, Album.titulo AS album_titulo FROM Musica JOIN Artista ON Musica.id_artista = Artista.id LEFT JOIN Album ON Musica.id_album = Album.id;
    musicas = db.session.query(Musica, Artista.nome, Album.titulo).join(Artista, Musica.id_artista == Artista.id).outerjoin(Album, Musica.id_album == Album.id).all()
    
    data = []
    for mus, art_nome, alb_titulo in musicas:
        d = mus.to_dict()
        d['artista_nome'] = art_nome
        d['album_titulo'] = alb_titulo or 'Sem Álbum'
        data.append(d)
        
    sql_log = "SELECT Musica.*, Artista.nome AS artista_nome, Album.titulo AS album_titulo FROM Musica JOIN Artista ON Musica.id_artista = Artista.id LEFT JOIN Album ON Musica.id_album = Album.id;"
    return jsonify({
        'data': data,
        'sql': sql_log
    })

@app.route('/api/musicas', methods=['POST'])
def create_musica():
    data = request.json
    titulo = data.get('titulo')
    duracao = int(data.get('duracao', 0) or 0)
    reproducoes = int(data.get('reproducoes', 0) or 0)
    letra = data.get('letra')
    genero = data.get('genero')
    ano = int(data.get('ano', datetime.datetime.now().year))
    id_album = data.get('id_album')
    id_artista = data.get('id_artista')
    
    if not titulo or not id_artista:
        return jsonify({'error': 'Titulo e Artista são obrigatórios'}), 400
        
    # Convert id_album to None if it is empty string or empty value
    if id_album == '' or id_album == 'None':
        id_album = None
        
    # COMENTÁRIO SQL ABSTRAÍDO:
    # INSERT INTO Musica (titulo, duracao, reproducoes, letra, genero, ano, id_album, id_artista) VALUES (:titulo, :duracao, :reproducoes, :letra, :genero, :ano, :id_album, :id_artista);
    musica = Musica(titulo=titulo, duracao=duracao, reproducoes=reproducoes, letra=letra, genero=genero, ano=ano, id_album=id_album, id_artista=id_artista)
    db.session.add(musica)
    db.session.commit()
    
    album_val = id_album if id_album is not None else 'NULL'
    sql_log = f"INSERT INTO Musica (titulo, duracao, reproducoes, letra, genero, ano, id_album, id_artista) VALUES ('{titulo}', {duracao}, {reproducoes}, '{letra or ''}', '{genero or ''}', {ano}, {album_val}, {id_artista});"
    return jsonify({
        'data': musica.to_dict(),
        'sql': sql_log
    })

@app.route('/api/musicas/<int:id>', methods=['PUT'])
def update_musica(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Musica WHERE id = :id;
    musica = Musica.query.get_or_404(id)
    
    data = request.json
    titulo = data.get('titulo')
    duracao = int(data.get('duracao', 0) or 0)
    reproducoes = int(data.get('reproducoes', 0) or 0)
    letra = data.get('letra')
    genero = data.get('genero')
    ano = int(data.get('ano', datetime.datetime.now().year))
    id_album = data.get('id_album')
    id_artista = data.get('id_artista')
    
    if not titulo or not id_artista:
        return jsonify({'error': 'Titulo e Artista são obrigatórios'}), 400
        
    if id_album == '' or id_album == 'None':
        id_album = None
        
    musica.titulo = titulo
    musica.duracao = duracao
    musica.reproducoes = reproducoes
    musica.letra = letra
    musica.genero = genero
    musica.ano = ano
    musica.id_album = id_album
    musica.id_artista = id_artista
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # UPDATE Musica SET titulo = :titulo, duracao = :duracao, reproducoes = :reproducoes, letra = :letra, genero = :genero, ano = :ano, id_album = :id_album, id_artista = :id_artista WHERE id = :id;
    db.session.commit()
    
    album_val = id_album if id_album is not None else 'NULL'
    sql_log = f"UPDATE Musica SET titulo = '{titulo}', duracao = {duracao}, reproducoes = {reproducoes}, letra = '{letra or ''}', genero = '{genero or ''}', ano = {ano}, id_album = {album_val}, id_artista = {id_artista} WHERE id = {id};"
    return jsonify({
        'data': musica.to_dict(),
        'sql': sql_log
    })

@app.route('/api/musicas/<int:id>', methods=['DELETE'])
def delete_musica(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Musica WHERE id = :id;
    musica = Musica.query.get_or_404(id)
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # DELETE FROM Musica WHERE id = :id;
    db.session.delete(musica)
    db.session.commit()
    
    sql_log = f"DELETE FROM Musica WHERE id = {id};"
    return jsonify({
        'status': 'success',
        'sql': sql_log
    })

# --- CRUD USUARIO ---

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT Usuario.*, Pagamento.status AS pagamento_status, Plano.tipo AS plano_tipo FROM Usuario LEFT JOIN Pagamento ON Usuario.id_pagamento = Pagamento.id LEFT JOIN Plano ON Pagamento.id_plano = Plano.id;
    usuarios = db.session.query(Usuario, Pagamento.status, Plano.tipo).outerjoin(Pagamento, Usuario.id_pagamento == Pagamento.id).outerjoin(Plano, Pagamento.id_plano == Plano.id).all()
    
    data = []
    for usr, pag_status, plano_tipo in usuarios:
        d = usr.to_dict()
        d['pagamento_status'] = pag_status or 'Nenhum'
        d['plano_tipo'] = plano_tipo or 'Nenhum'
        data.append(d)
        
    sql_log = "SELECT Usuario.*, Pagamento.status AS pagamento_status, Plano.tipo AS plano_tipo FROM Usuario LEFT JOIN Pagamento ON Usuario.id_pagamento = Pagamento.id LEFT JOIN Plano ON Pagamento.id_plano = Plano.id;"
    return jsonify({
        'data': data,
        'sql': sql_log
    })

@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    pais = data.get('pais')
    id_pagamento = data.get('id_pagamento')
    
    if not nome or not email:
        return jsonify({'error': 'Nome e Email são obrigatórios'}), 400
        
    if id_pagamento == '' or id_pagamento == 'None':
        id_pagamento = None
        
    data_nascimento = None
    if data.get('data_nascimento'):
        try:
            data_nascimento = datetime.datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').date()
        except ValueError:
            pass
            
    # COMENTÁRIO SQL ABSTRAÍDO:
    # INSERT INTO Usuario (nome, email, data_nascimento, pais, id_pagamento) VALUES (:nome, :email, :data_nascimento, :pais, :id_pagamento);
    usuario = Usuario(nome=nome, email=email, data_nascimento=data_nascimento, pais=pais, id_pagamento=id_pagamento)
    db.session.add(usuario)
    db.session.commit()
    
    pag_val = id_pagamento if id_pagamento is not None else 'NULL'
    nasc_val = f"'{data_nascimento.isoformat()}'" if data_nascimento else 'NULL'
    sql_log = f"INSERT INTO Usuario (nome, email, data_nascimento, pais, id_pagamento) VALUES ('{nome}', '{email}', {nasc_val}, '{pais or ''}', {pag_val});"
    
    return jsonify({
        'data': usuario.to_dict(),
        'sql': sql_log
    })

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Usuario WHERE id = :id;
    usuario = Usuario.query.get_or_404(id)
    
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    pais = data.get('pais')
    id_pagamento = data.get('id_pagamento')
    
    if not nome or not email:
        return jsonify({'error': 'Nome e Email são obrigatórios'}), 400
        
    if id_pagamento == '' or id_pagamento == 'None':
        id_pagamento = None
        
    data_nascimento = None
    if data.get('data_nascimento'):
        try:
            data_nascimento = datetime.datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').date()
        except ValueError:
            pass
            
    usuario.nome = nome
    usuario.email = email
    usuario.data_nascimento = data_nascimento
    usuario.pais = pais
    usuario.id_pagamento = id_pagamento
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # UPDATE Usuario SET nome = :nome, email = :email, data_nascimento = :data_nascimento, pais = :pais, id_pagamento = :id_pagamento WHERE id = :id;
    db.session.commit()
    
    pag_val = id_pagamento if id_pagamento is not None else 'NULL'
    nasc_val = f"'{data_nascimento.isoformat()}'" if data_nascimento else 'NULL'
    sql_log = f"UPDATE Usuario SET nome = '{nome}', email = '{email}', data_nascimento = {nasc_val}, pais = '{pais or ''}', id_pagamento = {pag_val} WHERE id = {id};"
    
    return jsonify({
        'data': usuario.to_dict(),
        'sql': sql_log
    })

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    # COMENTÁRIO SQL ABSTRAÍDO:
    # SELECT * FROM Usuario WHERE id = :id;
    usuario = Usuario.query.get_or_404(id)
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # DELETE FROM Usuario WHERE id = :id;
    db.session.delete(usuario)
    db.session.commit()
    
    sql_log = f"DELETE FROM Usuario WHERE id = {id};"
    return jsonify({
        'status': 'success',
        'sql': sql_log
    })

# --- DATABASE FEATURES DEMONSTRATION ---

@app.route('/api/musicas/<int:id>/reproduzir', methods=['POST'])
def reproduzir_musica(id):
    # This route simulates music reproduction.
    # It adds a record to Historico_Reproducao which triggers the MySQL trigger `atualiza_reproducoes`.
    # The trigger increments Musica.reproducoes. We then fetch the updated reproduction count.
    
    # COMENTÁRIO SQL ABSTRAÍDO:
    # INSERT INTO Historico_Reproducao (id_usuario, id_musica) VALUES (1, :id_musica);
    # -- GATILHO DISPARADO NO BANCO:
    # -- CREATE TRIGGER atualiza_reproducoes AFTER INSERT ON Historico_Reproducao FOR EACH ROW BEGIN UPDATE Musica SET reproducoes = reproducoes + 1 WHERE id = NEW.id_musica; END
    
    hist = HistoricoReproducao(id_usuario=1, id_musica=id)
    db.session.add(hist)
    db.session.commit()
    
    # Fetch updated music info to show reproduction count
    musica = Musica.query.get(id)
    
    sql_log = f"INSERT INTO Historico_Reproducao (id_usuario, id_musica) VALUES (1, {id}); -- [DISPAROU TRIGGER: atualiza_reproducoes]"
    return jsonify({
        'data': musica.to_dict(),
        'sql': sql_log
    })

@app.route('/api/top-musicas', methods=['GET'])
def get_top_musicas():
    # Queries the MySQL View TopMusicas
    # COMENTÁRIO SQL ABSTRAÍDO (Visão/View):
    # SELECT titulo, artista, reproducoes FROM TopMusicas;
    
    result = db.session.execute(text("SELECT titulo, artista, reproducoes FROM TopMusicas;"))
    data = [{'titulo': row[0], 'artista': row[1], 'reproducoes': row[2]} for row in result]
    
    sql_log = "SELECT titulo, artista, reproducoes FROM TopMusicas; -- [CONSULTA À VIEW]"
    return jsonify({
        'data': data,
        'sql': sql_log
    })

# Routes End ------------------------------- |

if __name__ == '__main__':
    with app.app_context():
        try:
            print("Conectando ao MySQL e rodando o script schema.sql...")
            init_db()
            print("Tabelas, triggers, visões e dados de sementes inicializados com sucesso!")
        except Exception as e:
            print(f"Erro ao inicializar banco: {e}")
            
    app.run(debug=True)