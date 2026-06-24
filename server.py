from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import psycopg2
import random
import string
import os
import io
import requests

app = Flask(__name__)

# === CONFIGURAÇÃO DE SEGURANÇA ===
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'chave_ultra_secreta_da_morincoin')

# Link do PostgreSQL que você gerou na Render
DATABASE_URL = "postgresql://admin:SdveynYtqSio6nHp7r2ItKVtD5iD7K8V@dpg-d8s7fd7avr4c73fdo9o0-a/morincoin"

# Configuração Segura do Bot do Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Credenciais do Admin protegidas
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@morin.com')
ADMIN_PASS = os.environ.get('ADMIN_PASSWORD', 'admin123')

def get_db_connection():
    """Cria uma conexão com o banco de dados PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

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
    """Cria as tabelas no PostgreSQL se elas não existirem"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            remetente TEXT,
            destinatario TEXT,
            valor INTEGER,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar conta do Administrador padrão se não existir
    try:
        cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin) VALUES (%s, %s, 'admin', 10000, 1)", (ADMIN_EMAIL, ADMIN_PASS))
    except psycopg2.IntegrityError:
        conn.rollback()

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
            cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin) VALUES (%s, %s, %s, %s, 0)", (email, senha, username, saldo_sorteado))
        except psycopg2.IntegrityError:
            conn.rollback()
        
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# --- TEMPLATES HTML (INTERFACES 100% INTACTAS COM CHAVINHA INCLUÍDA) ---
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
        
        /* --- ESTILOS DA CHAVINHA (TOGGLE SWITCH) --- */
        .email-header { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
        .email-header label { font-size: 14px; color: #9ca3af; }
        
        .switch { position: relative; display: inline-block; width: 44px; height: 24px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #374151; transition: .3s; border-radius: 24px; }
        .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
        input:checked + .slider { background-color: #34d399; }
        input:checked + .slider:before { transform: translateX(20px); }
        
        /* --- CAMPO DE EMAIL INTEGRADO --- */
        .email-container { display: flex; align-items: center; background: #1f2937; border: 1px solid #374151; border-radius: 6px; margin: 10px 0; padding-right: 10px; }
        .email-container input { margin: 0; border: none; background: transparent; flex: 1; }
        .email-suffix { color: #6b7280; font-family: monospace; font-size: 14px; user-select: none; padding-left: 5px; }
        
        /* --- TEXTO INFORMATIVO CLICÁVEL --- */
        .info-link { font-size: 12px; color: #6b7280; text-decoration: underline; cursor: pointer; display: inline-block; margin-bottom: 10px; }
        .info-link:hover { color: #9ca3af; }
        
        /* --- POPUP / MODAL DE EXPLICAÇÃO --- */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 12px; max-width: 300px; text-align: center; }
        .modal-content p { font-size: 14px; color: #d1d5db; line-height: 1.5; }
        .modal-btn { background: #34d399; color: #000; font-weight: bold; border: 0; padding: 8px 16px; border-radius: 6px; margin-top: 15px; cursor: pointer; width: auto; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="text-align:center; color:#34d399;">🔑 Criar Conta MRN</h2>
        <form method="POST" action="/register" id="regForm">
            <input type="text" name="username" id="usernameField" placeholder="Nome de Usuário (Ex: yuto)" required oninput="atualizarEmailAnonimo()">
            
            <div class="email-header">
                <label id="switchLabel">Modo: Anónimo 🥷</label>
                <label class="switch">
                    <input type="checkbox" id="emailToggle" onchange="alternarModoEmail()">
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="email-container">
                <input type="text" name="email" id="emailField" placeholder="Utilizador" required>
                <span id="emailSuffix" class="email-suffix">@morincoin.com</span>
            </div>
            
            <span class="info-link" onclick="abrirAjuda()">O que é esta chave?</span>
            
            <input type="password" name="senha" placeholder="Sua Senha" required>
            <input type="text" name="codigo" placeholder="Código de 7 dígitos (Admin)" required>
            <button type="submit">Validar e Criar</button>
        </form>
        <a href="/">Voltar para o Login</a>
    </div>

    <div id="helpModal" class="modal">
        <div class="modal-content">
            <h3 style="color:#34d399; margin-top:0;">ℹ️ Sobre os modos de E-mail</h3>
            <p id="helpText">
                <strong>Chave Desativada (Anónimo):</strong> Cria uma conta segura usando apenas o seu nome de utilizador interno da rede. Não precisa de dados reais seus!<br><br>
                <strong>Chave Ativada (E-mail Real):</strong> Permite digitar um e-mail seu (como Gmail). Necessário para futura recuperação de conta por verificação.
            </p>
            <button class="modal-btn" onclick="fecharAjuda()">Entendi</button>
        </div>
    </div>

    <script>
        function atualizarEmailAnonimo() {
            const toggle = document.getElementById('emailToggle');
            const username = document.getElementById('usernameField').value.toLowerCase().replace(/[^a-z0-9]/g, '');
            const emailInput = document.getElementById('emailField');
            
            // Se estiver no modo anónimo, o campo de e-mail espelha o nome de utilizador automaticamente
            if (!toggle.checked) {
                emailInput.value = username;
            }
        }

        function alternarModoEmail() {
            const toggle = document.getElementById('emailToggle');
            const label = document.getElementById('switchLabel');
            const emailInput = document.getElementById('emailField');
            const suffix = document.getElementById('emailSuffix');
            
            if (toggle.checked) {
                // Modo E-mail Real Ativado
                label.innerText = "Modo: E-mail Real 📧";
                suffix.style.display = "none"; // Esconde o @morincoin.com
                emailInput.placeholder = "Ex: seuemail@gmail.com";
                emailInput.value = "";
                emailInput.readOnly = false;
            } else {
                // Modo Anónimo Ativado
                label.innerText = "Modo: Anónimo 🥷";
                suffix.style.display = "inline"; // Mostra o @morincoin.com
                emailInput.placeholder = "Utilizador";
                emailInput.readOnly = true; // Trava para não editarem o sufixo manualmente
                atualizarEmailAnonimo();
            }
        }

        // Interações do Modal de Ajuda
        function abrirAjuda() { document.getElementById('helpModal').style.display = 'flex'; }
        function fecharAjuda() { document.getElementById('helpModal').style.display = 'none'; }

        // Junta o sufixo no envio do formulário caso esteja em modo anónimo
        document.getElementById('regForm').addEventListener('submit', function(e) {
            const toggle = document.getElementById('emailToggle');
            const emailInput = document.getElementById('emailField');
            if (!toggle.checked && !emailInput.value.includes('@')) {
                emailInput.value = emailInput.value + "@morincoin.com";
            }
        });

        // Inicializa o estado correto na primeira carga da página
        alternarModoEmail();
    </script>
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
            <form action="/gerar-codigo" method="POST
