import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")
st.markdown("Monitoramento centralizado dos logs de backup dos clientes.")

# --- CONEXÃO COM A PLANILHA ---
# O link fornecido foi convertido para formato CSV direto
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300) # Atualiza o cache a cada 5 minutos
def load_data():
    try:
        # Lendo o CSV da publicação web do Google
        df = pd.read_csv(CSV_URL)
        
        # Mapeamento provável das colunas do Google Forms
        # Coluna 0: Timestamp (Carimbo)
        # Coluna 1: Hardware Hash
        # Coluna 2: Status
        # Coluna 3: Nome do Arquivo
        # Coluna 4: Data/Hora do Arquivo
        df.columns = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info']
        
        # Tratamento de Datas
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Pega apenas o último status enviado por cada cliente único
        df_latest = df.sort_values('Data_Envio').drop_duplicates('Hardware_Hash', keep='last')
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")
        return None

df_clientes = load_data()

if df_clientes is not None:
    # Lógica de Status: Alerta se o backup tem mais de 24 horas
    agora = datetime.now()
    limite = agora - timedelta(hours=24)
    
    total = len(df_clientes)
    em_dia = len(df_clientes[df_clientes['Data_Backup_DT'] > limite])
    atrasados = total - em_dia

    # Indicadores
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Clientes", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta=f"{atrasados} Críticos", delta_color="inverse")

    st.divider()

    st.subheader("📋 Status Detalhado")
    
    # Função para destacar linhas atrasadas
    def color_rows(row):
        if pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < limite:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    # Exibição da tabela
    st.dataframe(
        df_clientes.style.apply(color_rows, axis=1),
        use_container_width=True
    )

    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Aguardando o recebimento do primeiro log de backup para exibir os dados.")
