# proxmox server
node = "pve-m01"
server = "10.20.82.250"
hostname = "rackone.prova"
private_key_path = "main_project/id_ed25519"
public_key_path = "main_project/id_ed25519.pub"
# API Token !!Manage Carefully!!
API_TOKEN = 'PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d'
headers = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}