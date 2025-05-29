# Jarvis - Assistente Pessoal de Sistema 🤖

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge)

Um assistente pessoal de sistema, inspirado no J.A.R.V.I.S. de Tony Stark, construído em Python para monitorar, otimizar e interagir com seu computador de forma autônoma e através de uma interface web amigável.

## ✨ Funcionalidades Principais

- **Análise de Processos Ociosos:** Detecta processos que consomem muita RAM com baixo uso de CPU.
- **Detecção de Arquivos Grandes:** Escaneia pastas em busca de arquivos que ocupam espaço desnecessário.
- **Feedback por Voz:** Comunica ações e descobertas importantes (na versão de linha de comando/agendada).
- **API Robusta com FastAPI:** Oferece endpoints para controle e visualização de dados do sistema.
- **Interface de Linha de Comando (CLI):** Permite executar tarefas específicas e iniciar o modo agendador.
- **Agendamento Automático de Tarefas:** Roda em segundo plano, executando verificações em intervalos programados.
- **Configuração Externa e Segura:** Utiliza um arquivo `.env` para senhas, caminhos e outros parâmetros.
- **Logging Detalhado:** Mantém um registro de atividades no arquivo `Jarvis.log`.
- **Painel de Controle Web Interativo (Streamlit):** Uma interface gráfica para visualizar status, logs e interagir com o Jarvis.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Backend (API & Lógica Central):**
    - **FastAPI:** Para construção da API RESTful.
    - **Uvicorn:** Servidor ASGI para rodar a API FastAPI.
    - **psutil:** Para obter informações do sistema (processos, memória, disco).
    - **pyttsx3:** Para a síntese de voz.
    - **APScheduler:** Para o agendamento de tarefas em segundo plano.
    - **python-dotenv:** Para o gerenciamento de variáveis de ambiente (`.env`).
- **Frontend (Dashboard):**
    - **Streamlit:** Para a criação da interface web interativa.
    - **Requests:** Para comunicação do Dashboard com a API do Jarvis.

## 🚀 Instalação e Configuração

Siga os passos abaixo para executar o Jarvis em sua máquina.

**1. Clone o repositório:**
```bash
git clone [https://github.com/MatheusDorta/Jarvas.git](https://github.com/MatheusDorta/Jarvas.git)
cd Jarvas
```
**2. Crie e ative um ambiente virtual:**
```bash
# Crie o ambiente
python -m venv venv

# Ative o ambiente (Windows)
.\venv\Scripts\activate

# Ative o ambiente (Linux/macOS)
source venv/bin/activate
```
**3. Instale as dependências:**
#Obs: Certifique-se de que seu arquivo requirements.txt está atualizado com todas as bibliotecas (fastapi, uvicorn, streamlit, requests, psutil, pyttsx3, apscheduler, python-dotenv). Se não estiver, gere-o novamente com pip freeze > requirements.txt após instalar todas as dependências listadas acima.
```bash
pip install -r requirements.txt
```
**4. Configure suas variáveis de ambiente:**
- **Crie uma cópia do arquivo .env.example (se ainda não o fez em passos anteriores) e renomeie-a para .env.**
- **Abra o arquivo .env e edite as variáveis com os seus caminhos e preferências. Exemplo:**
<!-- end list -->
```# Exemplo de configuração no .env
PASTAS_SCAN_ARQUIVOS="C:\Users\SEU_NOME_DE_USUARIO\Documents,C:\Users\SEU_NOME_DE_USUARIO\Downloads"
LIMITE_MB_ARQUIVOS="5000"
```

## ⚙️ Modo de Uso
O Jarvis possui diferentes modos de operação:

**1. Servidor da API (Backend)**
Este é o "cérebro" que precisa estar rodando para o Dashboard Web funcionar.
Para iniciar o servidor da API: (No terminal, com o ambiente virtual ativado, na pasta do projeto)
```bash
uvicorn api:app --reload
```
**2. Interface Web (Dashboard com Streamlit)
A interface gráfica para interagir com o Jarvis.
Requisito: O servidor da API (item acima) precisa estar rodando em outro terminal.

Para iniciar o Dashboard: (Em um NOVO terminal, com o ambiente virtual ativado, na pasta do projeto)
```bash
streamlit run dashboard.py
```
***3. Linha de Comando (CLI) e Agendador (main.py)
Para execuções pontuais ou para iniciar o modo de agendamento independente da API.
 - Verificar processos:
```bash
python main.py --processos
```
- Verificar arquivos grandes:
```bash
python main.py --arquivos
```
- Executar todas as verificações:
```bash
python main.py
```
- Iniciar em modo agendador:
```bash
python main.py --agendar
```
(Pressione Ctrl + C para parar o agendador).
- Ajuda para os comandos do main.py:
```bash
python main.py --help
```
## 🗺️ Estrutura do Projeto (Simplificada)
```
Jarvis/                 # Pasta raiz do seu projeto
├── .env                # Configurações e chaves (NÃO ENVIAR AO GITHUB)
├── .env.example        # Exemplo do arquivo .env (ENVIAR AO GITHUB)
├── .gitignore          # Especifica arquivos a serem ignorados pelo Git
├── api.py              # Lógica da API com FastAPI
├── dashboard.py        # Lógica da Interface Web com Streamlit
├── main.py             # Lógica CLI e do Agendador APScheduler
├── scanner.py          # Funções de escaneamento (processos, arquivos)
├── Jarvis.log          # Arquivo de log gerado pelo sistema
├── requirements.txt    # Dependências do projeto Python
└── venv/               # Pasta do ambiente virtual (Ignorada pelo Git)
```

## ✍️ Autor
## Matheus Dorta

GitHub: @MatheusDorta
<!-- end list -->
