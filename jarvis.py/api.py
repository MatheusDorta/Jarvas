# api.py

# --- IMPORTS ---
# Bibliotecas Padrão
import os
import logging

# Bibliotecas de Terceiros
from fastapi import FastAPI, Query, HTTPException
import psutil
from dotenv import load_dotenv

# Módulos Locais
from scanner import processos_que_usam_muita_ram, encontrar_arquivos_grandes

# --- CONFIGURAÇÃO INICIAL ---
# Carrega variáveis de ambiente do arquivo .env (essencial para Uvicorn)
load_dotenv()

# Configuração do sistema de logging para a API
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - API - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Jarvis.log", encoding='utf-8'), # Nome do arquivo de log
        logging.StreamHandler()
    ]
)

# Cria a instância principal do aplicativo FastAPI
app = FastAPI(
    title="Jarvis API",
    description="API para o Assistente Pessoal Jarvis",
    version="1.0.0"
)

# --- ENDPOINTS DA API ---

@app.get("/")
async def read_root():
    """Endpoint raiz da API. Retorna uma mensagem de boas-vindas."""
    return {"Mensagem": "Bem vindo a API do Jarvis, seu assistente virtual esta online!"}

@app.get("/status")
async def get_system_status():
    """Retorna o status atual do sistema (CPU, RAM, Disco)."""
    cpu_usage = psutil.cpu_percent(interval=1)      # Uso da CPU em %
    ram_usage = psutil.virtual_memory().percent     # Uso da RAM em %
    disk_usage_percent = "N/A"                      # Valor padrão caso haja erro

    try:
        disk_info = psutil.disk_usage('/')
        disk_usage_percent = disk_info.percent      # Uso do disco principal em %
    except Exception as e:
        logging.error(f"API: Erro ao obter uso do disco: {str(e)}")
        disk_usage_percent = f"Erro ao obter uso do disco: {str(e)}"

    return {
        "cpu_usage_percent": cpu_usage,
        "ram_usage_percent": ram_usage,
        "disk_usage_percent": disk_usage_percent,
    }

@app.get("/logs")
async def get_logs(num_linhas: int = Query(50, description="Número de linhas recentes do log para retornar", ge=1, le=1000)):
    """Retorna as últimas N linhas do arquivo de log do Jarvis."""
    log_file_name = "Jarvis.log"  # Deve ser o mesmo nome configurado no logging

    try:
        with open(log_file_name, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
            last_n_lines = lines[-num_linhas:]  # Pega as últimas N linhas
        return {"logs": "".join(last_n_lines)}
    except FileNotFoundError:
        logging.warning(f"API: Arquivo de log '{log_file_name}' não encontrado ao tentar ler.")
        raise HTTPException(status_code=404, detail=f"Arquivo de log '{log_file_name}' não encontrado.")
    except Exception as e:
        logging.error(f"API: Erro ao ler o arquivo de log '{log_file_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo de log: {str(e)}")

@app.post("/scan/processos")
async def trigger_process_scan():
    """Dispara a verificação de processos e retorna os resultados."""
    logging.info("API: Recebido comando para escanear processos.")
    try:
        processos_encontrados = processos_que_usam_muita_ram(limite_mb=300)

        if processos_encontrados:
            logging.info(f"API: Scan de processos encontrou {len(processos_encontrados)} processos.")
            resultado_formatado = [
                {"nome": nome, "memoria_mb": mem, "pid": pid}
                for nome, mem, pid in processos_encontrados
            ]
            return {
                "status": "Sucesso",
                "message": f"{len(processos_encontrados)} processos suspeitos encontrados.",
                "processos": resultado_formatado
            }
        else:
            logging.info("API: Scan de processos não encontrou processos suspeitos.")
            return {
                "status": "Sucesso",
                "message": "Nenhum processo suspeito encontrado."
            }
    except Exception as e:
        logging.error(f"API: Erro durante o scan de processos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao escanear processos: {str(e)}")

@app.post("/scan/arquivos")
async def trigger_file_scan():
    """Dispara a verificação de arquivos grandes e retorna os resultados."""
    logging.info("API: Recebido comando para escanear arquivos grandes.")
    try:
        # Lê as configurações do arquivo .env
        pastas_string = os.getenv("PASTAS_SCAN_ARQUIVOS")
        # Corrigido para LIMITE_MB_ARQUIVOS para consistência com o .env que definimos
        limite_mb_string = os.getenv("LIMITE_MB_ARQUIVOS")

        if not pastas_string or not limite_mb_string:
            msg_erro = "Variáveis PASTAS_SCAN_ARQUIVOS ou LIMITE_MB_ARQUIVOS não definidas no .env."
            logging.error(f"API: {msg_erro}")
            raise HTTPException(status_code=400, detail=msg_erro)

        pastas_para_verificar = pastas_string.split(',')
        limite_mb = int(limite_mb_string) # Converte para inteiro

        logging.info(f"API: Iniciando scan. Pastas: {pastas_para_verificar}, Limite: {limite_mb}MB.")
        arquivos_encontrados = encontrar_arquivos_grandes(pastas=pastas_para_verificar, limite_mb=limite_mb)

        if arquivos_encontrados:
            logging.info(f"API: Scan de arquivos encontrou {len(arquivos_encontrados)} arquivos grandes.")
            resultado_formatado = [
                {"caminho": caminho, "tamanho_mb": tamanho}
                for caminho, tamanho in arquivos_encontrados
            ]
            return {
                "status": "Sucesso",
                "message": f"{len(arquivos_encontrados)} arquivos grandes encontrados.",
                "arquivos": resultado_formatado
            }
        else:
            logging.info("API: Scan de arquivos não encontrou arquivos grandes.")
            return {
                "status": "Sucesso",
                "message": "Nenhum arquivo grande encontrado nas pastas e com o limite especificado."
            }
    except ValueError: # Erro específico se LIMITE_MB_ARQUIVOS não for um número
        msg_erro_valor = "LIMITE_MB_ARQUIVOS no .env não é um número válido."
        logging.error(f"API: {msg_erro_valor}")
        raise HTTPException(status_code=400, detail=msg_erro_valor)
    except Exception as e:
        logging.error(f"API: Erro durante o scan de arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao escanear arquivos: {str(e)}")

# --- PONTO DE PARTIDA (Opcional, para rodar com 'python api.py', mas Uvicorn é preferível) ---
# if __name__ == "__main__":
#     import uvicorn
#     logging.info("Iniciando servidor Uvicorn a partir do api.py (para desenvolvimento)...")
#     uvicorn.run(app, host="0.0.0.0", port=8000)