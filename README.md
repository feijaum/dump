📊 BACKUP DOS CLIENTES

Este projeto é uma solução de monitorização centralizada para backups distribuídos em diversos servidores Windows. O sistema identifica o ficheiro de backup mais recente, gera um ID único para cada cliente e envia os dados para uma Planilha Google, que é visualizada através de um dashboard em Streamlit.

🚀 Funcionalidades Principais

Serviço Silencioso: Corre em segundo plano como um Serviço do Windows (24/7).

ID Único por Hardware: Utiliza um Hash de hardware (Placa-mãe, Disco e Rede) para identificar o cliente sem necessidade de login.

Intervalo de Monitorização: Verifica a pasta de backup a cada 1 hora.

Dashboard Visual: Classificação automática por cores (Verde, Amarelo e Vermelho) baseada na urgência do backup.

Identificação Manual: Permite que escreva o nome do cliente diretamente na Planilha Google para que apareça no Dashboard.

📁 Estrutura de Arquivos

backup_monitor.py: Contém a lógica principal (procurar ficheiros "dump" e enviar para o Google).

service_installer.py: Script que instala e configura o serviço no Windows.

app_streamlit.py: Código do painel visual para o seu computador/servidor.

ver_hash.py: Utilitário para descobrir o ID de um cliente antes da instalação.

compilar.bat: Automatiza a criação do executável (.exe).

🛠️ Requisitos (Para o Desenvolvedor)

Antes de começar, certifique-se de que tem o Python 3.10+ instalado e as bibliotecas necessárias:

pip install wmi requests pywin32 pyinstaller pandas streamlit


📦 1. Como Criar o Instalador (.exe)

Coloque os ficheiros backup_monitor.py, service_installer.py e compilar.bat na mesma pasta.

Execute o ficheiro compilar.bat.

Aguarde o processo terminar. O instalador final estará dentro da pasta dist/service_installer.exe.

🔧 2. Instalação no Cliente

Siga estes passos em cada servidor de cliente:

Copie o ficheiro service_installer.exe para uma pasta permanente (ex: C:\MonitorBackup).

Abra o Prompt de Comando (CMD) como Administrador.

Navegue até à pasta e instale o serviço:

service_installer.exe install


O programa perguntará o caminho da pasta de backup. Cole o caminho completo e pressione Enter.

Inicie o serviço:

service_installer.exe start


Dica: Se quiser saber o ID do cliente antes de instalar, use o ver_hash.bat.

📈 3. O Dashboard (Streamlit)

Para monitorizar os seus clientes, execute no seu computador:

streamlit run app_streamlit.py


Regras de Cores do Painel:

🟢 Branco/Verde: Backup realizado hoje. Tudo ok!

🟡 Amarelo: O cliente fez backup ontem, mas ainda não fez (ou não enviou) o de hoje.

🔴 Vermelho (Crítico): Backup mais antigo que ontem ou o serviço reportou um ERRO.

Como nomear os clientes:

Abra a Planilha Google onde os dados estão a cair.

Adicione uma nova coluna chamada "Nome_Cliente" à direita da última coluna.

Escreva o nome da empresa ao lado do Hash correspondente. O Dashboard lerá esta informação automaticamente.

⚙️ Manutenção do Serviço

Comandos úteis via CMD (Administrador) na pasta do cliente:

Parar o serviço: service_installer.exe stop

Iniciar o serviço: service_installer.exe start

Desinstalar/Remover: service_installer.exe remove

Logs de erro: Verifique o ficheiro monitor_service.log na pasta do executável.
