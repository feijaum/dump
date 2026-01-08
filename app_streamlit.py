
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configurações Visuais
st.set_page_config(page_title="Monitor de Backups", page_icon="📈", layout="wide")

st.title("📈 Dashboard de Monitoramento de Backups")
st.markdown("Acompanhamento centralizado de todos os clientes.")

# --- LINK DA PLANILHA (CSV) ---
# Importante: No Google Sheets, use Arquivo > Compartilhar > Publicar na Web > CSV
CSV_URL = "COLE_AQUI_O_LINK_DO_SEU_CSV"

@st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos
def load_data():
    if CSV_URL == "COLE_AQUI_O_LINK_DO_SEU_CSV":
        return None
    try:
        df = pd.read_csv(CSV_URL)
        # Renomeia colunas para facilitar (ajuste conforme a ordem da sua planilha)
        df.columns = ['Data_Registro', 'Hardware_Hash', 'Status', 'Nome_Arquivo', 'Data_Backup_Info']
        
        # Converte strings de data para objetos datetime
        df['Data_Registro'] = pd.to_datetime(df['Data_Registro'], errors='coerce')
        df['Data_Backup_DT'] = pd.to_datetime(df['Data_Backup_Info'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
        
        # Pega apenas o registro mais recente de cada cliente (Hardware Hash)
        df_latest = df.sort_values('Data_Registro').drop_duplicates('Hardware_Hash', keep='last')
        return df_latest
    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
        return None

df_clientes = load_data()

if df_clientes is not None:
    # Métricas
    agora = datetime.now()
    prazo = agora - timedelta(hours=24)
    
    total = len(df_clientes)
    em_dia = len(df_clientes[df_clientes['Data_Backup_DT'] > prazo])
    atrasados = total - em_dia

    m1, m2, m3 = st.columns(3)
    m1.metric("Total de Clientes", total)
    m2.metric("Backups em Dia (24h)", em_dia)
    m3.metric("Clientes em Alerta", atrasados, delta=f"{atrasados} Críticos", delta_color="inverse")

    st.divider()

    # Tabela com destaque para atrasados
    st.subheader("Lista de Dispositivos")
    
    def highlight_late(row):
        # Se o backup for mais antigo que 24h, pinta de vermelho
        if pd.isna(row.Data_Backup_DT) or row.Data_Backup_DT < prazo:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    st.dataframe(
        df_clientes.style.apply(highlight_late, axis=1),
        use_container_width=True
    )
    
    if st.button("Recarregar Dados"):
        st.rerun()
else:
    st.warning("⚠️ O link do CSV da Planilha ainda não foi configurado no arquivo app_streamlit.py.")
    st.info("Siga as instruções no README para publicar sua planilha do Google.")
