import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")
st.markdown("Monitoramento centralizado dos logs de backup.")

# --- CONEXÃO COM A PLANILHA ---
# O link foi corrigido de '/pubhtml' para '/pub?output=csv'
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300) # Atualiza o cache automaticamente a cada 5 minutos
def load_data():
    try:
        # Lendo o CSV da publicação web do Google
        df = pd.read_csv(CSV_URL)
        
        # Verificação de segurança: Se a planilha estiver vazia
        if df.empty:
            return None

        # Renomeação dinâmica para evitar erros de contagem de colunas
        # Mapeia as colunas por posição, não por nome exato
        # Ordem esperada: [0:Timestamp, 1:Hash, 2:Status, 3:Arquivo, 4:Data_Backup]
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info']
        
        # Se a planilha tiver mais ou menos colunas, ajustamos dinamicamente
        current_cols = list(df.columns)
        mapping = {}
        for i, name in enumerate(new_cols):
            if i < len(current_cols):
                mapping[current_cols[i]] = name
        
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        # Tenta converter a data do backup (formato enviado pelo serviço)
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Filtra para pegar apenas o último status de cada cliente único (Hardware Hash)
        df_latest = df.sort_values('Data_Envio').drop_duplicates('Hardware_Hash', keep='last')
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

df_clientes = load_data()

if df_clientes is not None:
    # Lógica de Status: Alerta se o backup tem mais de 24 horas
    agora = datetime.now()
    limite = agora - timedelta(hours=24)
    
    total = len(df_clientes)
    em_dia = len(df_clientes[df_clientes['Data_Backup_DT'] > limite])
    atrasados = total - em_dia

    # Layout de Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Clientes", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta=f"{atrasados} Críticos", delta_color="inverse")

    st.divider()

    st.subheader("📋 Detalhes dos Dispositivos")
    
    # Função para destacar linhas atrasadas
    def highlight_rows(row):
        # Destaca se o backup estiver atrasado ou se o status for ERRO
        is_late = pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < limite
        is_error = str(row.Status).upper() == "ERRO"
        
        if is_late or is_error:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    # Exibição da tabela formatada
    st.dataframe(
        df_clientes.style.apply(highlight_rows, axis=1),
        use_container_width=True
    )
    
    if st.button("🔄 Atualizar Agora"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Aguardando o recebimento do primeiro log de backup para exibir os dados.")
    st.markdown("Certifique-se de que o serviço foi executado em pelo menos um cliente.")
