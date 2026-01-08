# -*- coding: utf-8 -*-
import wmi
import hashlib

def get_hardware_hash():
    """Gera o identificador único do hardware exatamente como o serviço faz."""
    try:
        c = wmi.WMI()
        uuid = c.Win32_ComputerSystemProduct()[0].UUID
        disk = c.Win32_DiskDrive()[0].SerialNumber.strip()
        net = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)[0].MACAddress
        
        combined = f"UUID:{uuid}-DISK:{disk}-MAC:{net}"
        hex_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return hex_hash
    except Exception as e:
        return f"Erro ao gerar: {e}"

if __name__ == "__main__":
    print("====================================================")
    print("      IDENTIFICADOR DE HARDWARE (HASH ID)")
    print("====================================================")
    print("\nCopie o código abaixo para o seu dicionário de clientes:\n")
    print(f"ID DO CLIENTE: {get_hardware_hash()}")
    print("\n====================================================")
    input("\nPressione ENTER para fechar...")
