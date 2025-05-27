# 🤖 Jarvis - Assistente Inteligente para Monitoramento do Sistema

Jarvis é um assistente de sistema pessoal, inspirado no J.A.R.V.I.S do Tony Stark, feito em Python para te ajudar a manter seu computador mais limpo e eficiente. Ele analisa processos ociosos que consomem muita memória RAM e detecta arquivos grandes que ocupam espaço desnecessariamente no seu sistema.

## 📦 Funcionalidades

- Verifica processos com alto uso de RAM e pouca CPU.
- Informa os principais processos que podem estar deixando o sistema lento.
- Escaneia pastas como `Downloads`, `Documents`, `Videos` e `Desktop` em busca de arquivos maiores que 1 GB.
- Notificação por voz (via `pyttsx3`) para imitar a experiência de um assistente virtual.
- Totalmente personalizável e modular.

## 🧠 Tecnologias Utilizadas

- Python 3.10+
- [psutil](https://pypi.org/project/psutil/) — para análise de processos
- [pyttsx3](https://pypi.org/project/pyttsx3/) — para conversão de texto em fala
- Módulos nativos: `os`, `getpass`, `time`

## 🚀 Como Usar

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/jarvis-assistente.git
cd jarvis-assistente

 **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
