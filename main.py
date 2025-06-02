# ==============================================================================
#                                   JARVIS
#               Ponto de Entrada Principal do Assistente de Sistema
# ==============================================================================

# --- IMPORTS ---
# Bibliotecas Padrão do Python
import os
import logging
import argparse
import getpass
import signal

# Bibliotecas de Terceiros (Instaladas via pip)
import pyttsx3
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

# Módulos Locais do Projeto
from scanner import encontrar_arquivos_grandes, processos_que_usam_muita_ram


# --- CONFIGURAÇÃO INICIAL ---
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o sistema de logging para registrar atividades em um arquivo e no console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Jarvis.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Inicializa o motor de Text-to-Speech (TTS) uma única vez para otimizar a performance
try:
    TTS_ENGINE = pyttsx3.init()
    TTS_ENGINE.setProperty('rate', 180)  # Define a velocidade da fala
except Exception as e:
    logging.error(f"Não foi possível inicializar o motor de voz (pyttsx3): {e}")
    TTS_ENGINE = None


# --- FUNÇÕES PRINCIPAIS ---
def falar(engine, texto):
    """Vocaliza um texto usando o motor de TTS já inicializado."""
    if engine:
        logging.info(f"Jarvis Falando: {texto}")
        engine.say(texto)
        engine.runAndWait()
    else:
        # Caso o motor de voz falhe, exibe a fala no console como alternativa
        print(f"[Jarvis]: {texto}")

def executar_scan_processos(tts_engine):
    """Executa a verificação de processos e reporta os resultados."""
    logging.info("Iniciando verificação de processos.")
    falar(tts_engine, "Iniciando verificação de processos ociosos com alto consumo de memória.")

    processos = processos_que_usam_muita_ram(limite_mb=300)

    if processos:
        mensagem = f"Atenção! Encontrei {len(processos)} processos suspeitos."
        logging.warning(mensagem)
        falar(tts_engine, mensagem)
        for nome, mem, pid in processos:
            logging.info(f"Processo: {nome}, PID: {pid}, Consumo: {mem} MB")
            falar(tts_engine, f"O processo {nome} está consumindo {mem} megabytes.")
    else:
        logging.info("Nenhum processo suspeito encontrado.")
        falar(tts_engine, "Análise de processos concluída. Nenhum processo suspeito encontrado.")

def executar_scan_arquivos(tts_engine):
    """Executa a verificação de arquivos grandes e reporta os resultados."""
    logging.info("Iniciando verificação de arquivos grandes.")
    falar(tts_engine, "Iniciando verificação de arquivos grandes. Isso pode demorar um pouco.")

    # Lê as configurações do arquivo .env
    pastas_string = os.getenv("PASTAS_SCAN_ARQUIVOS")
    limite_mb_string = os.getenv("LIMITE_MB_ARQUIVOS")

    if not pastas_string or not limite_mb_string:
        logging.error("Variáveis PASTAS_SCAN_ARQUIVOS ou LIMITE_MB_ARQUIVOS não encontradas no .env")
        falar(tts_engine, "Erro: Configurações de verificação de arquivos não encontradas no arquivo .env.")
        return

    pastas_para_verificar = pastas_string.split(',')
    limite_mb = int(limite_mb_string)

    logging.info(f"Pastas a serem verificadas: {pastas_para_verificar}")
    logging.info(f"Limite de tamanho definido: {limite_mb} MB")

    arquivos_grandes = encontrar_arquivos_grandes(pastas_para_verificar, limite_mb)

    if arquivos_grandes:
        mensagem = f"Encontrei {len(arquivos_grandes)} arquivos com mais de {limite_mb / 1000} gigabytes."
        logging.warning(mensagem)
        falar(tts_engine, mensagem)
        falar(tts_engine, "Os 5 maiores são:")
        for caminho, tamanho in sorted(arquivos_grandes, key=lambda item: item[1], reverse=True)[:5]:
            nome_arquivo = os.path.basename(caminho)
            logging.info(f"Arquivo encontrado: {caminho} ({tamanho} MB)")
            falar(tts_engine, f"O arquivo {nome_arquivo} com {tamanho} megabytes.")
    else:
        logging.info("Nenhum arquivo grande encontrado.")
        falar(tts_engine, "Não encontrei arquivos excessivamente grandes nas pastas verificadas.")


# --- BLOCO DE EXECUÇÃO PRINCIPAL ---
def main():
    """Função principal que analisa os argumentos da linha de comando e orquestra as tarefas."""
    # Configura o parser de argumentos para a Interface de Linha de Comando (CLI)
    parser = argparse.ArgumentParser(description="Jarvis - Seu assistente de sistema pessoal.")
    parser.add_argument('--processos', action='store_true', help='Executa a verificação de processos.')
    parser.add_argument('--arquivos', action='store_true', help='Executa a verificação de arquivos grandes.')
    parser.add_argument('--agendar', action='store_true', help='Inicia o Jarvis em modo de agendamento.')
    args = parser.parse_args()

    # --- MODO AGENDADOR ---
    if args.agendar:
        scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

        def shutdown_handler(sig, frame):
            logging.warning("Sinal de encerramento recebido. Desligando o agendador...")
            falar(TTS_ENGINE, "Encerrando agendador.")
            scheduler.shutdown(wait=False)
            logging.info("Agendador do Jarvas encerrado.")

        signal.signal(signal.SIGINT, shutdown_handler)

        logging.info("Jarvis entrando em modo de agendamento. Pressione Ctrl+C para sair.")
        falar(TTS_ENGINE, "Jarvis em modo de agendamento.")

        # Agenda as tarefas para serem executadas em intervalos definidos
        scheduler.add_job(lambda: executar_scan_processos(TTS_ENGINE), 'interval', hours=2, id='scan_processos')
        scheduler.add_job(lambda: executar_scan_arquivos(TTS_ENGINE), 'interval', hours=8, id='scan_arquivos')
        
        logging.info("Tarefas agendadas. O agendador está iniciando.")
        scheduler.start()

    # --- MODO DE EXECUÇÃO ÚNICA ---
    else:
        executou_algo = False
        if args.processos:
            executar_scan_processos(TTS_ENGINE)
            executou_algo = True
        if args.arquivos:
            if executou_algo:
                logging.info("---") # Separador visual no log
            executar_scan_arquivos(TTS_ENGINE)
            executou_algo = True

        # Se nenhum comando específico foi dado, executa todas as tarefas
        if not executou_algo:
            logging.info("Nenhum comando específico fornecido. Executando todas as verificações.")
            executar_scan_processos(TTS_ENGINE)
            logging.info("---")
            executar_scan_arquivos(TTS_ENGINE)

        logging.info("--- Fim da execução em modo único ---")
        falar(TTS_ENGINE, "Jarvis concluiu as tarefas.")

# Garante que a função main() só seja executada quando o script for rodado diretamente
if __name__ == "__main__":
    main()