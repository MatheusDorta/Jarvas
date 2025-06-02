# api.py

# ==============================================================================
# BLOCO 1: IMPORTS
# - O que faz: Carrega todas as bibliotecas e módulos externos e locais
#              necessários para a API funcionar.
# - Interação/Resultado para o Cliente da API: Nenhuma interação direta, mas
#                                              este bloco habilita todas as
#                                              funcionalidades subsequentes.
# ==============================================================================
# Bibliotecas Padrão
import os
import logging
import json # Para manipulação de JSON

# Bibliotecas de Terceiros
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field # Para validação de dados de entrada
import psutil                        # Para obter informações do sistema
from dotenv import load_dotenv      # Para carregar variáveis de ambiente

# Módulos Locais do Projeto
from scanner import processos_que_usam_muita_ram, encontrar_arquivos_grandes

# ==============================================================================
# BLOCO 2: CONFIGURAÇÃO INICIAL
# - O que faz: Executa tarefas de configuração que precisam acontecer uma vez
#              quando a API é iniciada.
# - Interação/Resultado para o Cliente da API:
#   - `load_dotenv()`: Permite que a API use configurações do arquivo .env.
#   - `logging.basicConfig()`: Define como os logs da API serão formatados e
#                              armazenados (em "Jarvis.log" e no console).
#   - `app = FastAPI(...)`: Cria a instância principal da aplicação FastAPI,
#                          que é o coração da nossa API.
# ==============================================================================
# Carrega variáveis de ambiente do arquivo .env (ex: PASTAS_SCAN_ARQUIVOS)
load_dotenv()

# Configuração do sistema de logging específico para esta API
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - API - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Jarvis.log", encoding='utf-8'), # Garante salvar em UTF-8
        logging.StreamHandler()                               # Também mostra no console
    ]
)

# Cria a instância principal do aplicativo FastAPI com título, descrição e versão
app = FastAPI(
    title="Jarvis API",
    description="API para o Assistente Pessoal Jarvis",
    version="1.0.0"
)

# ==============================================================================
# BLOCO 3: MODELOS PYDANTIC (Definição dos Dados de Entrada)
# - O que faz: Define a estrutura e as regras de validação para os dados que
#              a API espera receber no corpo (body) das requisições POST.
# - Interação/Resultado para o Cliente da API:
#   - Se o cliente enviar dados que não correspondem a estes modelos para os
#     endpoints de scan, o FastAPI automaticamente retornará um erro HTTP 422
#     (Unprocessable Entity) com detalhes da validação.
# ==============================================================================
class ProcessScanRequest(BaseModel):
    """Corpo da requisição para disparar um scan de processos."""
    limite_mb: int = Field(default=300, ge=50, description="Limite em MB para um processo ser considerado 'alto consumidor'. Padrão: 300MB.")

class FileScanRequest(BaseModel):
    """Corpo da requisição para disparar um scan de arquivos."""
    limite_mb: int = Field(default=5000, ge=100, description="Limite em MB para um arquivo ser considerado 'grande'. Padrão: 5000MB.")

# ==============================================================================
# BLOCO 4: ENDPOINTS DA API (As "portas de entrada" da API)
# - O que faz: Define os diferentes "endereços" (URLs) que podem ser acessados
#              na API e as funções Python que são executadas quando esses
#              endereços são chamados pelos métodos HTTP corretos (GET, POST).
# - Interação/Resultado para o Cliente da API: Estes são os pontos de contato
#                                              diretos. O cliente faz uma
#                                              requisição para uma dessas URLs e
#                                              recebe uma resposta em JSON.
# ==============================================================================

# --- Endpoint 4.1: Raiz ("/") ---
@app.get("/")
async def read_root():
    """
    Ponto de entrada principal, retorna uma mensagem de boas-vindas.
    
    Interação/Resultado para o Cliente:
    - Cliente acessa a URL base da API (ex: http://127.0.0.1:8000/)
    - Recebe: {"Mensagem": "Bem vindo..."}
    """
    logging.info("API: Endpoint raiz '/' acessado.")
    return {"Mensagem": "Bem vindo a API do Jarvis, seu assistente virtual esta online!"}

# --- Endpoint 4.2: Status do Sistema ("/status") ---
@app.get("/status")
async def get_system_status():
    """
    Coleta e retorna dados de uso de CPU, RAM e Disco do servidor.
    
    Interação/Resultado para o Cliente:
    - Cliente acessa '/status'
    - Recebe um JSON com {"cpu_usage_percent": X, "ram_usage_percent": Y, ...}
    """
    logging.info("API: Endpoint '/status' acessado.")
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage_percent = "N/A" # Valor padrão

    try:
        disk_info = psutil.disk_usage('/')
        disk_usage_percent = disk_info.percent
    except Exception as e:
        logging.error(f"API: Erro ao obter uso do disco: {str(e)}")
        disk_usage_percent = f"Erro ao obter uso do disco: {str(e)}"

    return {
        "cpu_usage_percent": cpu_usage,
        "ram_usage_percent": ram_usage,
        "disk_usage_percent": disk_usage_percent,
    }

# --- Endpoint 4.3: Visualização de Logs ("/logs") ---
@app.get("/logs")
async def get_logs(num_linhas: int = Query(50, description="Número de linhas recentes do log para retornar", ge=1, le=1000)):
    """
    Lê as últimas N linhas do arquivo 'Jarvis.log'.
    Aceita um parâmetro 'num_linhas' na URL.
    
    Interação/Resultado para o Cliente:
    - Cliente acessa '/logs?num_linhas=X'
    - Recebe um JSON com {"logs": "conteúdo_do_log..."} ou erro.
    """
    logging.info(f"API: Endpoint '/logs' acessado, requisitando {num_linhas} linhas.")
    log_file_name = "Jarvis.log"

    try:
        with open(log_file_name, "r", encoding="utf-8", errors='replace') as log_file:
            lines = log_file.readlines()
            last_n_lines = lines[-num_linhas:]
        return {"logs": "".join(last_n_lines)}
    except FileNotFoundError:
        logging.warning(f"API: Arquivo de log '{log_file_name}' não encontrado.")
        raise HTTPException(status_code=404, detail=f"Arquivo de log '{log_file_name}' não encontrado.")
    except Exception as e:
        logging.error(f"API: Erro ao ler o arquivo de log '{log_file_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo de log: {str(e)}")

# --- Endpoint 4.4: Scan de Processos ("/scan/processos") ---
@app.post("/scan/processos")
async def trigger_process_scan(request_data: ProcessScanRequest):
    """
    Recebe um limite de MB, dispara o scan de processos e retorna os resultados.
    
    Interação/Resultado para o Cliente:
    - Cliente envia POST para '/scan/processos' com JSON: {"limite_mb": X}.
    - Recebe JSON com status e lista de processos.
    """
    limite_informado = request_data.limite_mb
    logging.info(f"API: Recebido comando para escanear processos. Limite: {limite_informado}MB.")
    try:
        processos_encontrados = processos_que_usam_muita_ram(limite_mb=limite_informado)

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

# --- Endpoint 4.5: Scan de Arquivos ("/scan/arquivos") ---
@app.post("/scan/arquivos")
async def trigger_file_scan(request_data: FileScanRequest):
    """
    Recebe um limite de MB, dispara o scan de arquivos (pastas do .env, ~HOME~ expandido)
    e retorna os arquivos encontrados.
    
    Interação/Resultado para o Cliente:
    - Cliente envia POST para '/scan/arquivos' com JSON: {"limite_mb": Y}.
    - Recebe JSON com status e lista de arquivos.
    """
    limite_informado = request_data.limite_mb
    logging.info(f"API: Recebido comando para escanear arquivos grandes. Limite: {limite_informado}MB.")
    
    pastas_para_verificar_final = []
    home_dir = os.path.expanduser("~")
    
    try:
        pastas_config_string = os.getenv("PASTAS_SCAN_ARQUIVOS")

        if not pastas_config_string:
            msg_erro_pastas = "Variável PASTAS_SCAN_ARQUIVOS não definida no .env."
            logging.error(f"API: {msg_erro_pastas}")
            raise HTTPException(status_code=400, detail=msg_erro_pastas)

        pastas_raw = pastas_config_string.split(',')
        
        for pasta_template in pastas_raw:
            pasta_processada = pasta_template.strip()
            caminho_final_provisorio = ""
            
            if pasta_processada.startswith("~HOME~/"):
                nome_subpasta = pasta_processada.replace("~HOME~/", "")
                caminho_final_provisorio = os.path.join(home_dir, nome_subpasta)
            elif pasta_processada.startswith("~HOME~\\"):
                nome_subpasta = pasta_processada.replace("~HOME~\\", "")
                caminho_final_provisorio = os.path.join(home_dir, nome_subpasta)
            else:
                caminho_final_provisorio = pasta_processada 
            
            if os.path.exists(caminho_final_provisorio) and os.path.isdir(caminho_final_provisorio):
                pastas_para_verificar_final.append(caminho_final_provisorio)
                # Ajuste no log: Logar a pasta que será usada, não "iniciando scan" aqui.
                logging.debug(f"API: Pasta adicionada para scan: {caminho_final_provisorio}")
            else:
                logging.warning(f"API: Pasta '{caminho_final_provisorio}' (configurada como '{pasta_template.strip()}') não existe ou não é um diretório válido. Ignorando.")
        
        if not pastas_para_verificar_final:
            msg_erro_pastas_validas = "Nenhuma pasta válida encontrada para escanear. Verifique a variável PASTAS_SCAN_ARQUIVOS no .env."
            logging.error(f"API: {msg_erro_pastas_validas}")
            raise HTTPException(status_code=400, detail=msg_erro_pastas_validas)
                
        # Log de início do scan com as pastas validadas
        logging.info(f"API: Iniciando scan de arquivos. Pastas válidas: {pastas_para_verificar_final}, Limite: {limite_informado}MB.")
        arquivos_encontrados = encontrar_arquivos_grandes(pastas=pastas_para_verificar_final, limite_mb=limite_informado)

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
    except ValueError:
        msg_erro_valor = "O limite_mb fornecido não é um número válido ou ocorreu um erro de valor ao processar as configurações."
        logging.error(f"API: {msg_erro_valor}")
        raise HTTPException(status_code=400, detail=msg_erro_valor)
    except Exception as e:
        logging.error(f"API: Erro durante o scan de arquivos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao escanear arquivos: {str(e)}")
    
# --- Endpoint 4.6: Status dos Jobs Agendados ("/jobs/status") ---
@app.get("/scheduler/jobs")
async def get_scheduler_status():
    """
    Lê e retorna o status dos jobs agendados a partir do arquivo 'scheduler_status.json'.
    
    Interação/Resultado para o Cliente da API:
    - Cliente acessa '/scheduler/jobs'.
    - Recebe um JSON contendo a lista de jobs e seus detalhes, ou uma mensagem de erro.
    """
    
    nome_arquivo_status = "scheduler_status.json"
    logging.info(f"API: Endpoint '/scheduler/status' acessado. Lendo status dos jobs agendados do arquivo '{nome_arquivo_status}'.")   
     
    try:
        with open(nome_arquivo_status, "r", encoding="utf-8") as f:
              jobs_status = json.load(f) # Carrega o conteúdo do arquivo JSON
        logging.info(f"API: Status dos jobs agendados lido com sucesso. Total de jobs: {len(jobs_status)}.")
        return jobs_status
    except FileNotFoundError:
        logging.warning(f"API: Arquivo de status '{nome_arquivo_status}' não encontrado.")
        return {"status": "Erro", "message": f"Arquivo de status '{nome_arquivo_status}' não encontrado."}
    except json.JSONDecodeError:
        logging.error(f"API: Erro ao decodificar o arquivo JSON '{nome_arquivo_status}'.")
        raise HTTPException(status_code=500, detail=f"Erro ao decodificar o arquivo JSON: {nome_arquivo_status}. Verifique o formato do arquivo.")
    except Exception as e:
        logging.error(f"API: Erro ao ler o arquivo de status '{nome_arquivo_status}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo de status: {str(e)}")
             

# ==============================================================================
# BLOCO 7: PONTO DE PARTIDA OPCIONAL PARA DESENVOLVIMENTO
# - O que faz: Permite rodar a API diretamente com 'python api.py'.
#              No entanto, para produção ou desenvolvimento mais robusto,
#              é preferível usar 'uvicorn api:app --reload'.
# - Interação/Resultado para o Cliente da API: Se executado, inicia o servidor
#                                              Uvicorn na porta 8000.
# ==============================================================================
# if __name__ == "__main__":
#     import uvicorn
#     logging.info("Iniciando servidor Uvicorn a partir do api.py (para desenvolvimento)...")
#     uvicorn.run(app, host="0.0.0.0", port=8000)
