import requests #Permette di fare richieste HTTP
import urllib3 #Permette di disabilitare i warning per i certificati non validi
import urllib.parse #Permette di convertire i caratteri speciali in URL
import paramiko
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disabilita i warning per i certificati non validi

node = "pve"
server = "192.168.144.128"
vmid = 102
# API Token !!Manage Carefully!!
#PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84',
    'Content-Type': 'application/json'
}
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