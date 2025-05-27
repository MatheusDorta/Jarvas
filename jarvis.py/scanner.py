"""
Módulo de Escaneamento do Jarvas.

Este arquivo contém as funções de análise do sistema, separadas da lógica
principal de execução. Cada função aqui é uma "ferramenta" que o Jarvas usa
para inspecionar processos, arquivos, etc.
"""
import psutil
import os


def processos_que_usam_muita_ram(limite_mb=300):
    """
    Encontra processos com alto uso de RAM, mas baixo uso de CPU.
    """
    processos_suspeitos = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
            cpu_percent = proc.info['cpu_percent']

            if mem_mb > limite_mb and cpu_percent < 5:
                processos_suspeitos.append((
                    proc.info['name'],
                    int(mem_mb),
                    proc.info['pid']
                ))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processos_suspeitos


def encontrar_arquivos_grandes(pastas, limite_mb=10000):
    """
    Busca recursivamente por arquivos maiores que um limite em uma lista de pastas.
    """
    arquivos_grandes = []
    for pasta_inicial in pastas:
        for raiz, dirs, arquivos in os.walk(pasta_inicial):
            for nome_arquivo in arquivos:
                try:
                    caminho_completo = os.path.join(raiz, nome_arquivo)
                    tamanho_mb = os.path.getsize(caminho_completo) / (1024 * 1024)

                    if tamanho_mb > limite_mb:
                        arquivos_grandes.append((caminho_completo, int(tamanho_mb)))
                except (FileNotFoundError, PermissionError):
                    continue
    return arquivos_grandes
