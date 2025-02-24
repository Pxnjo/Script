import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

node = "pve-m01"
server = "10.20.82.250"
vmid = 100
# API Token !!Manage Carefully!!
#PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d',
    'Content-Type': 'application/json'
}
base_url = f"https://{server}:8006/api2/json/nodes/{node}"
def error_handler(response):
    return response.status_code, response.text
def metodo(type, url, headers, data=None):
            if type == 'get':
                response = requests.get(url, headers=headers, verify=False)
            elif type == 'post':
                response = requests.post(url, headers=headers, json=data, verify=False)
            elif type == 'put':
                response = requests.put(url, headers=headers, json=data, verify=False)
            elif type == 'delete':
                response = requests.delete(url, headers=headers, verify=False)
            return response
def check_comando_aggiornamenti(OS):
    OS = OS.strip()
    print(f"OS: {OS}")
    # Apri il file JSON in modalità lettura ('r')
    with open('main_project/os_list.json', 'r', encoding="utf-8") as file:
        OS_list = json.load(file)  # Carica il contenuto del file JSON in una variabile Python
    for item in OS_list:
        #print(f"Analizzando: {item}")  # Debug: stampa il dizionario che sta analizzando
        if OS in item['distro']:
            update = item['update_command']
            error_sudo = item['error_missing_sudo']
            return update, error_sudo
    print("OS non trovato!")  # Debug se non trova nulla
    return None  # Se non trova nulla, restituisce None

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accetta la chiave pubblica del server se non presente nel known_hosts
hostname = '10.20.83.193'
port = 22
username = 'test'
password = 'Vmware1!'
client.connect(hostname, port=port, username=username, password=password)

# Check OS
stdin, stdout, stderr = client.exec_command("head -n 1 /etc/os-release | cut -d '\"' -f2")
output = stdout.read().decode('utf-8')
stderr = stderr.read().decode('utf-8')

update, error_sudo = check_comando_aggiornamenti(output)
# aggiornamenti
while True:
    stdin, stdout, stderr = client.exec_command(f'sudo -S {update} update ')
    stdin.write("Vmware1!\n")
    stdin.flush()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if error_sudo in error: # Se il comando viene eseguito troppo presto, l'output verrà vuoto quindi ripete il comando
        stdin.write("Vmware1!\n")
        stdin.flush()
    else:
        break

# Check updates
print("Output degli aggiornamenti:")
for line in output.split('\n'):
    if line != '':
        print(f"- {line}")
if error != '' and error_sudo not in error and 'WARNING' not in error:
    print(f"Output di errore degli aggiornamenti: {error}")
client.close()