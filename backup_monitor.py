# -*- coding: utf-8 -*-
import os
import wmi
import hashlib
import json
import requests
import time
import logging
import sys
from datetime import datetime

# --- CONFIGURAÇÕES DO GOOGLE FORM ---
# URL final obtida do seu HTML
FORM_ACTION_URL = "https://docs.google.com/forms/d/e/1FAIpQLSebyi4xevq1s9PfuzbobRMUoRM_j_BX4SR1fKFCwZAycyYehQ/formResponse"

# IDs das entradas (entries) obtidos do seu HTML
FORM_ENTRY_IDS = {
    "hash": "entry.1076243954",
    "status": "entry.1908981916",
    "filename": "entry.2068928701",
    "file_timestamp": "entry.1321886630"
}

# --- CONFIGURAÇÕES DE BUSCA ---
SEARCH_TERM = "dump"
CHECK_INTERVAL_SECONDS = 3600 # Verifica a cada 1 hora

# Caminhos automáticos baseados na localização do executável
BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
LOG_FILE = os.path.join(BASE_DIR, "monitor_service.log")
CONFIG_FILE = os.path.join(BASE_DIR, "monitor_config.json")

def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s', 
        filename=LOG_FILE, 
        filemode='a'
    )

def load_config():
    """Carrega o caminho da pasta de backup do arquivo JSON"""
    if not os.path.exists(CONFIG_FILE): return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f).get("BACKUP_DIR")
    except: return None

def get_hardware_hash():
    """Gera o identificador unico do hardware"""
    try:
        c = wmi.WMI()
        uuid = c.Win32_ComputerSystemProduct()[0].UUID
        disk = c.Win32_DiskDrive()[0].SerialNumber.strip()
        net = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)[0].MACAddress
        combined = f"UUID:{uuid}-DISK:{disk}-MAC:{net}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    except: return "HASH_DESCONHECIDO"

def find_latest_backup(directory):
    """Procura o arquivo mais recente que contenha 'dump' no nome"""
    latest_file = None
    latest_time = 0
    try:
        if not os.path.exists(directory): return None, None
        for filename in os.listdir(directory):
            if SEARCH_TERM in filename.lower():
                file_path = os.path.join(directory, filename)
                file_time = os.path.getctime(file_path)
                if file_time > latest_time:
                    latest_time = file_time
                    latest_file = file_path
        return latest_file, latest_time
    except: return None, None

def main_task():
    """Executa a rotina de checagem e envio"""
    backup_dir = load_config()
    if not backup_dir: return
    
    hw_hash = get_hardware_hash()
    latest_file, latest_time = find_latest_backup(backup_dir)
    
    status = "OK" if latest_file else "ERRO"
    filename = os.path.basename(latest_file) if latest_file else "Nao encontrado"
    file_ts = datetime.fromtimestamp(latest_time).strftime('%d/%m/%Y %H:%M:%S') if latest_time else "N/A"

    payload = {
        FORM_ENTRY_IDS["hash"]: hw_hash,
        FORM_ENTRY_IDS["status"]: status,
        FORM_ENTRY_IDS["filename"]: filename,
        FORM_ENTRY_IDS["file_timestamp"]: file_ts
    }
    
    try:
        requests.post(FORM_ACTION_URL, data=payload, timeout=20)
    except Exception as e:
        logging.error(f"Erro no envio: {e}")

if __name__ == "__main__":
    setup_logging()
    main_task()
