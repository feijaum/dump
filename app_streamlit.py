import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais e Título do Projeto
st.set_page_config(page_title="BACKUP DOS CLIENTES", page_icon="📊", layout="wide")

st.title("📊 BACKUP DOS CLIENTES - Dashboard")

# --- DICIONÁRIO DE CLIENTES ---
# Edite este dicionário para mapear os Hashes aos nomes reais dos clientes
DICIONARIO_CLIENTES = {
    "exemplo_hash_12345": "Farmácia do João",
    "exemplo_hash_67890": "Mercado Central",
    "HASH_TESTE_A3F58B": "Cliente Teste Matriz"
}

# --- CONEXÃO COM A PLANILHA ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQMAr0iEgRF6pg_wnN9tGFMA9-hKohffXWMhr5IvNjXkxHrs1_u5j22JNuKOII0sQRdGQKT7Fjn-qZS/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        if df.empty: return None

        # Mapeamento por posição para evitar erros de nomes de colunas do Google
        new_cols = ['Data_Envio', 'Hardware_Hash', 'Status', 'Arquivo', 'Data_Backup_Info']
        current_cols = list(df.columns)
        mapping = {current_cols[i]: new_cols[i] for i in range(len(new_cols)) if i < len(current_cols)}
        df = df.rename(columns=mapping)
        
        # Tratamento de Datas
        df['Data_Envio'] = pd.to_datetime(df['Data_Envio'], errors='coerce')
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # REGISTRO ÚNICO POR CLIENTE: 
        # Ordenamos pelo envio mais recente e removemos duplicados do Hash
        df_latest = df.sort_values('Data_Envio', ascending=False).drop_duplicates('Hardware_Hash', keep='first')
        
        # Aplicar o Dicionário de Nomes
        df_latest['Nome_Cliente'] = df_latest['Hardware_Hash'].map(DICIONARIO_CLIENTES).fillna("DESCONHECIDO (Novo Cliente)")
        
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
    c1.metric("Clientes Monitorados", total)
    c2.metric("Backups em Dia", em_dia)
    c3.metric("Clientes em Alerta", atrasados, delta_color="inverse")

    st.divider()

    # Tabela formatada
    st.subheader("📋 Status dos Clientes")
    
    # Reorganizar colunas para o Nome vir primeiro
    cols_view = ['Nome_Cliente', 'Status', 'Arquivo', 'Data_Backup_Info', 'Data_Envio', 'Hardware_Hash']
    
    def highlight_rows(row):
        is_late = pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < limite
        is_error = str(row.Status).upper() == "ERRO"
        if is_late or is_error:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df_clientes[cols_view].style.apply(highlight_rows, axis=1),
        use_container_width=True
    )
    
    if st.button("🔄 Atualizar Painel"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Nenhum dado recebido ainda.")
