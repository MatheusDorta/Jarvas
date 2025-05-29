# dashboard.py

# ==============================================================================
# BLOCO 1: IMPORTS E CONFIGURAÇÕES GLOBAIS
# - O que faz: Carrega todas as ferramentas (bibliotecas) que vamos usar
#              e define constantes globais, como o endereço da nossa API.
# - O que você vê no Dashboard: Nada diretamente, mas este bloco é a
#                               fundação para que todo o resto funcione.
# ==============================================================================
import streamlit as st
import requests  # Para fazer requisições HTTP para a API

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
#              de processos e de arquivos através da API.
# - O que você vê no Dashboard: A seção "🔬 Iniciar Scans Manuais", com um
#                               botão "Verificar Processos Agora ⚙️". Quando
#                               clicado, ele mostra os resultados do scan.
#                               (O botão de arquivos será o próximo!)
# ==============================================================================
def exibir_controles_scan(api_base_url: str):
    """Exibe os controles para iniciar scans de processos e arquivos via API."""
    st.header("🔬 Iniciar Scans Manuais")
    
    # --- Scan de Processos ---
    st.subheader("Análise de Processos")
    if st.button("Verificar Processos Agora ⚙️", key="btn_scan_processos_key"):
        with st.spinner("Analisando processos... Por favor, aguarde. 🕵️‍♂️"):
            try: 
                response = requests.post(f"{api_base_url}/scan/processos")
                
                if response.status_code == 200:
                    resultados = response.json()
                    st.success(resultados.get("message", "Scan de processos concluído com sucesso!"))
                    
                    processos_encontrados = resultados.get("processos")
                    if processos_encontrados: 
                        st.write("Processos Encontrados:")
                        for proc in processos_encontrados:
                            with st.expander(f"⚠️ {proc.get('nome')} (PID: {proc.get('pid')})"):
                                st.write(f" - Consumo de Memória: {proc.get('memoria_mb')} MB")
                else: 
                    st.error(f"Erro ao escanear processos. Status da API: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Não foi possível conectar à API do Jarvis em {api_base_url}/scan/processos. Verifique se o servidor FastAPI está rodando.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado ao escanear processos: {e}")
    st.markdown("---")  # Linha de separação visual


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
    # Ex: st.page_link("pagina_configuracoes.py", label="Configurações Avançadas")

# Container principal onde o conteúdo do dashboard será renderizado
with st.container():
    exibir_status_api(API_URL)          # Chama a função do Bloco 2
    exibir_status_sistema(API_URL)      # Chama a função do Bloco 3
    exibir_logs_api(API_URL)            # Chama a função do Bloco 4
    exibir_controles_scan(API_URL)      # Chama a função do Bloco 5

# Seção final com próximos passos ou notas
st.subheader("🚀 Próximos Passos")
st.info("Adicionar o botão para disparar o Scan de Arquivos e exibir seus resultados no painel.")