import psutil
import pyttsx3
import os
import getpass

###### Leitor de processos que usam muita RAM ######
#Esse código verifica os processos que estão usando muita RAM e fala o nome do processo e o PID.
#iniciar o motor de fala
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Define velocidade de fala

def falar(texto):
    print("[Jarvis]" + texto)
    engine.say(texto)
    engine.runAndWait()
    
def processos_que_usam_muita_ram(limite_mb=300):
    processo_suspeitos= []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
        try:
            mem_mb = proc.info['memory_info'].rss / (1024 * 1024) 
            cpu = proc.info['cpu_percent']
            if mem_mb > limite_mb and cpu < 5:
                processo_suspeitos.append((proc.info['name'], mem_mb, proc.info['pid'],))
        except (psutil.NoSuchProcess, psutil.AcessDenied):
            continue
    return processo_suspeitos

#Execução 
falar ("Iniciando verificação de processos...")

processos = processos_que_usam_muita_ram()

if processos:
    falar(f"Encontrei {len(processos)} processos que estão usando muita RAM.")
    for nome, mem, pid in processos:
        falar(f"O processo {nome}, PID {pid}, está usando {int(mem)} MB de RAM.")       
else:
    falar("Todos os processos estão dentro dos limites normais de uso de RAM.")
        


### Escanei arquivos grandes ###
def encontrar_arquivos_grandes (pastas, limite_mb=10000):
    arquivos_grandes = []
    for pasta in pastas: 
        for raiz, dirs, arquivos in os.walk(pasta):
           for nome in arquivos:
               try:
                   caminho = os.path.join(raiz, nome)
                   tamanho_mb = os.path.getsize(caminho) / (1024 * 1024)
                   if tamanho_mb > limite_mb:
                       arquivos_grandes.append((caminho, int(tamanho_mb)))
               except Exception:
                   continue
    return arquivos_grandes

# Definir as pastas a serem verificadas
usuario = getpass.getuser()
pastas_para_verificar = [
    f"C:\\Users\\{usuario}\\Documents",
    f"C:\\Users\\{usuario}\\Downloads",
    f"C:\\Users\\{usuario}\\Desktop",
    f"C:\\Users\\{usuario}\\Videos",
    f"C:\\Users\\{usuario}\\Pictures",
    f"C:\\Users\\{usuario}\\Music",
    f"C:\\Users\\{usuario}\\AppData\\Local",
]

falar ("Iniciando verificação de arquivos grandes...")

arquivos_grandes = encontrar_arquivos_grandes(pastas_para_verificar)

if arquivos_grandes:
    falar(f"Econtrei {len(arquivos_grandes)} arquivo(s) maior que 10 GB.")
    for caminho, tamanho in sorted(arquivos_grandes, key=lambda x:-x[1])[:5]:
        # Falar o caminho e o tamanho do arquivo
        falar(f"{os.path.basename(caminho)} com {tamanho} MB.")
else:
    falar("Não encontrei arquivos grandes nas pastas especificadas.")   
    
    falar("Verificação concluída, se precisar de mais alguma coisa, é só chamar.")   