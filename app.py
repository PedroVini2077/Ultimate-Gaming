from flask import Flask, request, render_template, redirect
import re, bcrypt, sqlite3

app = Flask(__name__)

conexao = sqlite3.connect('users.db')
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL,
    data_nascimento TEXT NOT NULL,
    senha TEXT NOT NULL
)
""")

conexao.commit()
conexao.close()

@app.route('/logout')
def logout():
    return redirect('/?logout=1')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/')
def home():
    logout_msg = request.args.get('logout')
    return render_template('index.html', logout_msg=logout_msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        erros = {}
        if not email:
            erros['email'] = 'Email é obrigatório.'
        elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
            erros['email'] = 'Email inválido.'
        if not senha:
            erros['senha'] = 'Senha é obrigatória.'
        elif len(senha) < 6 or len(senha) > 20:
            erros['senha'] = 'Senha deve ter entre 6 e 20 caracteres.'
        if erros:
            return render_template('login.html', erros=erros, email=email)
        
        conexao = sqlite3.connect('users.db')
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conexao.close()
            
        if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
            return render_template('login.html', sucesso=True, nome=usuario['nome'], erros={})
            
        erros['geral'] = 'Email ou senha incorretos.'
        return render_template('login.html', erros=erros, email=email)

    return render_template('login.html', erros={}, email='')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            data_nascimento = request.form['data_nascimento']
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']
            
            dados_usuario = {
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'data_nascimento': data_nascimento,
                'senha': senha,
                'confirmar_senha': confirmar_senha
            }
            
            erros = {}
        
            if not nome:
                erros['nome'] = 'Nome é obrigatório.'
            elif not re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome):
                erros['nome'] = 'Nome deve conter apenas letras e espaços.'
            if not email:
                erros['email'] = 'Email é obrigatório.'
            elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
                erros['email'] = 'Email inválido.'
            if not telefone:
                erros['telefone'] = 'Telefone é obrigatório.'
            elif not telefone.isdigit() or len(telefone) < 11:
                erros['telefone'] = 'Telefone deve conter apenas números e ter pelo menos 11 dígitos.'
            if not data_nascimento:
                erros['data_nascimento'] = 'Data de nascimento é obrigatória.'
            if not senha:
                erros['senha'] = 'Senha é obrigatória.'
            elif len(senha) < 6 or len(senha) > 20:
                erros['senha'] = 'Senha deve ter entre 6 e 20 caracteres.'
            if senha != confirmar_senha:
                erros['confirmar_senha'] = 'As senhas não coincidem.'
            if erros:
                return render_template('cadastro.html', erros=erros, **dados_usuario)
            
            conexao = sqlite3.connect('users.db')
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            usuario_existente = cursor.fetchone()
            
            if usuario_existente:
                conexao.close()
                return render_template(
                    'cadastro.html',
                    email_duplicado=True,
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    data_nascimento=data_nascimento,
                    senha=senha,
                    confirmar_senha=confirmar_senha,
                    erros={}
                )
                
            novo_usuario = {
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'data_nascimento': data_nascimento,
                'senha': bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            }
            
            conexao = sqlite3.connect('users.db')
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO users (nome, email, telefone, data_nascimento, senha)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, email, telefone, data_nascimento, novo_usuario['senha']))
            conexao.commit()
            conexao.close()
                
            return render_template('cadastro.html', sucesso=True, erros={})
        
    return render_template(
        'cadastro.html',
        erros={},
        nome='',
        email='',
        telefone='',
        data_nascimento='',
        senha='',
        confirmar_senha='',
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)