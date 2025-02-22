import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko #Permette di fare connessioni SSH
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

def error_handler(response):
    return response.status_code, response.text
#Dichiarazone metodi
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

#Dichiarazione variabili globali
node = "pve" #pve-m01
server = "192.168.144.128"
base_url = f"https://{server}:8006/api2/json/nodes/{node}"
step = 0 #Variabile che aspetta la clonazione della VM per applicare modifiche

# API Token !!Manage Carefully!!
#PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84',
    'Content-Type': 'application/json'
}

# Clone VM from template
# Get first unsed VMid
url = f"{base_url}/qemu"
response = metodo('get', url, headers)
if response.status_code == 200:
    vm_list = response.json()['data']
    vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid']]
else:
    print(f"Error to retrieve vmid: {error_handler(response)}")

vmid = 100
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
else:
    print(f"VM clone failed: {error_handler(response)}")

#Resize disk
if step == 1:
    data = {
        "disk": "scsi0",
        "size": "+1G"
    }
    url = f"{base_url}/qemu/{vmid}/resize"
    response = metodo('put', url, headers, data)
    if response.status_code == 200:
        print("Disk resized successfully")
    else:
        print(f"Disk resize failed: {error_handler(response)}")

#Configure Cloudinit
data = {
    "ciuser": "test",
    "cipassword": "Vmware1!",
    "sshkeys": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAwrcE2CcP52XWHPB2bR8gK2ONuotiZFXfpl5Cpe+LmZ mmonegroup\\alessandro.custura@MM027",
    "ipconfig0": "ip=dhcp"
}
data["sshkeys"] = urllib.parse.quote(data["sshkeys"])
url = f"{base_url}/qemu/{vmid}/config"
response = metodo('put', url, headers, data)
if response.status_code == 200:
    print("Cloudinit configured successfully")
else:
    print(f"Cloudinit configuration failed: {error_handler(response)}")

# Start VM
url = f"{base_url}/qemu/{vmid}/status/start"
response = metodo('post',  url, headers, data={}) # proxmox si aspetta un json anche se vuoto
if response.status_code == 200:
    print(f"VM {vmid} started successfully")
else:
    print(f"VM {vmid} start failed: {error_handler(response)}")

# SSH connection
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
hostname = '192.168.144.149'
port = 22
username = 'test'
password = 'Vmware1!'
client.connect(hostname, port=port, username=username, password=password)

# Execute command and get output/error
stdin, stdout, stderr = client.exec_command('sudo apt update | grep "All packages are up to date"')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')
error = "\n".join([line for line in error.splitlines() if "WARNING" not in line]) # Rimuove i warning
print(f"questo è l'output: {output}")
print(f"questo è l'errore: {error}")
client.close()


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
#Delete VM
delete = input("Do you want to delete the VM? (y/n): ").strip().lower()
while delete not in ('y', 'n'):
    delete = input("Expected values '(y/n)': ").strip().lower()
if delete == 'y':
    deleteVM()
else:
    print("VM not deleted")
