import urllib.parse # Permette di convertire i caratteri speciali in URL
import requests # Permette di fare richieste HTTP
import paramiko # Permette di fare connessioni SSH
import urllib3 # Permette di disabilitare i warning per i certificati non validi
import time # Permette di fare pause
import json # Permette di manipolare file json
import sys
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disabilita i warning per i certificati non validi
# Dichiarazione variabili globali
# API Token lavoro PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
# API Token casa PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84
node = "pve-m01" #pve-m01
server = "10.20.82.250" #10.20.82.250/192.168.144.128
base_url = f"https://{server}:8006/api2/json/nodes/{node}"
hostname = "pxnjo.test"
step = 0 # Variabile che aspetta la clonazione della VM per applicare modifiche
# API Token !!Manage Carefully!!
headers = {
    'Authorization': 'PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d',
    'Content-Type': 'application/json'
}
with open("main_project/id_ed25519.pub", "r") as file: # legge la chiave pubblica
    public_key = file.read().strip()
private_key = "main_project/id_ed25519"
client = paramiko.SSHClient() # initializza la connessione SSH
possible_error_message = ['lock', 'unable', 'dpkg:', 'E:', 'e:']
# Gestione errori
def error_handler(response):
    return response.status_code, response.text
# Dichiarazone metodi API
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

# Clone VM from template
def clone_vm():
    # Get first unsed VMid
    vmid = 100 # VMID di partenza
    url = f"{base_url}/qemu"
    response = metodo('get', url, headers)
    if response.status_code == 200:
        vm_list = response.json()['data']
        vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid']]
    else:
        print(f"Error to retrieve vmid: {error_handler(response)}")

    while vmid in vm_ids:  # Se vmid è già nella lista, incrementalo
        vmid += 1
    # Clone VM
    templateId = (input("Enter the template VM ID: "))
    url = f"{base_url}/qemu/{templateId}/clone"
    data = {
        "newid": vmid # VMid della nuova macchina
    }
    response = metodo('post', url, headers, data)
    if response.status_code == 200:
        print(f"VM {vmid} cloned successfully")
        step = 1
        return vmid
    else:
        print(f"VM clone failed: {error_handler(response)}")

#Resize disk
def resize_disk():
    if step == 1:
        data = {
            "disk": "scsi0",
            "size": "+1G"
        }
        url = f"{base_url}/qemu/{vmid}/resize"
        response = metodo('put', url, headers, data)
        if response.status_code == 200:
            print("Disk resized successfully\n- Disk: scsi0\n- Size: +1G")
        else:
            print(f"Disk resize failed: {error_handler(response)}")

#Configure Cloudinit
i = 0
def cloud_init(i, ip=None):
    if i == 0:
        ciuser = 'test'
        ipconfig0 = f"ip={ip}/8,gw=10.0.1.100"
        data = {
            "ciuser": "test",
            "cipassword": "Vmware1!",
            "sshkeys": public_key,
            "ipconfig0": ipconfig0
        }
    elif i == 1:
        ciuser = 'root'
        ipconfig0 = f"ip={ip}/8,gw=10.0.1.100"
        data = {
            "ciuser": "root",
            "cipassword": "Vmware1!",
            "sshkeys": public_key,
            "ipconfig0": ipconfig0
        }
    else:
        print("Valore di 'i' non valido. Usa 0 o 1.")
        return  # Esce dalla funzione se i non è né 0 né 1
    
    # Codifica la chiave SSH per l'URL
    data["sshkeys"] = urllib.parse.quote(data["sshkeys"])

    # Invio della richiesta API
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)

    # Controllo del risultato
    if response.status_code == 200:
        print(f"Cloudinit configured successfully\n-User: {ciuser}\n-Password: Vmware1!\n-sshkey: {public_key}\n-ip: {ipconfig0}")
        i += i
        return True, ciuser
    else:
        print(f"Cloudinit configuration failed: {error_handler(response)}")

# set dns domain/server
def dns_set():
    data = {
        "searchdomain": "8.8.8.8",
        "nameserver": "8.8.4.4"
    }
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        print(f"Dns set successfully:\n-Search_domain: {data['searchdomain']}\n-Nameserver: {data['nameserver']}")
    else:
        print(f"Dns set failed: {error_handler(response)}")

# set hostname
def set_hostname():
    data = {
        "name": hostname
    }
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        print(f"Hostname set successfully: {data['name']}")
        return data['name']
    else:
        print(f"Hostname set failed: {error_handler(response)}")

def check_xterm_js():
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('get', url, headers)
    status = response.json()['data']
    if 'serial0' in status:
        print(f"Xterm.js serial port found: {response.json()['data']['serial0']}")
    else:
        print(f"Xterm.js serial port not found: {error_handler(response)}")

# Start VM
def start_vm():
    url = f"{base_url}/qemu/{vmid}/status/start"
    response = metodo('post',  url, headers, data={}) # proxmox si aspetta un json anche se vuoto
    if response.status_code == 200:
        print(f"VM {vmid} started successfully")
    else:
        print(f"VM {vmid} start failed: {error_handler(response)}")

# Get VM IP
def get_IPvm():
    while True:
        url = f"{base_url}/qemu/{vmid}/agent/network-get-interfaces"
        response = metodo('get', url, headers)
        #print(response.json())
        if response.status_code != 200 or response.json()['data']['result'][1] is None or 'ip-addresses' not in response.json()['data']['result'][1]: # Se non trova l'ip riprova
            time.sleep(10)
        elif response.json()['data']['result'][1]['ip-addresses'][0]['ip-address-type'] != 'ipv4': # Se l'ip è vuoto riprova
            time.sleep(5)
        else:
            ip_addr = response.json()['data']['result'][1]['ip-addresses'][0]['ip-address']
            print(f'L\'ip della nuova VM è: {ip_addr}')
            return ip_addr

# Check runlevel
def runlevel():
    while True:
        stdin, stdout, stderr = client.exec_command("runlevel | cut -d ' ' -f2")
        output = stdout.read().decode('utf-8').strip()
        if output.isdigit():  # Controlla se l'output è un numero
            output = int(output)  # Converte in intero
            if output < 3:
                continue  # Riprova finché il runlevel è inferiore a 3
            else:
                break  # Esce quando il runlevel è 3 o superiore
        else:
            print(f"Valore inatteso per runlevel: '{output}'")  # Debug in caso di errore
            break  # Esce se il valore non è valido

# SSH connection
def ssh():
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accetta la chiave pubblica del server se non presente nel known_hosts
    hostname = ip_addr
    port = 22
    username = user
    password = 'Vmware1!'
    client.connect(hostname, port=port, username=username, password=password)

# SSH connection with private key
def ssh_key():
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accetta la chiave pubblica del server se non presente nel known_hosts
    hostname = ip_addr
    port = 22
    username = user
    max_retries = 5  # Numero massimo di tentativi
    attempt = 0  # Contatore dei tentativi
    while attempt < max_retries:
        try:
            client.connect(hostname, port=port, username=username, key_filename=private_key)
            print(f"User '{username}' logged in successfully with the key") # il print verrà eseguito solo se la connessione ssh riesce perchè il try in caso di errore passa direttamente dal except
            break
        except paramiko.ssh_exception.AuthenticationException as auth_error:
            print(f"- User '{username}' authentication failed: {auth_error}")
            break
        except paramiko.ssh_exception.SSHException as ssh_error:
            print(f"SSH error: {ssh_error}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
        attempt += 1
        print(f"Retrying... Attempt {attempt} of {max_retries}")
        time.sleep(10)
    else: 
        print(f"Failed to connect to {hostname} after {max_retries} attempts")
    client.close()  # Chiudi la connessione SSH
    client.get_host_keys().clear()  # Rimuove tutte le chiavi host per evitare conflitti

# ping check
def ping(client, timeout=30):
    stdin, stdout, stderr = client.exec_command("ping -c 4 8.8.8.8")
    output = stdout.read().decode('utf-8')
    if 'time=' in output:
        return "Ping succeeded"
    else: 
        return "Ping failed"

# check bios or uefi mode
def check_bios_mode():
    stdin, stdout, stderr = client.exec_command("cd /sys/firmware/efi")
    output = stdout.read().decode('utf-8')
    stderr = stderr.read().decode('utf-8')
    if stderr == '':
        print("Uefi mode")
    else:
        print("Bios mode")

# check disk size
def check_resized_disk():
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('get', url, headers)
    if response.status_code == 200:
        disk_info = response.json()['data']['scsi0']
        match = re.search(r'size=(\d+G)', disk_info)
        # Se non trovi la dimensione in G, cerca quella in M (MB)
        if not match:
            match = re.search(r'size=(\d+)(M)', disk_info) # se la dimensione in proxmox è in MB fa un altro check
            if match:
                disk_size = round(float(match.group(1))/ 1024, 1) # Converti da MB a GB e arrotonda di un numero dopo la virgola
        else:
            disk_size = match.group(1)  # Dimensione in G
        stdin, stdout, stderr = client.exec_command("lsblk -o NAME,SIZE | grep sda | head -n 1")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if str(disk_size) in output:
            print(f"Disk size matches with proxmox: {disk_size}")
        else:
            print(f"Disk size does not match with proxmox: {disk_size}, error: {error}")
    else:
        print(f"Disk size not found {disk_info}")

# chech hostname
def check_hostname():
    stdin, stdout, stderr = client.exec_command("hostname -f")
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8')
    if hostname in output:
        print(f"Hostname matches with proxmox: {hostname}")
    else:
        print(f"Hostname does not match with proxmox: {hostname}, error: {error}")

# chech fstrim
def check_fstrim():
    stdin, stdout, stderr = client.exec_command("systemctl status fstrim.timer | grep \"Active:\" | awk '{print $2}'")
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8')
    if error == '':
        print(f"Fstrim status: {output}")
    else:
        print(f"Fstrim status error: {error}")

# Check comando per aggiornamenti
def check_comando_aggiornamenti(OS):
    OS = OS.strip()
    # Apri il file JSON in modalità lettura ('r')
    with open('main_project/os_list.json', 'r', encoding="utf-8") as file:
        OS_list = json.load(file)  # Carica il contenuto del file JSON in una variabile Python
    for item in OS_list:
        if any(OS in distro for distro in item['distro']): # controlla se OS è contenuto in una stringa della lista
            update_command = item['update_command'] # cerca qual'è il comando per fare l'aggiornamento
            error_sudo = item['error_missing_sudo'] # controlla in base alla distribuzione se vengono richiesti i permessi di sudo
            #print(f"OS: {OS} + {update_command}")
            return update_command, error_sudo
    print("OS non trovato!")  # Debug se non trova nulla
    return None, None  # Se non trova nulla, restituisce None

# check OS
def check_OS():
    stdin, stdout, stderr = client.exec_command("grep '^ID=' /etc/os-release | cut -d '=' -f2")
    output = stdout.read().decode('utf-8').replace('"', '').strip() # rimuove le virgolette di alcuni sistemi operativi
    error = stderr.read().decode('utf-8')
    update_command, error_sudo = check_comando_aggiornamenti(output)
    if update_command is None:
        return None, None
    return update_command, error_sudo

# aggiornamenti 
def aggiornamento():
    update_command, error_sudo = check_OS()
    if update_command is None:
        print("Cannot perform update: OS not found")
        return # esci subito dalla funzione se l'OS non è trovato
    max_retries = 3  # numero massimo di tentativi
    attempts = 0  # inizializza il contatore dei tentativi
    while attempts < max_retries:
        time.sleep(10)
        stdin, stdout, stderr = client.exec_command(f'sudo -S {update_command} update -y', get_pty=True)
        stdin.write("Vmware1!\n")
        stdin.flush()

        for line in iter(stdout.readline, ""):
            sys.stdout.write(line)  # Stampa subito ogni riga di output
            sys.stdout.flush()
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if  any(error_msg in output for error_msg in possible_error_message) or any(error_msg in error for error_msg in possible_error_message):
            print(f"Error during update: {error}")
            attempts += 1 
            time.sleep(10)
        if error_sudo in error: # Se il comando viene eseguito troppo presto, l'output verrà vuoto quindi ripete il comando
            stdin.write("Vmware1!\n")
            stdin.flush()
        else:
            print("Update completed successfully")
            break
    if attempts == max_retries:  # Se il numero massimo di tentativi è stato raggiunto
        print(f"Errore nell'aggiornamento dopo {max_retries} tentativi.")

# check cloud-init.target verificha che cloud-init abbia finito di inizializzare la Vm
def check_cloud_init(timeout=300):
    output = ''
    start_time = time.time()  # Registra l'ora di inizio
    while output != 'active':
        stdin, stdout, stderr = client.exec_command("systemctl status cloud-init.target | grep \"Active:\" | awk '{print $2}'")
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8')
        if error:
            print(f"Error: {stderr}")
            break
        if time.time() - start_time > timeout:
            print("Cloud-init timeout after 5 minutes: try to manually update the VM")
            break
        time.sleep(5)
    if output == 'active':
        print("Cloud-init finished")
        aggiornamento()

# Stop VM
def stopVM():
    url = f"{base_url}/qemu/{vmid}/status/current"
    response = metodo('get', url, headers)
    status = response.json()['data']['status'] # Filtro per ottenere solo lo status
    if status == 'stopped':
        print(f"VM {vmid} stopped successfully")
        return True
    else:
        url = f"{base_url}/qemu/{vmid}/status/stop"
        response = metodo('post', url, headers, data={}) # proxmox si aspetta un json anche se vuoto
        stopVM()

# Delete VM
def deleteVM():
    url = f"{base_url}/qemu/{vmid}/status/current"
    response = metodo('get', url, headers)
    status = response.json()['data']['status'] # Filtro per ottenere solo lo status
    if status == 'stopped':
        url = f"{base_url}/qemu/{vmid}"
        response = metodo('delete', url, headers)
        if response.status_code == 200:
            print(f"VM {vmid} deleted successfully")
        else:
            print(f"VM {vmid} delete failed: {error_handler(response)}")
    else:
        url = f"{base_url}/qemu/{vmid}/status/stop"
        response = metodo('post', url, headers, data={}) # proxmox si aspetta un json anche se vuoto
        deleteVM()
# request to delete VM
def request_deleteVM():
    delete = input("Do you want to delete the VM? (y/n): ").strip().lower()
    while delete not in ('y', 'n'):
        delete = input("Expected values '(y/n)': ").strip().lower()
    if delete == 'y':
        deleteVM()
    else:
        print("VM not deleted")

ip_addr = '10.20.83.215'
vmid = clone_vm() # definisce il primo vmid disponibile
resize_disk() # fa il resize del disco su proxmox
set_hostname() # imposta l'hostname
check_xterm_js() # fa il controllo se la porta seriale è presente sulla configurazione della macchina
dns_set() # imposta il domain server e il nameserver
i, user = cloud_init(i, ip_addr) # imposta cloud init con dhcp/user

start_vm() # fa partire la vm
ip_addr = get_IPvm() # trova l'ip asegnato da dhcp
ssh_key() # test connessione ssh user con chiave privata
ssh() # crea una connessione ssh
print(f"DHCP: {ping(client)}") # risultato test config DHCP
client.close() # chiute la connessione ssh
client.get_host_keys().clear()  # Rimuove tutte le chiavi host
stopVM() # ferma la VM

i, user = cloud_init(i, ip_addr) # cambia il cloud init con IPV4 ricevuto prima da dhcp \ i permette di cambiare 
start_vm() # fa ripartire la VM
ssh_key() # test connessione ssh root con chiave privata
ssh() # crea una connessione ssh
print(f"IPV4 Static: {ping(client)}") # risultato test config IPV4
check_bios_mode() # fa il check se la macchina è in bios o in uefi mode
check_resized_disk() # verifica l'efettivo ridimensionamento del disco
check_hostname() # comara l'hostname impostato su proxmox con quello efettivo nella macchina
check_fstrim() # lancia il comando fstrim per liberare spazio
runlevel() # serve a capire a che livello di avvio si trova la macchina per capire se proseguire con l'update
check_cloud_init() # cerca prima se cloud-init ha finito di inizializzare la VM, poi cerca il sistema operativo, poi cerca di aggiornare i pacchetti
client.close()
request_deleteVM() # richiesta per eliminare la VM una volta eseguiti tutti i test