from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
import random
import string
import os
import io
import requests

app = Flask(__name__)

# === CONFIGURAÇÃO DE SEGURANÇA ===
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave_ultra_secreta_da_morincoin')
DB_FILE = 'morincoin.db'

# Configuração Segura do Bot do Telegram (Puxa do painel de Environment da Render)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Credenciais do Admin protegidas (puxa da Render ou usa padrão local)
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@morin.com')
ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'admin123')

def enviar_txt_telegram(username, email):
    """Gera o arquivo .txt e envia direto para o Telegram do Administrador"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        conteudo = f"=== NOVO CADASTRO DE TESTADOR ===\n\nUsuário: {username}\nE-mail Utilizado: {email}\n"
        arquivo_memoria = io.BytesIO(conteudo.encode('utf-8'))
        arquivo_memoria.name = f"{username}_cadastro.txt"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        dados = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"👤 Novo usuário na rede: @{username}"}
        arquivos = {'document': arquivo_memoria}
        
        requests.post(url, data=dados, files=arquivos)
        return True
    except Exception:
        return False

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            saldo INTEGER NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    # Tabela de Códigos de Convite (7 dígitos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codigos (
            codigo TEXT PRIMARY KEY,
            usado INTEGER DEFAULT 0
        )
    ''')
    # Tabela de Transações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remetente TEXT,
            destinatario TEXT,
            valor INTEGER,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar conta do Administrador padrão se não existir
    try:
        cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin) VALUES (?, ?, 'admin', 10000, 1)", (ADMIN_EMAIL, ADMIN_PASS))
    except sqlite3.IntegrityError:
        pass

    # === TESTADORES PROTEGIDOS E COM SALDOS ALEATÓRIOS ===
    logins_adicionais = [
        ('testador1@morin.com', os.environ.get('TESTADOR_1_PASS', 'mrn2026a'), 'testador1'),
        ('testador2@morin.com', os.environ.get('TESTADOR_2_PASS', 'mrn2026b'), 'testador2'),
        ('testador3@morin.com', os.environ.get('TESTADOR_3_PASS', 'mrn2026c'), 'testador3'),
        ('testador4@morin.com', os.environ.get('TESTADOR_4_PASS', 'mrn2026d'), 'testador4'),
        ('testador5@morin.com', os.environ.get('TESTADOR_5_PASS', 'mrn2026e'), 'testador5'),
        ('testador6@morin.com', os.environ.get('TESTADOR_6_PASS', 'mrn2026f'), 'testador6'),
        ('testador7@morin.com', os.environ.get('TESTADOR_7_PASS', 'mrn2026g'), 'testador7'),
        ('testador8@morin.com', os.environ.get('TESTADOR_8_PASS', 'mrn2026h'), 'testador8'),
        ('testador9@morin.com', os.environ.get('TESTADOR_9_PASS', 'mrn2026i'), 'testador9'),
        ('testador10@morin.com', os.environ.get('TESTADOR_10_PASS', 'mrn2026j'), 'testador10')
    ]
    
    saldos_possiveis = [150, 150, 150, 150, 500, 150, 150, 1000, 150, 150]
    
    for email, senha, username in logins_adicionais:
        try:
            saldo_sorteado = random.choice(saldos_possiveis)
            cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin) VALUES (?, ?, ?, ?, 0)", (email, senha, username, saldo_sorteado))
        except sqlite3.IntegrityError:
            pass
        
    conn.commit()
    conn.close()

init_db()

# --- TEMPLATES HTML (INTERFACES 100% INTACTAS) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MorinCoin - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0b0f19; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #111827; padding: 30px; border-radius: 12px; width: 90%; max-width: 360px; border: 1px solid #1f2937; }
        input, button { padding: 12px; margin: 10px 0; width: 100%; box-sizing: border-box; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; }
        button { background: #0284c7; border: 0; font-weight: bold; cursor: pointer; }
        a { color: #38bdf8; text-decoration: none; font-size: 14px; display: block; text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="text-align:center; color:#38bdf8;">🪙 MorinCoin Login</h2>
        <form method="POST" action="/login">
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar na Rede</button>
        </form>
        <a href="/register">Novo por aqui? Registrar com código</a>
    </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MorinCoin - Registro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0b0f19; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #111827; padding: 30px; border-radius: 12px; width: 90%; max-width: 360px; border: 1px solid #1f2937; }
        input, button { padding: 12px; margin: 10px 0; width: 100%; box-sizing: border-box; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; }
        button { background: #34d399; border: 0; color: #000; font-weight: bold; cursor: pointer; }
        a { color: #38bdf8; text-decoration: none; font-size: 14px; display: block; text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="text-align:center; color:#34d399;">🔑 Criar Conta MRN</h2>
        <form method="POST" action="/register">
            <input type="text" name="username" placeholder="Nome de Usuário (Ex: yuto)" required>
            <input type="email" name="email" placeholder="Seu E-mail" required>
            <input type="password" name="senha" placeholder="Sua Senha" required>
            <input type="text" name="codigo" placeholder="Código de 7 dígitos (Admin)" required>
            <button type="submit">Validar e Criar</button>
        </form>
        <a href="/">Voltar para o Login</a>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Rede MorinCoin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0b0f19; color: #f3f4f6; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .card { background: #111827; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #1f2937; }
        h1, h3 { color: #38bdf8; margin-top: 0; }
        input, select, button { padding: 12px; margin: 8px 0; width: 100%; box-sizing: border-box; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; }
        button { background: #0284c7; border: 0; font-weight: bold; cursor: pointer; }
        .nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .btn-logout { background: #ef4444; width: auto; padding: 8px 15px; margin: 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <span>Olá, <strong>{{ user[3] }}</strong> ({{ 'ADMIN' if user[5]==1 else 'USER' }})</span>
            <a href="/logout"><button class="btn-logout">Sair</button></a>
        </div>

        <h1>🪙 MorinCoin: {{ user[4] }} MRN</h1>

        {% if user[5] == 1 %}
        <div class="card" style="border-color: #eab308;">
            <h3 style="color: #eab308;">🛠️ Painel Mestre (Admin)</h3>
            <form action="/gerar-codigo" method="POST">
                <button type="submit" style="background: #eab308; color: #000;">Gerar Código de 7 Dígitos</button>
            </form>
            <h4>Códigos Ativos para Testadores:</h4>
            <ul>
                {% for c in codigos %}
                    <li><code>{{ c[0] }}</code> - {{ '❌ Usado' if c[1]==1 else '✅ Disponível' }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="card">
            <h3>💸 Enviar MorinCoins</h3>
            <form action="/transferir" method="POST">
                <label>Destinatário (Username):</label>
                <input type="text" name="destinatario" placeholder="Ex: amigo" required>
                <label>Quantidade:</label>
                <input type="number" name="valor" min="1" required>
                <button type="submit">Assinar e Enviar</button>
            </form>
        </div>

        <div class="card">
            <h3>📜 Histórico Geral da Rede (Blockchain)</h3>
            <ul>
                {% for t in transacoes %}
                    <li style="font-family: monospace; font-size:13px; margin-bottom: 5px;">
                        🔹 [<strong>{{ t[0] }}</strong> ➡️ <strong>{{ t[1] }}</strong>] enviou <strong>{{ t[2] }} MRN</strong> ({{ t[3] }})
                    </li>
                {% endfor %}
            </ul>
        </div>
    </div>
</body>
</html>
"""

# --- ROTAS DO FLASK ---

@app.route('/')
def index():
    if 'user_id' in session:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        
        cursor.execute("SELECT remetente, destinatario, valor, data FROM transacoes ORDER BY id DESC")
        transacoes = cursor.fetchall()
        
        codigos = []
        if user and user[5] == 1:
            cursor.execute("SELECT codigo, usado FROM codigos ORDER BY usado ASC")
            codigos = cursor.fetchall()
            
        conn.close()
        if user:
            return render_template_string(DASHBOARD_HTML, user=user, transacoes=transacoes, codigos=codigos)
    return LOGIN_HTML

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        return redirect(url_for('index'))
    return "Login Inválido! Verifique o e-mail e a senha.", 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower().strip()
        email = request.form.get('email').strip()
        senha = request.form.get('senha')
        codigo = request.form.get('codigo').strip()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM codigos WHERE codigo = ? AND usado = 0", (codigo,))
        cod_valido = cursor.fetchone()
        
        if not cod_valido:
            conn.close()
            return "Código Inválido ou já utilizado por outra pessoa!", 400
            
        try:
            cursor.execute("INSERT INTO usuarios (email, senha, username, saldo) VALUES (?, ?, ?, 50)", (email, senha, username))
            cursor.execute("UPDATE codigos SET usado = 1 WHERE codigo = ?", (codigo,))
            
            # DISPARE DO LOG PARA O BOT DO TELEGRAM
            enviar_txt_telegram(username, email)
            
            conn.commit()
            conn.close()
            return "Conta criada com sucesso! Acesse a página inicial e faça login."
        except sqlite3.IntegrityError:
            conn.close()
            return "Erro: Usuário ou E-mail já cadastrados na rede!", 400
            
    return REGISTER_HTML

@app.route('/transferir', methods=['POST'])
def transferir():
    if 'user_id' not in session:
        return "Não autorizado", 403
        
    destinatario_username = request.form.get('destinatario').lower().strip()
    valor = int(request.form.get('valor'))
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session['user_id'],))
    remetente = cursor.fetchone()
    
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (destinatario_username,))
    destinatario = cursor.fetchone()
    
    if not destinatario:
        conn.close()
        return "Erro: Usuário de destino não existe!", 404
        
    if remetente[3] == destinatario_username:
        conn.close()
        return "Erro: Você não pode transferir para si mesmo!", 400
        
    if remetente[4] < valor:
        conn.close()
        return "Erro: Saldo insuficiente de MorinCoins!", 400
        
    cursor.execute("UPDATE usuarios SET saldo = saldo - ? WHERE id = ?", (valor, remetente[0]))
    cursor.execute("UPDATE usuarios SET saldo = saldo + ? WHERE id = ?", (valor, destinatario[0]))
    cursor.execute("INSERT INTO transacoes (remetente, destinatario, valor) VALUES (?, ?, ?)", (remetente[3], destinatario_username, valor))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/gerar-codigo', methods=['POST'])
def gerar_codigo():
    if 'user_id' not in session:
        return "Não autorizado", 403
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_admin FROM usuarios WHERE id = ?", (session['user_id'],))
    if cursor.fetchone()[0] == 1:
        novo_cod = "MRN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        cursor.execute("INSERT INTO codigos (codigo) VALUES (?)", (novo_cod,))
        conn.commit()
        
    conn.close()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
