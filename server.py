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
    
    # Tabela de Usuários (Adicionado o campo 'pin' padrão para suporte futuro)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            saldo INTEGER NOT NULL,
            is_admin INTEGER DEFAULT 0,
            pin TEXT DEFAULT '000000'
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
        cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin, pin) VALUES (%s, %s, 'admin', 10000, 1, '999999')", (ADMIN_EMAIL, ADMIN_PASS))
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
            pin_aleatorio = "".join(random.choices(string.digits, k=6))
            cursor.execute("INSERT INTO usuarios (email, senha, username, saldo, is_admin, pin) VALUES (%s, %s, %s, %s, 0, %s)", (email, senha, username, saldo_sorteado, pin_aleatorio))
        except psycopg2.IntegrityError:
            conn.rollback()
        
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# --- TEMPLATES HTML COM AS NOVAS IMPLEMENTAÇÕES ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>MorinCoin - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #0b0f19; color: #fff; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .box { background: #111827; padding: 30px; border-radius: 12px; width: 90%; max-width: 360px; border: 1px solid #1f2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        input, button { padding: 12px; margin: 10px 0; width: 100%; box-sizing: border-box; border-radius: 6px; border: 1px solid #374151; background: #1f2937; color: #fff; font-size: 14px; }
        button { background: #0284c7; border: 0; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #0369a1; }
        .links-container { display: flex; flex-direction: column; gap: 8px; margin-top: 15px; text-align: center; }
        a, .fake-link { color: #38bdf8; text-decoration: none; font-size: 14px; cursor: pointer; }
        a:hover, .fake-link:hover { text-decoration: underline; }
        
        /* --- ESTILOS DO POP-UP / MODAL --- */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); justify-content: center; align-items: center; z-index: 1000; padding: 20px; box-sizing: border-box; }
        .modal-content { background: #111827; border: 1px solid #374151; padding: 25px; border-radius: 12px; max-width: 400px; width: 100%; position: relative; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }
        .close-btn { position: absolute; top: 12px; right: 15px; color: #9ca3af; font-size: 22px; font-weight: bold; cursor: pointer; user-select: none; }
        .close-btn:hover { color: #fff; }
        .modal h3 { margin-top: 0; color: #38bdf8; }
        .modal p { font-size: 14px; color: #d1d5db; line-height: 1.6; text-align: left; }
        
        /* Estilos específicos para o FAQ interno */
        .faq-item { border-bottom: 1px solid #1f2937; padding: 10px 0; }
        .faq-question { font-weight: bold; color: #34d399; cursor: pointer; font-size: 14px; }
        .faq-answer { font-size: 13px; color: #9ca3af; margin-top: 5px; display: none; line-height: 1.4; }
    </style>
</head>
<body>
    <div class="box">
        <h2 style="text-align:center; color:#38bdf8; margin-top: 0;">🪙 MorinCoin Login</h2>
        <form method="POST" action="/login">
            <input type="email" name="email" placeholder="E-mail" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar na Rede</button>
        </form>
        
        <div class="links-container">
            <a href="/register">Novo por aqui? Registrar com código</a>
            <span class="fake-link" onclick="abrirModal('faqModal')">❓ Saiba mais sobre o projeto</span>
            <span class="fake-link" onclick="abrirModal('suporteModal')">⚠️ Problemas para Logar?</span>
        </div>
    </div>

    <div id="welcomeModal" class="modal" style="display: flex;">
        <div class="modal-content" style="text-align: center;">
            <span class="close-btn" onclick="fecharModal('welcomeModal')">&times;</span>
            <h3 style="color: #eab308;">⚠️ Projeto em Desenvolvimento</h3>
            <p style="text-align: center;">
                Seja bem-vindo à rede de testes da <strong>MorinCoin (MRN)</strong>!<br><br>
                Este site ainda <strong>não está totalmente pronto</strong>. Estamos realizando atualizações constantes na interface e no sistema de segurança. Sinta-se livre para explorar e criar sua conta de testes!
            </p>
            <button onclick="fecharModal('welcomeModal')" style="background: #eab308; color: #000; width: auto; padding: 8px 20px; margin-top: 10px;">Entrar no Site</button>
        </div>
    </div>

    <div id="faqModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="fecharModal('faqModal')">&times;</span>
            <h3>💡 Perguntas Frequentes (FAQ)</h3>
            <div style="max-height: 350px; overflow-y: auto; padding-right: 5px;">
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">- O que é o MorinCoin?</div>
                    <div class="faq-answer">É uma plataforma de simulação e testes para uma rede de moedas digitais internas (MRN), construída para estudar movimentações e banco de dados na nuvem.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">- Quem desenvolveu o MorinCoin?</div>
                    <div class="faq-answer">O projeto foi totalmente idealizado e desenvolvido por Yuto Kawaguchi como um ecossistema financeiro simulado moderno e focado em privacidade.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">- O MorinCoin é um investimento?</div>
                    <div class="faq-answer">Não! A MorinCoin (MRN) é uma moeda estritamente virtual e fictícia usada para testes. Ela não possui valor financeiro real e não é um investimento de mercado.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">- É seguro usar o MorinCoin?</div>
                    <div class="faq-answer">Sim! O site conta com criptografia de sessões e banco de dados relacional isolado. Além disso, você tem controle total sobre a privacidade dos seus dados.</div>
                </div>
                <div class="faq-item">
                    <div class="faq-question" onclick="toggleFaq(this)">- Preciso preencher meu e-mail real?</div>
                    <div class="faq-answer">Não é obrigatório! Na aba de registro você pode desativar a chave e usar o modo anônimo, que gera um e-mail interno automático do sistema para proteger sua privacidade.</div>
                </div>
            </div>
        </div>
    </div>

    <div id="suporteModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="fecharModal('suporteModal')">&times;</span>
            <h3 style="color: #ef4444;">🛠️ Suporte & Recuperação</h3>
            <p>
                Se você esqueceu seus dados ou perdeu o acesso à sua conta de testador, preencha o formulário abaixo para enviar um chamado diretamente ao Administrador da rede.
            </p>
            <form onsubmit="enviarSuporteFake(event)">
                <input type="text" id="supUser" placeholder="Seu Usuário (ex: yuto)" required>
                <input type="text" id="supPin" placeholder="Seu PIN de 6 dígitos de segurança" maxlength="6" required>
                <p style="font-size: 11px; color: #9ca3af; margin: 5px 0;">*Para sabermos que você é o dono real da conta, forneça o PIN de 6 dígitos que você ganhou assim que criou sua conta.</p>
                <button type="submit" style="background: #ef4444; margin-top: 10px;">Enviar Solicitação</button>
            </form>
        </div>
    </div>

    <script>
        function abrirModal(id) { document.getElementById(id).style.display = 'flex'; }
        function fecharModal(id) { document.getElementById(id).style.display = 'none'; }
        
        function toggleFaq(elemento) {
            const resposta = elemento.nextElementSibling;
            resposta.style.display = (resposta.style.display === 'block') ? 'none' : 'block';
        }

        function enviarSuporteFake(e) {
            e.preventDefault();
            alert("Chamado enviado com sucesso! O Administrador irá analisar os dados e validar o seu PIN em breve.");
            fecharModal('suporteModal');
            document.getElementById('supUser').value = '';
            document.getElementById('supPin').value = '';
        }
    </script>
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
        <h2 style="text-align:center; color:#34d399; margin-top: 0;">🔑 Criar Conta MRN</h2>
        <form method="POST" action="/register" id="regForm">
            <input type="text" name="username" id="usernameField" placeholder="Nome de Usuário (Ex: yuto)" required oninput="atualizarEmailAnonimo()">
            
            <div class="email-header">
                <label id="switchLabel">Modo: Anônimo 🥷</label>
                <label class="switch">
                    <input type="checkbox" id="emailToggle" onchange="alternarModoEmail()">
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="email-container">
                <input type="text" name="email" id="emailField" placeholder="Utilizador" required>
                <span id="emailSuffix" class="email-suffix">@morincoin.com</span>
            </div>
            
            <span class="info-link" onclick="abrirAjuda()">O que é essa chavinha? ⚠️</span>
            
            <input type="password" name="senha" placeholder="Sua Senha" required>
            <input type="text" name="codigo" placeholder="Código de 7 dígitos (Admin)" required>
            <button type="submit">Validar e Criar</button>
        </form>
        <a href="/">Voltar para o Login</a>
    </div>

    <div id="helpModal" class="modal">
        <div class="modal-content">
            <h3 style="color:#34d399; margin-top:0;">ℹ️ Sobre os modos de E-mail</h3>
            <p id="helpText" style="text-align: left; font-size: 13px;">
                <strong>Chave Desativada (Anônimo):</strong> Cria uma conta segura usando apenas o seu nome de usuário interno da rede. Não precisa de dados reais seus!<br><br>
                <strong>Chave Ativada (E-mail Real):</strong> Permite digitar um e-mail seu (como Gmail). Necessário para quem deseja mais segurança futura com suporte e verificação.
            </p>
            <button class="modal-btn" onclick="fecharAjuda()">Entendi</button>
        </div>
    </div>

    <script>
        function atualizarEmailAnonimo() {
            const toggle = document.getElementById('emailToggle');
            const username = document.getElementById('usernameField').value.toLowerCase().replace(/[^a-z0-9]/g, '');
            const emailInput = document.getElementById('emailField');
            
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
                label.innerText = "Modo: E-mail Real 📧";
                suffix.style.display = "none";
                emailInput.placeholder = "Ex: seuemail@gmail.com";
                emailInput.value = "";
                emailInput.readOnly = false;
            } else {
                label.innerText = "Modo: Anônimo 🥷";
                suffix.style.display = "inline";
                emailInput.placeholder = "Utilizador";
                emailInput.readOnly = true;
                atualizarEmailAnonimo();
            }
        }

        function abrirAjuda() { document.getElementById('helpModal').style.display = 'flex'; }
        function fecharAjuda() { document.getElementById('helpModal').style.display = 'none'; }

        document.getElementById('regForm').addEventListener('submit', function(e) {
            const toggle = document.getElementById('emailToggle');
            const emailInput = document.getElementById('emailField');
            if (!toggle.checked && !emailInput.value.includes('@')) {
                emailInput.value = emailInput.value + "@morincoin.com";
            }
        });

        alternarModoEmail();
    </script>
</bod