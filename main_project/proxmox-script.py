import urllib.parse # Permette di convertire i caratteri speciali in URL
import requests # Permette di fare richieste HTTP
import paramiko # Permette di fare connessioni SSH
import logging # permette di fare i log
import urllib3 # Permette di disabilitare i warning per i certificati non validi
import time # Permette di fare pause
import json # Permette di manipolare file json
import sys
import re
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from config import node, server, gateway, headers, hostname, private_key_path, public_key_path
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disabilita i warning per i certificati non validi
console = Console()

# Dichiarazione variabili globali
base_url = f"https://{server}:8006/api2/json/nodes/{node}"
with open(public_key_path, "r") as file: # legge la chiave pubblica
    public_key = file.read().strip()

client = paramiko.SSHClient() # initializza la connessione SSH
possible_error_message = ['lock', 'unable', 'dpkg:', 'E:', 'e:', 'Error', 'error']

# Gestione errori
def describe_errors(response):
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
def clone_vm(templateId):
    # Get first unsed VMid
    vmid = 100 # VMID di partenza
    url = f"{base_url}/qemu"
    response = metodo('get', url, headers)
    if response.status_code == 200:
        vm_list = response.json()['data']
        vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid']]
    else:
        console.print(f"[bold red]❌ Error to retrieve vmid:[/bold red] {describe_errors(response)}")

    while vmid in vm_ids:  # Se vmid è già nella lista, incrementalo
        vmid += 1
    # Clone VM
    url = f"{base_url}/qemu/{templateId}/clone"
    data = {
        "newid": vmid # VMid della nuova macchina
    }
    response = metodo('post', url, headers, data)
    if response.status_code == 200:
        console.print(f"[bold green]✅ VM {vmid} cloned successfully[/bold green]")
        return vmid
    else:
        console.print(f"[bold red]❌ VM clone failed:[/bold red] {describe_errors(response)}")
        return

#Resize disk
def resize_disk(check_if_cloned): #si assicura che la macchina sia clonata prima di fare il resize del disk
    if check_if_cloned is not None:
        data = {
            "disk": "scsi0",
            "size": "+5G"
        }
        url = f"{base_url}/qemu/{vmid}/resize"
        response = metodo('put', url, headers, data)
        if response.status_code == 200:
            console.print(f"[green]✔ Disk resized successfully[/green]")
            print(f"  {Fore.BLUE}|-- Disk:{Style.RESET_ALL} {data['disk']}")
            print(f"  {Fore.BLUE}|-- Size:{Style.RESET_ALL} {data['size']}")
        else:
            print(f"Disk resize failed: {describe_errors(response)}")

#Configure Cloudinit
def cloud_init(i, ip=None):
    if i == 0:
        ciuser = 'test'
        ipconfig0 = "DHCP"
        data = {
            "ciuser": "test",
            "cipassword": "Vmware1!",
            "sshkeys": public_key,
            "ipconfig0": "ip=dhcp",
            "searchdomain": "8.8.8.8",
            "nameserver": "8.8.4.4"
        }
    elif i == 1:
        ciuser = 'root'
        ipconfig0 = f"ip={ip}/24,gw={gateway}"
        data = {
            "ciuser": "root",
            "cipassword": "Vmware1!",
            "sshkeys": public_key,
            "ipconfig0": ipconfig0,
            "searchdomain": "8.8.8.8",
            "nameserver": "8.8.4.4"
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
        table = Table(title="Cloud-init Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("User", ciuser)
        table.add_row("Password", "******")  # Maschera password
        table.add_row("DNS Domain", data['searchdomain'])
        table.add_row("Nameserver", data['nameserver'])
        table.add_row("SSH Key", "[dim]ssh-ed25519 AAAA...CBN[/dim]")
        table.add_row("IP", ipconfig0)
        console.print(table)
        i += 1
        return True, ciuser
    else:
        console.print(f"[bold red]❌ Cloudinit configuration failed:[/bold red] {describe_errors(response)}")


#delete efi disk
def delete_efi_disk():
    data = {
        "delete":"efidisk0"
    }
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        console.print(f"[bold green]✔ EFI disk delete successfully[/bold green]")
    else:
        console.print(f"[bold red]❌ EFI disk delete failed:[/bold red] {describe_errors(response)}")

# set hostname
def set_hostname():
    data = {
        "name": hostname
    }
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        console.print(f"[bold green]✔ Hostname set successfully:[/bold green] {data['name']}")
        return data['name']
    else:
        console.print(f"[bold red]❌ Hostname set failed:[/bold red] {describe_errors(response)}")

#check xterm.js
def check_xterm_js():
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('get', url, headers)
    status = response.json()['data']
    if 'serial0' in status:
        console.print(f"[bold green]✔ Xterm.js serial port found:[/bold green] {response.json()['data']['serial0']}")
    else:
        console.print(f"[bold red]❌ Xterm.js serial port not found[/bold red]")

# Start VM
def start_vm():
    url = f"{base_url}/qemu/{vmid}/status/start"
    response = metodo('post',  url, headers, data={}) # proxmox si aspetta un json anche se vuoto
    if response.status_code == 200:
        console.print(f"[bold green]✅ VM {vmid} started successfully[/bold green]")
    else:
        console.print(f"[bold red]❌ VM {vmid} start failed:[/bold red] {describe_errors(response)}")

# Get VM IP
def get_IPvm(boot_counter = None, timeout=120):
    global ip_addr # variabile temporanea al posto del dhcp
    start_time = time.time()  # Registra l'ora di inizio
    while True:
        url = f"{base_url}/qemu/{vmid}/agent/network-get-interfaces"
        response = metodo('get', url, headers)
        if response.status_code != 200 or response.json()['data']['result'][1] is None or 'ip-addresses' not in response.json()['data']['result'][1]: # Se non trova la scritta ip-addresses riprova
            time.sleep(10)
        elif response.json()['data']['result'][1]['ip-addresses'][0]['ip-address-type'] != 'ipv4': # Se ip-addresses esiste ma l'ip è vuoto riprova
            time.sleep(5)
        else:
            ip_addr = response.json()['data']['result'][1]['ip-addresses'][0]['ip-address']
            console.print(f"[bold yellow]🔍 L'IP della nuova VM è:[/bold yellow] {ip_addr}")
            return ip_addr # se ottengo l'ip address vuol dire che la macchina parte
        if time.time() - start_time > timeout: # timeout se non trova l'ip
            console.print(f"[bold red]❌ Unable to get VM IP after 2min[/bold red]")
            if boot_counter == 0:
                return 1 # se era il primo tentativo di boot in uefi allora ritorna 1 per impostare il boot in bios
            else:
                return 2 # se nemmeno al secondo tentativo non funziona allora la macchina non parte

# set Boot mode in BIOS
def set_boot_mode(boot_counter):
    if boot_counter == 0:
        bios = 'UEFI'
        data = {
            "bios": "ovmf"
        }
    else:
        bios = 'BIOS'
        data = {
            "bios": "seabios"
        }
    url = f"{base_url}/qemu/{vmid}/config"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        console.print(f"[bold green]✔ Boot mode set to {bios} successfully[/bold green]")
        return bios
    else:
        console.print(f"[bold red]❌ Boot mode set to {bios} failed:[/bold red] {describe_errors(response)}")

# SSH connection
def ssh():
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accetta la chiave pubblica del server se non presente nel known_hosts
    hostname = ip_addr
    port = 22
    username = user
    password = 'Vmware1!'
    max_retries = 5  # Numero massimo di tentativi
    attempt = 0  # Contatore dei tentativi
    while attempt < max_retries:
        try:
            client.connect(hostname, port=port, username=username, password=password)
            stdin, stdout, stderr = client.exec_command('whoami')
            output = stdout.read().decode('utf-8').strip()
            console.print(f"[bold green]✔ User '{output}' logged in successfully with password[/bold green]") # il print verrà eseguito solo se la connessione ssh riesce perchè il try in caso di errore passa direttamente dal except
            break
        except paramiko.ssh_exception.AuthenticationException as auth_error:
            console.print(f"[bold red]❌ User '{username}' authentication with password failed:[/bold red] {auth_error}")
            break
        except paramiko.ssh_exception.SSHException as ssh_error:
            console.print(f"[bold red]❌ SSH error:[/bold red] {ssh_error}")
        except Exception as e:
            pass
        attempt += 1
        time.sleep(10)
    else:
        console.print(f"[bold red]❌ Failed to connect with user '{user}' and password to {hostname} after {max_retries} attempts[/bold red]")
    client.close()
    client.get_host_keys().clear()

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
            client.connect(hostname, port=port, username=username, key_filename=private_key_path)
            stdin, stdout, stderr = client.exec_command('whoami')
            output = stdout.read().decode('utf-8').strip()
            console.print(f"[bold green]✔ User '{output}' logged in successfully with the key[/bold green]") # il print verrà eseguito solo se la connessione ssh riesce perchè il try in caso di errore passa direttamente dal except
            break
        except paramiko.ssh_exception.AuthenticationException as auth_error:
            console.print(f"[bold red]❌ User '{username}' authentication failed:[/bold red] {auth_error}")
            break
        except paramiko.ssh_exception.SSHException as ssh_error:
            console.print(f"[bold red]❌ SSH error:[/bold red] {ssh_error}")
        except Exception as e:
            pass
        attempt += 1
        time.sleep(10)
    else: 
        console.print(f"[bold red]❌ Failed to connect with '{user}' and key to {hostname} after {max_retries} attempts[/bold red]")
        return "Unable to continue with tests"

# ping check
def ping(client, timeout=30):
    start_time = time.time() # Registra l'ora di inizio
    stdin, stdout, stderr = client.exec_command("ping -c 4 8.8.8.8")
    while not stdout.channel.exit_status_ready(): # Aspetta che il comando finisca
        if time.time() - start_time > timeout:
            client.exec_command("pkill -f 'ping -c 4 8.8.8.8'") # termina
            return console.print(f"[bold red]❌ Ping timeout[/bold red]")
    output = stdout.read().decode('utf-8')
    if 'time=' in output:
        return "✅ Ping succeeded"
    else: 
        return "❌ Ping failed"

# check bios or uefi mode
def check_boot_mode():
    stdin, stdout, stderr = client.exec_command("cd /sys/firmware/efi")
    output = stdout.read().decode('utf-8')
    stderr = stderr.read().decode('utf-8')
    if stderr == '':
        console.print(f"[bold cyan]ℹ Boot mode:[/bold cyan] UEFI")
    else:
        console.print(f"[bold cyan]ℹ Boot mode:[/bold cyan] BIOS")

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
            console.print(f"[bold green]✔ Disk size matches with proxmox:[/bold green] {disk_size}")
        else:
            console.print(f"[bold red]❌ Disk size does not match with proxmox:[/bold red] {disk_size}, error: {error}")
    else:
        console.print(f"[bold red]❌ Disk size not found:[/bold red] {disk_size}, {disk_info}")

# chech hostname
def check_hostname():
    stdin, stdout, stderr = client.exec_command('getent hosts | awk /"${HOSTNAME:-${HOST-}}"./\'{print $2}\'')
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8')
    if hostname in output:
        console.print(f"[bold green]✔ Hostname matches with proxmox:[/bold green] {hostname}")
    else:
        console.print(f"[bold red]❌ Hostname does not match with proxmox:[/bold red] {hostname}, error: {error}")

# chech fstrim
def check_fstrim():
    stdin, stdout, stderr = client.exec_command("systemctl status fstrim.timer | grep \"Active:\" | awk '{print $2}'")
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8')
    if error == '':
        console.print(f"[bold green]✔ Fstrim status:[/bold green] {output}")
    else:
        console.print(f"[bold red]❌ Fstrim status error:[/bold red] {error}")

# Check comando per aggiornamenti
def check_comando_aggiornamenti(OS):
    OS = OS.strip()
    # Apri il file JSON in modalità lettura ('r')
    with open('main_project/os_list.json', 'r', encoding="utf-8") as file:
        OS_list = json.load(file)  # Carica il contenuto del file JSON in una variabile Python
    for item in OS_list:
        if any(OS in distro for distro in item['distro']): # controlla se OS è contenuto in una stringa della lista
            update_command = item['update_command'] # cerca qual'è il comando per fare l'aggiornamento
            return update_command
    console.print(f"[bold red]❌ OS non trovato![/bold red]")  # Debug se non trova nulla
    return None  # Se non trova nulla, restituisce None

# check OS
def check_OS():
    stdin, stdout, stderr = client.exec_command("grep '^ID=' /etc/os-release | cut -d '=' -f2")
    output = stdout.read().decode('utf-8').replace('"', '').strip() # rimuove le virgolette di alcuni sistemi operativi
    error = stderr.read().decode('utf-8')
    update_command = check_comando_aggiornamenti(output)
    if update_command is None:
        return None
    return update_command

# Configura il logger per gli errori
error_logger = logging.getLogger('error_logger')
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler('main_project/error_log.txt', mode='w') # logga sovrascrivendo cosa c'era prima
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Configura il logger per gli aggiornamenti (successo)
update_logger = logging.getLogger('update_logger')
update_logger.setLevel(logging.DEBUG)
update_handler = logging.FileHandler('main_project/update_log.txt', mode='w') # logga sovrascrivendo cosa c'era prima
update_handler.setLevel(logging.DEBUG)
update_logger.propagate = False # Evita la propagazione dei log
update_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
update_handler.setFormatter(update_formatter)
update_logger.addHandler(update_handler)

# aggiornamenti 
def aggiornamento():
    update_command = check_OS()
    if update_command is None:
        console.print(f"[bold red]❌ Cannot perform update: OS not found[/bold red]")
        return # esci subito dalla funzione se l'OS non è trovato
    time.sleep(10)
    stdin, stdout, stderr = client.exec_command(update_command)
    output = stdout.read().decode('utf-8').strip()
    error = stderr.read().decode('utf-8').strip()
    update_logger.debug(output) # logga gli aggiornamenti
    if error: 
        error_logger.error(error) # logga gli errori
        console.print(f"[bold red]❌ Errors during update: see 'error_log.txt' for more info[/bold red]") # se presenti degli errori restituisce
    else:
        console.print(f"[bold green]✔ Update finished without errors![/bold green]") # se presenti degli errori restituisce
    if output != '':
         console.print(f"[bold cyan]ℹ To view updates logs see 'update_log.txt' for more info[/bold cyan]")

# check cloud-init.target verificha che cloud-init abbia finito di inizializzare la Vm
def check_cloud_init(timeout=300):
    output = ''
    console.print("[bold yellow]⏳ Waiting for cloud-init to finish...[/bold yellow]")
    start_time = time.time()  # Registra l'ora di inizio
    while output != 'active': # ciclo che aspetta che cloud init finisca la configurazione per passare agli aggiornamenti
        stdin, stdout, stderr = client.exec_command("systemctl status cloud-init.target | grep \"Active:\" | awk '{print $2}'")
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8')
        if error:
            console.print(f"[bold red]❌ Error:[/bold red] {error}")
            break
        if time.time() - start_time > timeout:
            console.print("[bold red]❌ Cloud-init timeout after 5 minutes: try to manually update the VM[/bold red]")
            break
        time.sleep(5)
    if output == 'active':
        console.print("[bold green]✔ Cloud-init finished[/bold green]")
        aggiornamento()

# shutdown VM
def shutdownVM():
    url = f"{base_url}/qemu/{vmid}/status/current"
    response = metodo('get', url, headers)
    status = response.json()['data']['status'] # Filtro per ottenere solo lo status
    if status == 'stopped':
        console.print(f"[bold green]✔ VM {vmid} shutdown successfully[/bold green]")
        return True
    else:
        url = f"{base_url}/qemu/{vmid}/status/shutdown"
        response = metodo('post', url, headers, data={}) # proxmox si aspetta un json anche se vuoto
        shutdownVM()

# stop VM
def stopVM():
    url = f"{base_url}/qemu/{vmid}/status/current"
    response = metodo('get', url, headers)
    status = response.json()['data']['status'] # Filtro per ottenere solo lo status
    if status == 'stopped':
        console.print(f"[bold green]✔ VM {vmid} stopped successfully[/bold green]")
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
            console.print(f"[bold green]✔ VM {vmid} deleted successfully[/bold green]")
        else:
            console.print(f"[bold red]❌ VM {vmid} delete failed:[/bold red] {describe_errors(response)}")
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


#--------------------INIZIO DELLO SCRIPT---------------------------#
# templateId = (input("Enter the template VM ID: "))
if len(sys.argv) > 1:
    templateId = sys.argv[1]  # Prendi il primo argomento passato
    print(f"Template ID ricevuto: {templateId}")
else:
    print("Errore: devi passare un Template ID come parametro!")
    sys.exit(1)  # Esce con errore

boot_counter = 0 # tiene conto di quale boot mode è stato provato
i = 0
ip_addr = ''
console.print(Panel.fit("💻 [cyan]Proxmox VM Deployment[/cyan]", title="🚀 [bold green]Process Started[/bold green]"))
while True:
    vmid = clone_vm(templateId) # definisce il primo vmid disponibile
    if vmid is not None:
        console.print("[bold cyan]-----------------------------[/bold cyan]")
        console.print("[bold yellow]Setting Proxmox configuration[/bold yellow]")
        console.print("[bold cyan]-----------------------------[/bold cyan]")
        resize_disk(vmid) # fa il resize del disco su proxmox
        set_hostname() # imposta l'hostname
        check_xterm_js() # fa il controllo se la porta seriale è presente sulla configurazione della macchina
        if boot_counter == 1:
            delete_efi_disk() # elimina il disco efi quando la vm viene avviata in bios
            i = 0 # reimposta la variabile a di cloud init a 0
        i, user = cloud_init(i) # imposta cloud init con dhcp/user
        boot_mode = set_boot_mode(boot_counter) # la prima volta setta la macchina in uefi mode 
        start_vm() # fa ripartire la VM
        boot_counter = get_IPvm(boot_counter)
        if boot_counter == 1:
            console.print("[bold red]❌ VM doesn't boot in UEFI mode[/bold red]")
            deleteVM()
            continue
        elif boot_counter == 2: # se è uguale a 1 vuol dire che non ha fatto il boot nè in UEFI nè in BIOS
            console.print("[bold red]❌ Unable to continue with tests; the VM doesn't boot in either UEFI or BIOS[/bold red]")
            stopVM()
            break
        else:
            console.print(f"[bold green]✔ VM booted correctly in {boot_mode}[/bold green]")
            if boot_mode == 'UEFI': # solo se la macchina parte in uefi allora la elimina per fare la priva in bios
                boot_counter = 1
                deleteVM()
                continue # torna al inizio del ciclo 

        console.print("[bold cyan]------------------------------------[/bold cyan]")
        console.print("[bold yellow]Checking configuration inside the VM[/bold yellow]")
        console.print("[bold cyan]------------------------------------[/bold cyan]")
        ssh() # fa la prova di connessione ssh con la password di user
        status_ssh = ssh_key() # test connessione ssh user con chiave privata
        console.print(f"[bold green]✔ DHCP:[/bold green] {ping(client)}") # risultato test config DHCP
        client.close() # chiute la connessione ssh
        client.get_host_keys().clear() # Rimuove tutte le chiavi host
        shutdownVM() # ferma la VM
        i, user = cloud_init(i, ip_addr) # cambia il cloud init con IPV4 ricevuto prima da dhcp \ i permette di cambiare 
        start_vm() # fa ripartire la VM
        boot_counter = get_IPvm(1) # al riavvio della macchina se non parte finisce il test
        if boot_counter == 2:
            console.print("[bold red]❌ Unable to continue with tests: VM not booted after reboot[/bold red]")
            stopVM()
            break
        else:
            ssh() # fa la prova di connessione ssh con la password di root
            ssh_key() # test connessione ssh root con chiave privata
            console.print(f"[bold green]✔ IPV4 Static:[/bold green] {ping(client)}") # risultato test config IPV4
            #check_boot_mode() # fa il check se la macchina è in bios o in uefi mode
            check_resized_disk() # verifica l'efettivo ridimensionamento del disco
            check_boot_mode() # verifica dentro la macchina il boot mode
            check_hostname() # comara l'hostname impostato su proxmox con quello efettivo nella macchina
            check_fstrim() # lancia il comando fstrim per liberare spazio
            check_cloud_init() # cerca prima se cloud-init ha finito di inizializzare la VM, poi cerca il sistema operativo, poi cerca di aggiornare i pacchetti
            client.close() # chiute la connessione ssh
            client.get_host_keys().clear() # Rimuove tutte le chiavi host
            stopVM()
        break
    else:
        break