import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")

# --- CONEXÃO COM A PLANILHA DO GOOGLE ---
# Certifique-se de que a planilha tem as colunas na ordem: 
# [Carimbo, Hash, Status, Arquivo, Data Backup, Nome do Cliente]
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        # Carregar dados do Google Sheets
        df = pd.read_csv(CSV_URL)
        if df.empty: return None

        # Mapeamento por posição das colunas
        # Adicionamos a coluna 'Nome_Cliente' que você alimentará manualmente na planilha
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info', 'Nome_Cliente']
        current_cols = list(df.columns)
        
        # Faz o mapeamento dinâmico conforme a quantidade de colunas disponíveis
        mapping = {current_cols[i]: new_cols[i] for i in range(len(new_cols)) if i < len(current_cols)}
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # REGISTRO ÚNICO POR CLIENTE (O mais recente baseado no envio)
        df_latest = df.sort_values('Data_Envio', ascending=False).drop_duplicates('Hardware_Hash', keep='first')
        
        # Se a coluna Nome_Cliente não existir (planilha ainda não alterada), preenche com o Hash
        if 'Nome_Cliente' not in df_latest.columns:
            df_latest['Nome_Cliente'] = df_latest['Hardware_Hash']
            
        return df_latest
    except Exception as e:
        st.error(f"Erro ao carregar dados da nuvem: {e}")
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
    c1.metric("Clientes Monitorados", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta_color="inverse")

    st.divider()

    # Tabela formatada
    st.subheader("📋 Status dos Clientes")
    
    # Colunas para exibição (Nome do Cliente agora vem da planilha)
    cols_view = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash']
    
    # Garante que todas as colunas de visualização existem
    cols_to_show = [c for c in cols_view if c in df_clientes.columns]
    
    def highlight_rows(row):
        is_late = pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < limite
        is_error = str(row.Status).upper() == "ERRO"
        if is_late or is_error:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df_clientes[cols_to_show].style.apply(highlight_rows, axis=1),
        use_container_width=True
    )
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Aguardando o recebimento de dados ou verificação do link da planilha.")
