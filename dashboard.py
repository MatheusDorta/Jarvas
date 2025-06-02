# dashboard.py

# ==============================================================================
# BLOCO 1: IMPORTS E CONFIGURAÇÕES GLOBAIS
# - O que faz: Carrega todas as ferramentas (bibliotecas) que vamos usar
#              e define constantes globais, como o endereço da nossa API.
# - O que você vê no Dashboard: Nada diretamente, mas este bloco é a
#                               fundação para que todo o resto funcione.
# ==============================================================================
import streamlit as st
import os  # Para manipulação de caminhos de arquivos
import requests  # Para fazer requisições HTTP para a API
import pandas as pd  # Para manipulação de dados e exibição em tabelas

# URL base da nossa API do Jarvis (onde o Uvicorn está rodando o api.py)
API_URL = "http://127.0.0.1:8000"

# ==============================================================================
# BLOCO 2: FUNÇÃO PARA EXIBIR O STATUS DA CONEXÃO COM A API
# - O que faz: Esta função tenta se conectar ao endpoint raiz ("/") da nossa
#              API do Jarvis.
# - O que você vê no Dashboard: A seção "📢 Status da API", que mostra uma
#                               mensagem de sucesso verde se a API estiver
#                               online e respondendo, ou uma mensagem de erro
#                               vermelha caso contrário.
# ==============================================================================
def exibir_status_api(api_base_url: str):
    """Busca e exibe o status da API e a mensagem de boas-vindas."""
    st.header("📢 Status da API")
    try:
        response_root = requests.get(f"{api_base_url}/")
        if response_root.status_code == 200:
            api_data_root = response_root.json()
            mensagem_api = api_data_root.get("Mensagem", "API respondeu, mas a chave 'Mensagem' não foi encontrada.")
            st.success(f"API está funcionando: {mensagem_api}")
        else:
            st.error(f"Erro ao acessar a API (raiz). Status: {response_root.status_code} - {response_root.text}")
    except requests.exceptions.ConnectionError:
        st.error(f"Não foi possível conectar à API do Jarvis em {api_base_url}. Verifique se o servidor FastAPI (Uvicorn) está rodando.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao contatar a API (raiz): {e}")
    st.markdown("---")  # Linha de separação visual

# ==============================================================================
# BLOCO 3: FUNÇÃO PARA EXIBIR O STATUS DO SISTEMA (CPU, RAM, DISCO)
# - O que faz: Esta função pede à API (no endpoint "/status") as informações
#              atuais de uso de CPU, memória RAM e Disco.
# - O que você vê no Dashboard: A seção "📊 Status do Sistema", com três
#                               colunas, cada uma mostrando a porcentagem de
#                               uso e uma barra de progresso para CPU, RAM e Disco.
# ==============================================================================
def exibir_status_sistema(api_base_url: str):
    """Busca e exibe o status do sistema (CPU, RAM, Disco) a partir da API."""
    st.header("📊 Status do Sistema")
    try:
        response_status = requests.get(f"{api_base_url}/status")
        if response_status.status_code == 200:
            status_data = response_status.json()
            
            cpu_usage = status_data.get("cpu_usage_percent", "N/A")
            ram_usage = status_data.get("ram_usage_percent", "N/A")
            disk_usage = status_data.get("disk_usage_percent", "N/A")

            col1, col2, col3 = st.columns(3) # Divide o espaço em 3 colunas
            with col1:
                st.metric(label="🌡️ CPU", value=f"{cpu_usage}%")
                if isinstance(cpu_usage, (int, float)):
                    st.progress(int(cpu_usage))
            with col2:
                st.metric(label="🧠 RAM", value=f"{ram_usage}%")
                if isinstance(ram_usage, (int, float)):
                    st.progress(int(ram_usage))
            with col3:
                st.metric(label="💾 Disco", value=f"{disk_usage}%")
                if isinstance(disk_usage, (int, float)):
                    st.progress(int(disk_usage))
        else:
            st.error(f"Falha ao buscar o status do sistema. Status API: {response_status.status_code} - {response_status.text}")
    except requests.exceptions.ConnectionError:
        st.warning(f"Não foi possível buscar o status do sistema. A API do Jarvis em {api_base_url}/status parece estar offline.")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao buscar o status do sistema: {e}")
    st.markdown("---")  # Linha de separação visual

# ==============================================================================
# BLOCO 4: FUNÇÃO PARA EXIBIR OS LOGS RECENTES DO JARVIS
# - O que faz: Pede à API (no endpoint "/logs") as últimas N linhas do
#              arquivo de log. Permite ao usuário escolher quantas linhas quer ver.
# - O que você vê no Dashboard: A seção "📜 Logs Recentes do Jarvis", com um
#                               campo para digitar o número de linhas, um botão
#                               "Carregar Logs" e uma área de texto onde os
#                               logs são mostrados.
# ==============================================================================
def exibir_logs_api(api_base_url: str):
    """Busca e exibe as últimas N linhas de log da API."""
    st.header("📜 Logs Recentes do Jarvis")
    
    num_linhas_desejadas = st.number_input(
        "Número de linhas de log para exibir:",
        min_value=5, max_value=200, value=20, step=5, key="log_lines_input_key"
    )

    if st.button("Carregar Logs 🔄", key="load_logs_button_key"):
        try:
            response_logs = requests.get(f"{api_base_url}/logs", params={"num_linhas": num_linhas_desejadas})
            
            if response_logs.status_code == 200:
                logs_data = response_logs.json()
                log_content = logs_data.get("logs", "Nenhum log para exibir ou chave 'logs' não encontrada.")
                st.text_area("Visualizador de Logs:", value=log_content, height=300, disabled=True, key="log_viewer_area_key")
                st.success("Logs carregados com sucesso!")
            elif response_logs.status_code == 404:
                st.error(f"Falha ao carregar logs: Arquivo 'Jarvis.log' não encontrado no servidor da API.")
            else:
                st.error(f"Falha ao carregar logs. Status da API: {response_logs.status_code} - {response_logs.text}")
        except requests.exceptions.ConnectionError:
            st.error(f"Não foi possível conectar à API do Jarvis em {api_base_url}/logs. Verifique se o servidor FastAPI está rodando.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado ao buscar os logs: {e}")
    st.markdown("---") # Linha de separação visual

# ==============================================================================
# BLOCO 5: FUNÇÃO PARA EXIBIR OS CONTROLES DE SCAN (PROCESSOS E ARQUIVOS)
# - O que faz: Apresenta botões para o usuário disparar manualmente os scans
#              de processos e de arquivos através da API, permitindo definir
#              os limites de memória/tamanho.
# - O que você vê no Dashboard: A seção "🔬 Iniciar Scans Manuais", com
#                               inputs para limites e botões para cada tipo de scan.
#                               Os resultados são exibidos abaixo de cada botão.
# ==============================================================================
def exibir_controles_scan(api_base_url: str):
    """Exibe os controles para iniciar scans de processos e arquivos via API."""
    st.header("🔬 Iniciar Scans Manuais")

    # Define colunas para os botões de scan
    col_proc, col_arq = st.columns(2)

    # --- Scan de Processos (na primeira coluna) ---
    with col_proc:
        st.subheader("Análise de Processos")
        limite_mb_processos = st.number_input(
            "Limite de Memória (MB) para Processos:",
            min_value=50,
            value=300,  # Valor padrão que a API também usa se nada for enviado
            step=50,
            key="limite_proc_input_key"
        )
        if st.button("Verificar Processos Agora ⚙️", key="btn_scan_processos_key", use_container_width=True):
            with st.spinner("Analisando processos... Por favor, aguarde. 🕵️‍♂️"):
                try: 
                    payload = {"limite_mb": int(limite_mb_processos)} # Garante que é int
                    response = requests.post(f"{api_base_url}/scan/processos", json=payload) # Envia o payload como JSON
                    
                    if response.status_code == 200:
                        resultados = response.json()
                        st.success(resultados.get("message", "Scan de processos concluído com sucesso!"))
                        
                        processos_encontrados = resultados.get("processos")
                        st.session_state.resultados_processos_df = processos_encontrados if processos_encontrados else []
                    else: 
                        st.error(f"Erro ao escanear processos. Status da API: {response.status_code} - {response.text}")
                        st.session_state.resultados_processos_df = None # Indica erro
                except requests.exceptions.ConnectionError:
                    st.error(f"Não foi possível conectar à API do Jarvis em {api_base_url}/scan/processos.")
                    st.session_state.resultados_processos_df = None
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado ao escanear processos: {e}")
                    st.session_state.resultados_processos_df = None
        
        # Exibir resultados do scan de processos (se houver e não deu erro)
        if 'resultados_processos_df' in st.session_state and st.session_state.resultados_processos_df is not None:
            if st.session_state.resultados_processos_df: # Se a lista não estiver vazia
                st.write("Processos Encontrados:")
                df_processos = pd.DataFrame(st.session_state.resultados_processos_df)
                # Ajuste para garantir que as colunas existam antes de renomear
                if not df_processos.empty:
                    df_processos.columns = ["Nome do Processo", "Memória (MB)", "PID"]
                st.dataframe(df_processos, use_container_width=True, hide_index=True)

    # --- Scan de Arquivos (na segunda coluna) ---
    with col_arq:
        st.subheader("Análise de Arquivos Grandes")
        limite_mb_arquivos = st.number_input(
            "Limite de Tamanho (MB) para Arquivos:", # Label corrigido
            min_value=100,
            value=5000, # Valor padrão que a API também usa se nada for enviado
            step=100,
            key="limite_arq_input_key"
        )
        if st.button("Verificar Arquivos Agora 💾", key="btn_scan_arquivos_key", use_container_width=True):
            with st.spinner("Analisando arquivos... Isso pode levar alguns minutos. ⏳"):
                try: 
                    payload_arquivos = {"limite_mb": int(limite_mb_arquivos)} # Garante que é int
                    # CORRIGIDO: Adicionado json=payload_arquivos
                    response_arquivos = requests.post(f"{api_base_url}/scan/arquivos", json=payload_arquivos)
                    
                    if response_arquivos.status_code == 200:
                        resultados_arquivos = response_arquivos.json()
                        st.success(resultados_arquivos.get("message", "Scan de arquivos concluído com sucesso!"))
                        
                        arquivos_encontrados = resultados_arquivos.get("arquivos")
                        st.session_state.resultados_arquivos_df = arquivos_encontrados if arquivos_encontrados else []
                    elif response_arquivos.status_code == 400: 
                        error_detail = response_arquivos.json().get("detail", "Erro de configuração.")
                        st.error(f"Erro de configuração para o scan de arquivos: {error_detail}")
                        st.session_state.resultados_arquivos_df = None
                    else:
                        st.error(f"Erro ao escanear arquivos. Status da API: {response_arquivos.status_code} - {response_arquivos.text}")
                        st.session_state.resultados_arquivos_df = None
                except requests.exceptions.ConnectionError:
                    st.error(f"Não foi possível conectar à API do Jarvis em {api_base_url}/scan/arquivos.")
                    st.session_state.resultados_arquivos_df = None
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado ao escanear arquivos: {e}")
                    st.session_state.resultados_arquivos_df = None
                
        # Exibe os resultados do scan de arquivos (se houver e não deu erro)
        if 'resultados_arquivos_df' in st.session_state and st.session_state.resultados_arquivos_df is not None:
            if st.session_state.resultados_arquivos_df:
                st.write("Arquivos Grandes Encontrados:")
                dados_arquivos_formatados = []
                for arq in st.session_state.resultados_arquivos_df:
                    dados_arquivos_formatados.append({
                        "Nome do Arquivo": os.path.basename(arq.get('caminho', 'N/A')),
                        "Tamanho (MB)": arq.get('tamanho_mb'),
                        "Caminho Completo": arq.get('caminho')
                    })
                df_arquivos = pd.DataFrame(dados_arquivos_formatados)
                # Ajuste para garantir que as colunas existam antes de renomear/selecionar
                if not df_arquivos.empty:
                    # Se quiser manter as 3 colunas:
                    # df_arquivos = df_arquivos[["Nome do Arquivo", "Tamanho (MB)", "Caminho Completo"]]
                    pass # As colunas já são nomeadas corretamente na criação do dicionário
                st.dataframe(df_arquivos, use_container_width=True, hide_index=True)

    st.markdown("---")  # Linha de separação visual após a seção de scans

# ==============================================================================
# BLOCO 6: LAYOUT PRINCIPAL DA APLICAÇÃO STREAMLIT
# - O que faz: Este é o "esqueleto" da nossa página. Ele define o título
#              principal, o ícone na aba do navegador, a mensagem de
#              boas-vindas, a barra lateral (sidebar) e organiza onde cada
#              função de exibição (dos blocos anteriores) será chamada.
# - O que você vê no Dashboard: Toda a estrutura da página: o título, a
#                               mensagem de boas-vindas, a barra lateral à
#                               esquerda, e todas as seções (Status API, Status
#                               Sistema, Logs, Scans) aparecendo no corpo principal.
# ==============================================================================

# Configurações iniciais da página (deve ser o primeiro comando Streamlit, idealmente)
st.set_page_config(
    page_title="Painel Jarvis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal que aparece no topo do painel
st.title("🤖 Painel de Controle do Jarvis")

# Mensagem de boas-vindas e uma breve descrição
st.write("Aqui você pode gerenciar e monitorar o Jarvis, seu assistente virtual inteligente.")
st.markdown("---") # Linha de separação

# Configuração da Barra Lateral (Sidebar)
with st.sidebar:
    st.header("Navegação")
    # Futuramente, podemos adicionar links para diferentes "páginas" do dashboard aqui
    # Ex: st.page_link("dashboard.py", label="Status Geral", icon="📊")
    # Ex: st.page_link("pages/logs_detalhados.py", label="Logs Detalhados", icon="📜")

# Container principal onde o conteúdo do dashboard será renderizado
with st.container():
    exibir_status_api(API_URL)
    exibir_status_sistema(API_URL)
    exibir_logs_api(API_URL)
    exibir_controles_scan(API_URL)

# Seção final com próximos passos ou notas
st.subheader("🚀 Próximos Passos")
st.success("Dashboard com inputs para limites e scans de Processos e Arquivos totalmente funcional! ✔️")
st.info("Podemos agora pensar em: 1. Melhorar a interatividade das tabelas (filtros?). 2. Adicionar controle/visualização do Agendador. 3. Integrar com Telegram para notificações.")
