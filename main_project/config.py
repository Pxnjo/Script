# proxmox server
node = "pve"
server = "192.168.144.128"
gateway = "192.168.144.2" # gateway delle VM
hostname = "rackone.prova"
private_key_path = "main_project/id_ed25519"
public_key_path = "main_project/id_ed25519.pub"
# API Token !!Manage Carefully!!
API_TOKEN = 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84'
headers = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}