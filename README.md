# 🚀 Syntax Arena

<div align="center">
  <img src="imagens/banner.png" alt="Syntax Arena Logo" width="600px">
  <p><b>O bot definitivo para comunidades que misturam programação e games.</b></p>
</div>

---

## 📌 Sobre o Projeto
O **Syntax Arena** é um bot modular para o Discord desenvolvido em Python utilizando a biblioteca `discord.py`. Ele foi criado para gerenciar e dinamizar comunidades focadas em tecnologia e jogos, automatizando a configuração do servidor, oferecendo integração com a API do GitHub, sistema de cargos por menu interativo e ferramentas de moderação e entretenimento.

---

## ⚙️ Principais Funcionalidades

* 🛠️ **Setup Automático do Servidor:** Criação automatizada de categorias, canais organizados e cargos essenciais, evitando duplicidade e limpando estruturas antigas.
* 🎴 **Painel de Cargos Interativo:** Sistema persistente onde os usuários podem escolher entre os papéis de *Programador*, *Gamer* ou *Ambos*, liberando automaticamente as salas de voz e texto correspondentes.
* 🐙 **Integração com o GitHub:** Permite que os membros vinculem seus perfis (`!registrar`) e consultem estatísticas e links diretos de qualquer usuário (`!github`).
* 🛡️ **Moderação e Utilidades:** Comandos práticos para limpeza de chat (`!clear`), verificação de latência (`!ping`) e consulta de informações de usuários (`!userinfo`).
* 🎵 **Música e Projetos:** Comandos de reprodução de áudio em canais de voz e criação de canais de projetos privados.
* ☁️ **Alta Disponibilidade:** Integrado com um servidor web leve em Flask (`keep_alive.py`) para facilitar o deploy e monitoramento contínuo em plataformas de nuvem como o Render.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.12**
* **discord.py** (com suporte a voz e componentes UI)
* **Flask** (para o endpoint keep-alive)
* **Spotipy & yt-dlp** (para gerenciamento de mídia)
* **SQLite / Requests**

---

## 📋 Lista de Comandos

### ⚙️ Configuração (Administrador)
* `!setup` / `/setup` — Configura ou atualiza toda a estrutura de canais, cargos e painéis do servidor.

### 🎭 Cargos
* `!cargo` / `/cargo` — Abre o painel interativo de seleção de cargos (Programador / Gamer).

### 🐙 GitHub
* `!registrar <usuario>` — Vincula o seu nome de usuário do GitHub.
* `!github` — Visualiza o seu perfil do GitHub cadastrado.
* `!github @membro` — Visualiza o perfil do GitHub de outro membro.

### 🛡️ Moderação & Info
* `!ping` — Mostra a latência atual do bot.
* `!userinfo [@membro]` — Exibe detalhes e cargos do usuário.
* `!clear <quantidade>` — Apaga mensagens em massa no canal.

### 🎵 Música e Projetos
* `!play <nome da música>` — Toca uma música no canal de voz atual.
* `!stop` — Para a reprodução de áudio e desconecta o bot.
* `!criar_projeto` — Cria um canal de projeto privado (exige cadastro prévio no GitHub).

---

## 🚀 Como Executar o Projeto Localmente

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/syntax-arena.git](https://github.com/SEU_USUARIO/syntax-arena.git)
   cd syntax-arena
