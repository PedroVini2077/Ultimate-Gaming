from flask import Flask, request, render_template, redirect
import os, json, re

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'users.json')

app = Flask(__name__)

@app.route('/cadastro_teste')
def cadastro_teste():
    return render_template('cadastro_teste.html')

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
        
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            erros['geral'] = 'Email ou senha incorretos.'
            return render_template('login.html', erros=erros, email=email)
            
        for user in users:
            if user['email'] == email and user['senha'] == senha:
                return render_template('login.html', sucesso=True, nome=user['nome'], erros={})
            
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
            
        
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    users = json.load(f)
                    if not isinstance(users, list):
                        users = []
                except json.JSONDecodeError:
                    users = []
                    
            for user in users:
                if user['email'] == email:
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
                'senha': senha
            }
            users.append(novo_usuario)
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
                
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