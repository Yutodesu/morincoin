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
    
    # Criação do Admin padrão se não existir
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (ADMIN_EMAIL,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin) VALUES (?, ?, 'admin', 1000000, 1)", (ADMIN_EMAIL, ADMIN_PASS))
        
        # Gera 2 códigos iniciais para testes
        cursor.execute("INSERT OR IGNORE INTO codigos (codigo) VALUES ('MRN-DW9O')")
        cursor.execute("INSERT OR IGNORE INTO codigos (codigo) VALUES ('MRN-J3SD')")
        
    conn.commit()
    conn.close()

init_db()

# === INTERFACES HTML (DESIGN DO SITE) ===
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MorinCoin Network</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { background-color: #161b22; padding: 30px; border-radius: 12px; border: 1px solid #30363d; width: 100%; max-width: 450px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); text-align: center; }
        h1 { color: #ffd700; margin-bottom: 5px; font-size: 28px; }
        .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 25px; }
        .balance-box { background: linear-gradient(135deg, #1f242c, #2d333b); padding: 20px; border-radius: 8px; border: 1px solid #ffd700; margin-bottom: 25px; }
        .balance-label { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
        .balance-value { font-size: 32px; font-weight: bold; color: #ffffff; margin-top: 5px; }
        .balance-value span { color: #ffd700; font-size: 20px; }
        input, button, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #30363d; background-color: #0d1117; color: #c9d1d9; box-sizing: border-box; font-size: 14px; }
        input:focus, select:focus { border-color: #ffd700; outline: none; }
        button { background-color: #ffd700; color: #0d1117; font-weight: bold; border: none; cursor: pointer; transition: 0.2s; }
        button:hover { background-color: #e6c200; }
        .btn-secondary { background-color: transparent; border: 1px solid #30363d; color: #8b949e; margin-top: 5px; }
        .btn-secondary:hover { background-color: #21262d; color: #ffffff; border-color: #8b949e; }
        .btn-admin { background-color: #238636; color: white; border: none; }
        .btn-admin:hover { background-color: #2ea043; }
        .history { margin-top: 30px; width: 100%; max-width: 450px; text-align: left; }
        .history h3 { color: #ffd700; border-bottom: 1px solid #30363d; padding-bottom: 5px; font-size: 16px; }
        .tx-item { background-color: #161b22; padding: 12px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #21262d; font-size: 13px; display: flex; justify-content: space-between; }
        .tx-meta { color: #8b949e; font-size: 11px; margin-top: 3px; }
        .tx-amount { font-weight: bold; color: #58a6ff; }
        .tx-amount.negative { color: #f85149; }
        .admin-section { background-color: #1f242c; border: 1px dashed #238636; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left; }
        .admin-section h4 { color: #2ea043; margin: 0 0 10px 0; }
        .code-display { background-color: #0d1117; padding: 10px; border-radius: 4px; font-family: monospace; color: #58a6ff; font-size: 16px; text-align: center; border: 1px solid #30363d; margin-top: 5px; }
    </style>
</head>
<body>

    <div class="container">
        <h1>MorinCoin</h1>
        <div class="subtitle">Rede Experimental de Ativos Simulado</div>
        
        <div class="balance-box">
            <div class="balance-label">Seu Saldo Disponível</div>
            <div class="balance-value">{{ saldo }} <span>MRN</span></div>
            <div style="font-size: 12px; color: #8b949e; margin-top: 5px;">@{{ username }}</div>
        </div>

        <form action="/transferir" method="POST">
            <h3 style="color: #ffffff; font-size: 16px; margin-bottom: 5px; text-align: left;">Efetuar Transferência</h3>
            <select name="destinatario" required>
                <option value="" disabled selected>Escolha o destinatário...</option>
                {% for user in usuarios %}
                    <option value="{{ user }}">{{ user }}</option>
                {% endfor %}
            </select>
            <input type="number" name="valor" placeholder="Quantidade de MRN" min="1" required>
            <button type="submit">Confirmar Envio</button>
        </form>

        {% if is_admin %}
        <div class="admin-section">
            <h4>Painel do Desenvolvedor</h4>
            <p style="font-size: 12px; color: #8b949e; margin: 0 0 10px 0;">Gere chaves exclusivas de 7 dígitos para novos registros de testadores na rede.</p>
            <form action="/gerar-codigo" method="POST" style="margin: 0;">
                <button type="submit" class="btn-admin">Gerar Novo Código de Convite</button>
            </form>
            {% if codigo_gerado %}
                <div class="code-display">{{ codigo_gerado }}</div>
            {% endif %}
        </div>
        {% endif %}

        <form action="/logout" method="GET" style="margin: 0;">
            <button type="submit" class="btn-secondary">Sair da Conta</button>
        </form>
    </div>

    <div class="history">
        <h3>📜 Histórico Geral da Rede (Blockchain)</h3>
        {% if transacoes %}
            {% for tx in transacoes %}
                <div class="tx-item">
                    <div>
                        <div>🔹 <strong>{{ tx[0] }}</strong> ➡️ <strong>{{ tx[1] }}</strong></div>
                        <div class="tx-meta">{{ tx[3] }}</div>
                    </div>
                    <div class="tx-amount">{{ tx[2] }} MRN</div>
                </div>
            {% endfor %}
        {% else %}
            <p style="color: #8b949e; font-size: 13px; text-align: center;">Nenhuma transação efetuada na rede até o momento.</p>
        {% endif %}
    </div>

</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - MorinCoin</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; box-sizing: border-box; }
        .container { background-color: #161b22; padding: 35px; border-radius: 12px; border: 1px solid #30363d; width: 100%; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        h2 { color: #ffd700; margin-bottom: 5px; text-align: center; }
        p { color: #8b949e; text-align: center; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #30363d; background-color: #0d1117; color: #c9d1d9; box-sizing: border-box; }
        input:focus { border-color: #ffd700; outline: none; }
        button { width: 100%; padding: 12px; margin-top: 15px; background-color: #ffd700; color: #0d1117; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 15px; }
        button:hover { background-color: #e6c200; }
        .footer-links { text-align: center; margin-top: 20px; font-size: 13px; color: #8b949e; }
        .footer-links a { color: #58a6ff; text-decoration: none; }
        .footer-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Acessar Rede</h2>
        <p>Insira seus dados para entrar no painel MorinCoin</p>
        <form action="/login" method="POST">
            <input type="email" name="email" placeholder="Endereço de E-mail" required>
            <input type="password" name="password" placeholder="Sua Senha" required>
            <button type="submit">Entrar na Conta</button>
        </form>
        <div class="footer-links">
            Não possui acesso? <a href="/register">Registrar com código</a>
        </div>
    </div>
</body>
</html>
'''

REGISTER_HTML = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro - MorinCoin</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; box-sizing: border-box; }
        .container { background-color: #161b22; padding: 35px; border-radius: 12px; border: 1px solid #30363d; width: 100%; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        h2 { color: #ffd700; margin-bottom: 5px; text-align: center; }
        p { color: #8b949e; text-align: center; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #30363d; background-color: #0d1117; color: #c9d1d9; box-sizing: border-box; }
        input:focus { border-color: #ffd700; outline: none; }
        button { width: 100%; padding: 12px; margin-top: 15px; background-color: #238636; color: white; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; font-size: 15px; }
        button:hover { background-color: #2ea043; }
        .footer-links { text-align: center; margin-top: 20px; font-size: 13px; color: #8b949e; }
        .footer-links a { color: #58a6ff; text-decoration: none; }
        .footer-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Criar Conta</h2>
        <p>Insira uma chave válida para se registrar na rede</p>
        <form action="/register" method="POST">
            <input type="text" name="codigo" placeholder="Código de Convite (Ex: MRN-XXXX)" required>
            <input type="text" name="username" placeholder="Nome de Usuário (Sem @)" required>
            <input type="email" name="email" placeholder="E-mail (Pode ser fictício)" required>
            <input type="password" name="senha" placeholder="Crie uma Senha" required>
            <button type="submit">Finalizar Registro</button>
        </form>
        <div class="footer-links">
            Já possui cadastro? <a href="/login">Fazer Login</a>
        </div>
    </div>
</body>
</html>
'''

# === ROTAS DO SISTEMA DA REDE ===

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Puxa informações do usuário logado
    cursor.execute("SELECT username, saldo, is_admin FROM usuarios WHERE id = ?", (session['user_id'],))
    user_data = cursor.fetchone()
    
    # Lista todos os usuários cadastrados (menos o admin e ele mesmo) para o select de envio
    cursor.execute("SELECT username FROM usuarios WHERE id != ? AND username != 'admin'", (session['user_id'],))
    usuarios_lista = [row[0] for row in cursor.fetchall()]
    
    # Histórico de transações gerais (Blockchain)
    cursor.execute("SELECT remetente, destinatario, valor, data FROM transacoes ORDER BY id DESC")
    transacoes_lista = cursor.fetchall()
    
    # Verifica se há o último código gerado na sessão para mostrar na tela do admin
    codigo_gerado = session.pop('ultimo_codigo', None)
    
    conn.close()
    
    return render_template_string(
        INDEX_HTML, 
        username=user_data[0], 
        saldo=user_data[1], 
        is_admin=user_data[2], 
        usuarios=usuarios_lista,
        transacoes=transacoes_lista,
        codigo_gerado=codigo_gerado
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, senha FROM usuarios WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user[1] == password:
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return "Dados de login incorretos! Verifique seu e-mail e senha.", 400
            
    return LOGIN_HTML

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').lower().strip()
        email = request.form.get('email').strip()
        senha = request.form.get('senha')
        codigo = request.form.get('codigo').strip()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Validação se o código existe e não foi usado
        cursor.execute("SELECT * FROM codigos WHERE codigo = ? AND usado = 0", (codigo,))
        cod_valido = cursor.fetchone()
        
        if not cod_valido:
            conn.close()
            return "Código Inválido ou já utilizado por outra pessoa!", 400
            
        try:
            # Insere usuário com saldo inicial fixo de 50 MorinCoins
            cursor.execute("INSERT INTO usuarios (email, senha, username, saldo) VALUES (?, ?, ?, 50)", (email, senha, username))
            cursor.execute("UPDATE codigos SET usado = 1 WHERE codigo = ?", (codigo,))
            
            # CIRÚRGICO: Dispara o arquivo de texto direto para a nuvem estável do Telegram
            enviar_txt_telegram(username, email)
            
            conn.commit()
            conn.close()
            return "Conta criada com sucesso! Acesse a página inicial e faça login."
        except sqlite3.IntegrityError:
            conn.close()
            return "Erro: Usuário ou E-mail já cadastrados na rede!", 400
            
    return REGISTER_HTML

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/transferir', methods=['POST'])
def transferir():
    if 'user_id' not in session:
        return "Não autorizado", 403
        
    destinatario_username = request.form.get('destinatario')
    valor = int(request.form.get('valor'))
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Dados do remetente
    cursor.execute("SELECT id, email, senha, username, saldo FROM usuarios WHERE id = ?", (session['user_id'],))
    remetente = cursor.fetchone()
    
    # Dados do destinatário
    cursor.execute("SELECT id, saldo FROM usuarios WHERE username = ?", (destinatario_username,))
    destinatario = cursor.fetchone()
    
    if not destinatario:
        conn.close()
        return "Erro: Destinatário não localizado na rede!", 404
        
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
        # Gera o código de 7 dígitos no formato exato esperado pela interface: MRN-XXXX
        novo_cod = "MRN-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        cursor.execute("INSERT INTO codigos (codigo) VALUES (?)", (novo_cod,))
        conn.commit()
        session['ultimo_codigo'] = novo_cod
        
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
