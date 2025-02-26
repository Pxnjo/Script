import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko
import json
import re
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

node = "pve-m01"
server = "10.20.82.250"
vmid = 101
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

with open("main_project/id_ed25519.pub", "r") as file:
    public_key = file.read().strip()
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

# Start VM
def start_vm():
    url = f"{base_url}/qemu/{vmid}/status/start"
    response = metodo('post',  url, headers, data={}) # proxmox si aspetta un json anche se vuoto
    if response.status_code == 200:
        print(f"VM {vmid} started successfully")
    else:
        print(f"VM {vmid} start failed: {error_handler(response)}")


# SSH connection
client = paramiko.SSHClient()
def ssh():
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Accetta la chiave pubblica del server se non presente nel known_hosts
    hostname = ip_addr
    port = 22
    username = user
    password = 'Vmware1!'
    client.connect(hostname, port=port, username=username, password=password)

# ping check
def ping(client, timeout=30):
    stdin, stdout, stderr = client.exec_command("ping -c 4 8.8.8.8")
    output = stdout.read().decode('utf-8')
    if 'time=' in output:
        print("Ping succeeded")
    else: 
        print("Ping failed")

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
user = 'test'
ip_addr = '10.20.83.215'




