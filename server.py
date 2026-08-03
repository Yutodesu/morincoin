import os
from flask import Flask, request, redirect, session, render_template_string
import psycopg2
app=Flask(__name__)
app.secret_key=os.environ.get('FLASK_SECRET_KEY','morincoin-dev-key')
DB=os.environ.get('DATABASE_URL')
ADMIN=os.environ.get('ADMIN_EMAIL','admin@morin.com')
PASS=os.environ.get('ADMIN_PASSWORD','admin123')

def conn(): return psycopg2.connect(DB,sslmode='require')
def init():
 c=conn();x=c.cursor();x.execute("CREATE TABLE IF NOT EXISTS usuarios(id SERIAL PRIMARY KEY,email TEXT UNIQUE NOT NULL,senha TEXT NOT NULL,username TEXT UNIQUE NOT NULL,saldo INTEGER DEFAULT 150,is_admin INTEGER DEFAULT 0)");x.execute("SELECT 1 FROM usuarios WHERE email=%s",(ADMIN,));
 if not x.fetchone(): x.execute("INSERT INTO usuarios(email,senha,username,saldo,is_admin) VALUES(%s,%s,'admin',10000,1)",(ADMIN,PASS))
 c.commit();x.close();c.close()
STYLE="<style>body{font-family:Arial;background:#0b1020;color:white;display:flex;justify-content:center;padding:8vh 10px}.box{background:#18233b;padding:28px;border-radius:16px;width:380px}h1{color:#38bdf8;text-align:center}input,button{width:100%;box-sizing:border-box;padding:13px;margin:7px 0;border-radius:8px;border:0}input{background:#0b1020;color:white}button{background:#0ea5e9;color:white;font-weight:bold}a{color:#7dd3fc}</style>"
def page(body): return STYLE+"<main class='box'>"+body+"</main>"
@app.route('/',methods=['GET','POST'])
def home():
 if request.method=='POST':
  c=conn();x=c.cursor();x.execute('SELECT id,username,saldo FROM usuarios WHERE email=%s AND senha=%s',(request.form['email'],request.form['senha']));r=x.fetchone();x.close();c.close()
  if r: session['u']=r;return redirect('/painel')
  return page('<h1>🪙 MorinCoin</h1><p>Login inválido.</p>'+LOGIN)
 return page('<h1>🪙 MorinCoin</h1>'+LOGIN+'<p>Projeto MRN em funcionamento.</p>')
LOGIN="<form method='post'><input name='email' type='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button>Entrar</button></form><p><a href='/registro'>Criar conta</a></p>"
@app.route('/registro',methods=['GET','POST'])
def registro():
 if request.method=='POST':
  c=conn();x=c.cursor()
  try: x.execute("INSERT INTO usuarios(email,senha,username) VALUES(%s,%s,%s)",(request.form['email'],request.form['senha'],request.form['username']));c.commit();x.close();c.close();return redirect('/')
  except Exception: c.rollback();x.close();c.close();return page('<h1>MorinCoin</h1><p>E-mail ou usuário já cadastrado.</p><a href="/registro">Voltar</a>')
 return page("<h1>🔑 Criar conta</h1><form method='post'><input name='username' placeholder='Usuário' required><input name='email' type='email' placeholder='E-mail' required><input name='senha' type='password' placeholder='Senha' required><button>Criar conta</button></form><p><a href='/'>Voltar</a></p>")
@app.route('/painel')
def painel():
 if 'u' not in session:return redirect('/')
 u=session['u'];return page(f'<h1>Olá, {u[1]}!</h1><h2 style="text-align:center;color:#34d399">{u[2]} MRN</h2><p>Seu painel MorinCoin está online.</p><a href="/sair">Sair</a>')
@app.route('/sair')
def sair():session.clear();return redirect('/')
try:init()
except Exception as e: print('DB:',e,flush=True)
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)))
