import shutil
from datetime import datetime 
from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'chave_ultra_secreta_da_morincoin'

DB_FILE = 'morincoin.db'
BACKUP_FILE = 'morincoin_backup.db'
TXT_LOGINS = 'testadores.txt'

def fazer_backup():
    try:
        shutil.copy(DB_FILE, BACKUP_FILE)
    except Exception as e:
        print(f"[ERRO] {e}")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            senha TEXT
        )
    ''')
    conn.commit()
    conn.close()

def gerar_token():
    letras = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"MC-{letras}"

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('painel'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']
        senha = request.form['senha']

        # 1. TENTA VALIDAR PRIMEIRO PELO ARQUIVO DE TEXTO
        if os.path.exists(TXT_LOGINS):
            try:
                with open(TXT_LOGINS, 'r') as f:
                    for linha in f:
                        if ':' in linha:
                            u, s = linha.strip().split(':', 1)
                            if login_input == u and senha == s:
                                session['user_id'] = 999  # ID mestre para testadores do TXT
                                return redirect(url_for('painel'))
            except Exception as e:
                print(f"[ERRO AO LER TXT] {e}")

        # 2. SE NÃO ACHAR NO TXT, BUSCA NO BANCO DE DADOS AUTOMATICAMENTE
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, senha FROM usuarios WHERE email = ? OR username = ?", (login_input, login_input))
        user = cursor.fetchone()
        conn.close()

        if user and user[1] == senha:
            session['user_id'] = user[0]
            return redirect(url_for('painel'))
        else:
            return "Credenciais inválidas! Volte e tente novamente."

    template_login = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - MorinCoin</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 100px; background-color: #f4f4f9; color: #333; }
            .container { display: inline-block; padding: 30px; background: white; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            input { display: block; width: 200px; margin: 10px auto; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>MorinCoin - Admin Login</h2>
            <form method="POST">
                <input type="text" name="login_input" placeholder="Usuário ou E-mail" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button type="submit">Entrar</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(template_login)

@app.route('/painel', methods=['GET', 'POST'])
def painel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    token_gerado = None
    if request.method == 'POST' and 'gerar' in request.form:
        token_gerado = gerar_token()

    template_painel = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Painel Admin - MorinCoin</title>
        <style>
            body { font-family: sans-serif; background-color: #eef2f3; margin: 0; padding: 20px; }
            .nav { background: #333; color: white; padding: 15px; text-align: space-between; border-radius: 5px; }
            .nav a { color: #ff4d4d; float: right; text-decoration: none; font-weight: bold; }
            .main { margin-top: 30px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
            .btn { padding: 12px 25px; background: #28a745; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            .btn:hover { background: #218838; }
            .token-box { margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeeba; color: #856404; font-size: 22px; font-family: monospace; font-weight: bold; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="nav">
            <span style="font-size: 18px; font-weight: bold;">🪙 MorinCoin - Gerenciador do Sistema</span>
            <a href="/logout">Sair</a>
        </div>
        <div class="main">
            <h1>Painel do Administrador</h1>
            <p>Clique no botão abaixo para gerar um novo código de acesso para os usuários.</p>
            
            <form method="POST">
                <button type="submit" name="gerar" class="btn">⚡ Gerar Código de Acesso</button>
            </form>

            {% if token_gerado %}
                <div style="margin-top: 25px;">
                    <p><strong>Código de Acesso Gerado com Sucesso:</strong></p>
                    <div class="token-box">{{ token_gerado }}</div>
                    <p style="font-size: 12px; color: #666;">Copie esse código e use no site principal.</p>
                </div>
            {% endif %}
        </div>
    </body>
    </html>
    """
    return render_template_string(template_painel, token_gerado=token_gerado)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    fazer_backup()
    app.run(host='0.0.0.0', port=5000)
