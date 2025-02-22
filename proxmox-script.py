import requests
import urllib3
import urllib.parse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

node = "pve-m01"
server = "10.20.82.250"
# API Token !!Manage Carefully!!

#root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d
headers = {
    'Authorization': 'PVEAPIToken=root@pam!testCasa=1a3ef4e0-412e-405c-be2e-b495f6320b84',
    'Content-Type': 'application/json'
}

def error_handler(response):
    return response.status_code, response.text
    #exit()

step = 0
# Clone VM from template
# Get already used VM id
url = f"https://{server}:8006/api2/json/nodes/{node}/qemu"
response = requests.get(url, headers=headers, verify=False)
if response.status_code == 200:
    vm_list = response.json()['data']
    vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid']]
    #print("VMIDs:", vm_ids)
else:
    print(f"Error to retrieve vmid: {error_handler(response)}")

vmid = 100
while vmid in vm_ids:  # Se vmid è già nella lista, incrementalo
    vmid += 1
# Clone VM
templateId = (input("Enter the template VM ID: "))
url = f"https://{server}:8006/api2/json/nodes/{node}/qemu/{templateId}/clone"
data = {
    "newid": vmid
}
response = requests.post(url, headers=headers, json=data, verify=False)
if response.status_code == 200:
    print("VM cloned successfully")
    step = 1
else:
    print(f"VM clone failed: {error_handler(response)}")

#Resize disk
if step == 1:
    data = {
    "disk": "scsi0",
    "size": "+1G"
    }
    url = f"https://{server}:8006/api2/json/nodes/{node}/qemu/{vmid}/resize"
    response = requests.put(url, headers=headers, json=data, verify=False)
    if response.status_code == 200:
        print("Disk resized successfully")
    else:
        print(f"Disk resize failed: {error_handler(response)}")

#Configure Cloudinit
data = {
    "ciuser": "test",
    "cipassword": "Vmware1!",
    "sshkeys": "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAwrcE2CcP52XWHPB2bR8gK2ONuotiZFXfpl5Cpe+LmZ mmonegroup\\alessandro.custura@MM027"
}
data["cipassword"] = urllib.parse.quote(data["cipassword"])
data["sshkeys"] = urllib.parse.quote(data["sshkeys"])

url = f"https://{server}:8006/api2/json/nodes/{node}/qemu/{vmid}/config"
response = requests.put(url, headers=headers, json=data, verify=False)
if response.status_code == 200:
    print("Cloudinit configured successfully")
else:
    print(f"Cloudinit configuration failed: {error_handler(response)}")

delete = input("Do you want to delete the VM? (y/n): ").strip().lower()
while delete not in ('y', 'n'):
    delete = input("Expected values 'y' or 'n': ").strip().lower()
    
if delete == 'y':
    url = f"https://{server}:8006/api2/json/nodes/{node}/qemu/{vmid}"
    response = requests.delete(url, headers=headers, verify=False)
    if response.status_code == 200:
        print("VM deleted successfully")
    else:
        print(f"VM delete failed: {error_handler(response)}")
else:
    print("VM not deleted")
