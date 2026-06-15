# 🪙 MorinCoin - Rede de Testes e Simulação de Economia

Bem-vindo ao repositório oficial da **MorinCoin**! Este é um projeto experimental desenvolvido em Python utilizando o framework Flask e banco de dados SQLite3. O objetivo principal é simular o funcionamento básico de uma rede de transações (estilo blockchain) e estudar o comportamento econômico e a cooperação entre usuários.

---

## 🚀 Funcionalidades Atuais

- **Painel do Usuário:** Interface escura e intuitiva para visualização de saldos em tempo real.
- **Transferências Seguras:** Envio de moedas (MRN) entre carteiras através de usernames com validação de saldo.
- **Histórico Geral (Blockchain):** Listagem pública e em tempo real de todas as transações realizadas na rede.
- **Painel Mestre (Admin):** Área restrita para geração de códigos de convite ativos.

---

## 🔒 Segurança do Projeto

Para garantir a integridade do ambiente de testes e proteger a hospedagem na Render, a segurança foi estruturada da seguinte forma:
- **Variáveis de Ambiente:** Chaves secretas de sessão ficam isoladas no script do servidor.
- **Isolamento de Banco:** O arquivo `morincoin.db` é gerado localmente na hospedagem e não fica exposto publicamente no GitHub, prevenindo acessos externos não autorizados aos dados de login.
- **Contas de Teste:** Contas pré-configuradas para simulação com saldos variados para movimentação da rede.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Flask** (Servidor Web e Rotas)
- **SQLite3** (Armazenamento de dados e tabelas)
- **HTML5 & CSS3** (Interface responsiva para dispositivos móveis)
- **Render** (Hospedagem em nuvem)

---

## 📈 Próximos Passos (Roadmap)

- [ ] Ajustar o sistema de novos registros com validação dinâmica de convites.
- [ ] Implementar gráficos ou logs mais detalhados para o Histórico de Blocos.
- [ ] Criar dinâmicas de economia real usando saldo de MorinCoins.
