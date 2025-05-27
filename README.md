# Jarvis - Assistente Pessoal de Sistema 🤖

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green?style=for-the-badge)

Um assistente pessoal de sistema, inspirado no J.A.R.V.I.S. de Tony Stark, construído em Python para monitorar e otimizar seu computador de forma autônoma.

## ✨ Funcionalidades Principais

- **Análise de Processos Ociosos:** Detecta processos que consomem muita memória RAM, mas que estão com baixo uso de CPU.
- **Detecção de Arquivos Grandes:** Escaneia pastas pré-definidas em busca de arquivos que ocupam espaço desnecessário.
- **Feedback por Voz:** Comunica suas ações e descobertas usando uma voz sintetizada.
- **Interface de Linha de Comando (CLI):** Permite executar tarefas específicas através de comandos no terminal.
- **Agendamento Automático:** Roda em segundo plano, executando as tarefas de verificação em intervalos programados.
- **Configuração Externa:** Utiliza um arquivo `.env` para facilitar a configuração de pastas e limites sem alterar o código.
- **Logging Detalhado:** Mantém um registro de todas as atividades no arquivo `Jarvis.log` para depuração e histórico.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **psutil:** Para obter informações do sistema (processos, memória).
- **pyttsx3:** Para a síntese de voz (Text-to-Speech).
- **APScheduler:** Para o agendamento de tarefas em segundo plano.
- **python-dotenv:** Para o gerenciamento de variáveis de ambiente (`.env`).

## 🚀 Instalação e Configuração

Siga os passos abaixo para executar o Jarvis em sua máquina.

**1. Clone o repositório:**
```bash
git clone [https://github.com/MatheusDorta/Jarvas.git](https://github.com/MatheusDorta/Jarvas.git)
cd Jarvas

# Crie o ambiente
python -m venv venv

# Ative o ambiente (Windows)
.\venv\Scripts\activate

# Ative o ambiente (Linux/macOS)
source venv/bin/activate


pip install -r requirements.txt

# Exemplo de configuração no .env
PASTAS_SCAN_ARQUIVOS="C:\Users\SEU_NOME_DE_USUARIO\Documents,C:\Users\SEU_NOME_DE_USUARIO\Downloads"
LIMITE_MB_ARQUIVOS="5000"
