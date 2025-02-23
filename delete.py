import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

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

node = "pve"
server = "192.168.144.128"
base_url = f"https://{server}:8006/api2/json/nodes/{node}"

# API Token !!Manage Carefully!!
#PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84',
    'Content-Type': 'application/json'
}

vmid = input("Quale vm vuoi cancellare?: ")

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