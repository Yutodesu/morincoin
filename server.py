import os,sqlite3
from flask import Flask,request,redirect,session
app=Flask(__name__);app.secret_key=os.environ.get('FLASK_SECRET_KEY','morincoin-key');DB='morincoin.db'
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 c=db();c.execute('CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY,email TEXT UNIQUE,senha TEXT,username TEXT UNIQUE,saldo INTEGER DEFAULT 150,is_admin INTEGER DEFAULT 0)')
 if not c.execute('SELECT 1 FROM usuarios WHERE email=?',(os.environ.get('ADMIN_EMAIL','admin@morin.com'),)).fetchone(): c.execute('INSERT INTO usuarios(email,senha,username,saldo,is_admin) VALUES(?,?,?,?,1)',(os.environ.get('ADMIN_EMAIL','admin@morin.com'),os.environ.get('ADMIN_PASSWORD','admin123'),'admin',10000))
 c.commit();c.close()
S="<style>body{font-family:Arial;background:#0b1020;color:white;display:flex;justify-content:center;padding:8vh 10px}.box{background:#18233b;padding:28px;border-radius:16px;width:380px}h1{color:#38bdf8;text-align:center}input,button{width:100%;box-sizing:border-box;padding:13px;margin:7px 0;border-radius:8px;border:0}input{background:#0b1020;color:white}button{background:#0ea5e9;color:white;font-weight:bold}a{color:#7dd3fc}</style>"
def p(x):return S+"<main class='box'>"+x+"</main>"
L="<form method='post'><input name='email' type='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button>Entrar</button></form><p><a href='/registro'>Criar conta</a></p>"
@app.route('/',methods=['GET','POST'])
def home():
 if request.method=='POST':
  c=db();u=c.execute('SELECT * FROM usuarios WHERE email=? AND senha=?',(request.form['email'],request.form['senha'])).fetchone();c.close()
  if u:session['id']=u['id'];return redirect('/painel')
  return p('<h1>🪙 MorinCoin</h1><p>Login inválido.</p>'+L)
 return p('<h1>🪙 MorinCoin</h1>'+L+'<p>Rede MRN online.</p>')
@app.route('/registro',methods=['GET','POST'])
def reg():
 if request.method=='POST':
  c=db()
  try:c.execute('INSERT INTO usuarios(email,senha,username) VALUES(?,?,?)',(request.form['email'],request.form['senha'],request.form['username']));c.commit();c.close();return redirect('/')
  except sqlite3.IntegrityError:c.close();return p('<h1>MorinCoin</h1><p>Usuário ou e-mail já existe.</p><a href="/registro">Voltar</a>')
 return p("<h1>🔑 Criar conta</h1><form method='post'><input name='username' placeholder='Usuário' required><input name='email' type='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button>Criar conta</button></form><p><a href='/'>Voltar</a></p>")
@app.route('/painel')
def painel():
 if 'id' not in session:return redirect('/')
 c=db();u=c.execute('SELECT * FROM usuarios WHERE id=?',(session['id'],)).fetchone();c.close();return p(f'<h1>Olá, {u["username"]}!</h1><h2 style="text-align:center;color:#34d399">{u["saldo"]} MRN</h2><p>Seu painel está online.</p><a href="/sair">Sair</a>')
@app.route('/sair')
def sair():session.clear();return redirect('/')
init()
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
