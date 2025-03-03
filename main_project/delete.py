import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
from config import node, server, headers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

# variabile globale 
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
vmid = input("Which VM do you want do delete?: ")
delete = input(f"Are you sure to delete the VM {vmid}? (y/n): ").strip().lower()
while delete not in ('y', 'n'):
    delete = input("Expected values '(y/n)': ").strip().lower()
if delete == 'y':
    deleteVM()
else:
    print("VM not deleted")
