# scanner.py

# ==============================================================================
# BLOCO 1: IMPORTS
# - O que faz: Carrega as bibliotecas necessárias para as funções de scan.
# ==============================================================================
import os
import psutil  # Para interagir com processos e uso de sistema
import logging # Para registrar eventos e erros

# ==============================================================================
# BLOCO 2: FUNÇÃO PARA ENCONTRAR PROCESSOS COM ALTO USO DE RAM
# - O que faz: Itera sobre os processos do sistema e identifica aqueles que
#              consomem muita memória RAM e têm baixo uso de CPU.
# ==============================================================================
def processos_que_usam_muita_ram(limite_mb=300):
    """
    Encontra processos com alto uso de RAM, mas baixo uso de CPU.

    Args:
        limite_mb (int, optional): Limite em MB para considerar um processo
                                   como alto consumidor. Padrão é 300.

    Returns:
        list[tuple]: Lista de tuplas, cada uma contendo (nome, memoria_mb, pid)
                     dos processos suspeitos.
    """
    processos_suspeitos = []
    # ✨ LOG: Informa o início do scan de processos
    logging.info(f"SCANNER: Iniciando varredura de processos com limite de {limite_mb}MB.")

    # Itera sobre processos pedindo apenas os atributos necessários
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            # Coleta informações do processo
            proc_info = proc.info # Acessa o dicionário de informações uma vez
            mem_mb = proc_info['memory_info'].rss / (1024 * 1024)
            cpu_percent = proc_info['cpu_percent']

            # Verifica se atende aos critérios
            if mem_mb > limite_mb and cpu_percent < 5:
                processos_suspeitos.append((
                    proc_info['name'],
                    int(mem_mb),
                    proc_info['pid']
                ))
        # ✨ BLOCO TRY-EXCEPT MELHORADO PARA ROBUSTEZ ✨
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e_psutil:
            logging.warning(f"SCANNER: Exceção psutil ao acessar PID {proc.pid if hasattr(proc, 'pid') else 'desconhecido'}: {type(e_psutil).__name__}. Pulando.")
            continue # Pula para o próximo processo
        except KeyError as e_key:
            logging.warning(f"SCANNER: Chave não encontrada no proc.info para PID {proc.pid if hasattr(proc, 'pid') else 'desconhecido'}: {e_key}. Pulando.")
            continue
        except Exception as e_geral:
            logging.error(f"SCANNER: Erro inesperado com PID {proc.pid if hasattr(proc, 'pid') else 'desconhecido'}: {type(e_geral).__name__} - {e_geral}. Pulando.")
            continue
            
    if not processos_suspeitos:
        logging.info(f"SCANNER: Nenhum processo encontrado acima do limite de {limite_mb}MB e com CPU < 5%.")
    else:
        logging.info(f"SCANNER: Encontrados {len(processos_suspeitos)} processos suspeitos.")
    return processos_suspeitos

# ==============================================================================
# BLOCO 3: FUNÇÃO PARA ENCONTRAR ARQUIVOS GRANDES
# - O que faz: Percorre as pastas especificadas recursivamente e identifica
#              arquivos que excedem um determinado limite de tamanho.
# ==============================================================================
def encontrar_arquivos_grandes(pastas, limite_mb=10000):
    """
    Busca recursivamente por arquivos maiores que um limite em uma lista de pastas.

    Args:
        pastas (list[str]): Lista de caminhos de pastas para escanear.
        limite_mb (int, optional): Tamanho mínimo em MB para um arquivo ser
                                   considerado grande. Padrão é 10000 (10GB).

    Returns:
        list[tuple]: Lista de tuplas, cada uma contendo (caminho_completo, tamanho_mb)
                     dos arquivos grandes encontrados.
    """
    arquivos_grandes = []
    # ✨ LOG: Informa o início do scan de arquivos
    logging.info(f"SCANNER: Iniciando varredura de arquivos grandes. Limite: {limite_mb}MB. Pastas: {pastas}")

    for pasta_inicial in pastas:
        logging.debug(f"SCANNER: Escaneando pasta: {pasta_inicial}")
        if not os.path.isdir(pasta_inicial): # ✨ ADICIONADO: Verificação se a pasta existe
            logging.warning(f"SCANNER: Pasta '{pasta_inicial}' não existe ou não é um diretório. Pulando.")
            continue

        for raiz, _, arquivos_na_pasta in os.walk(pasta_inicial):
            logging.debug(f"SCANNER: Em '{raiz}', analisando {len(arquivos_na_pasta)} arquivos.")
            for nome_arquivo in arquivos_na_pasta:
                caminho_completo = "" # Inicializa para o bloco finally
                try:
                    caminho_completo = os.path.join(raiz, nome_arquivo)
                    if not os.path.isfile(caminho_completo): # ✨ ADICIONADO: Garante que é um arquivo
                        logging.debug(f"SCANNER: Item '{caminho_completo}' não é um arquivo. Pulando.")
                        continue

                    tamanho_bytes = os.path.getsize(caminho_completo)
                    tamanho_em_mb = tamanho_bytes / (1024 * 1024)
                    
                    logging.debug(f"SCANNER: Verificando: {caminho_completo}, Tamanho: {tamanho_em_mb:.2f}MB")
                    
                    if tamanho_em_mb > limite_mb:
                        logging.info(f"SCANNER: ARQUIVO GRANDE ENCONTRADO: {caminho_completo} ({tamanho_em_mb:.2f}MB)")
                        arquivos_grandes.append((caminho_completo, int(tamanho_em_mb)))
                # ✨ BLOCO TRY-EXCEPT MELHORADO PARA ROBUSTEZ ✨
                except FileNotFoundError:
                    logging.warning(f"SCANNER: Arquivo não encontrado durante getsize: {caminho_completo}. Pode ter sido removido. Pulando.")
                    continue
                except PermissionError:
                    logging.warning(f"SCANNER: Sem permissão para acessar: {caminho_completo}. Pulando.")
                    continue
                except Exception as e:
                    logging.error(f"SCANNER: Erro inesperado ao processar arquivo '{caminho_completo}': {type(e).__name__} - {e}. Pulando.")
                    continue
                    
    if not arquivos_grandes:
        logging.info(f"SCANNER: Nenhum arquivo encontrado acima do limite de {limite_mb}MB nas pastas especificadas.")
    else:
        logging.info(f"SCANNER: Encontrados {len(arquivos_grandes)} arquivos grandes.")
    return arquivos_grandes
