# proxmox server
node = "pve"
server = "10.20.30.40"
hostname = "test.prova"
gateway = "10.20.30.40"
private_key_path = "main_project/id_ed25519"
public_key_path = "main_project/id_ed25519.pub"
# API Token !!Manage Carefully!!
API_TOKEN = 'PVEAPIToken='
headers = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}