import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

<<<<<<< HEAD
node = "pve"
server = "192.168.144.128"
=======
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
>>>>>>> test
vmid = 102
# API Token !!Manage Carefully!!
#PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84',
    'Content-Type': 'application/json'
}
<<<<<<< HEAD
def error_handler(response):
    return response.status_code, response.text

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
error = "\n".join([line for line in error.splitlines() if "WARNING" not in line])
print(f"questo è l'output: {output}")
print(f"questo è l'errore: {error}")
client.close()
=======

url = f"{base_url}/qemu/{vmid}/agent/network-get-interfaces"
response = metodo('get', url, headers)
risposta = response.json()['data']['result'][1]['ip-addresses'][0]['ip-address']
print(risposta)




# SSH connection
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# hostname = '192.168.144.149'
# port = 22
# username = 'test'
# password = 'Vmware1!'

# client.connect(hostname, port=port, username=username, password=password)

# # Execute command and get output/error
# stdin, stdout, stderr = client.exec_command('sudo apt update | grep "All packages are up to date"')
# output = stdout.read().decode('utf-8')
# error = stderr.read().decode('utf-8')
# error = "\n".join([line for line in error.splitlines() if "WARNING" not in line])
# print(f"questo è l'output: {output}")
# print(f"questo è l'errore: {error}")
# client.close()
>>>>>>> test
