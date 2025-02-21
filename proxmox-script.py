import requests

node = "pve-m01"
# API Token !!Manage Carefully!!
headers = {
    'Authorization': 'PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d',
    'Content-Type': 'application/json'
}

step = 0
# Clone VM from template
# Get already used VM id
url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu"
response = requests.get(url, headers=headers, verify=False)
if response.status_code == 200:
    vm_list = response.json()['data']
    vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid']]
    #print("VMIDs:", vm_ids)
else:
    print(f"Error {response.status_code}: {response.text}")
vmid = 100
while vmid in vm_ids:  # Se vmid è già nella lista, incrementalo
    vmid += 1
# Clone VM
templateId = (input("Enter the template VM ID: "))
url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu/{templateId}/clone"
data = {
    "newid": vmid
}
response = requests.post(url, headers=headers, json=data, verify=False)
if response.status_code == 200:
    print("VM cloned successfully")
    step = 1
else:
    print("VM clone failed")
    print(response.text)

#Resize disk
if step == 1:
    data = {
    "disk": "scsi0",
    "size": "+10G"
    }
    url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu/{vmid}/resize"
    response = requests.put(url, headers=headers, json=data, verify=False)
    if response.status_code == 200:
        print("Disk resized successfully")
    else:
        print("Disk resize failed")

#Delete VM
delete = input("Do you want to delete the VM? (y/n): ")
if delete == 'y':
    url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu/{vmid}"
    response = requests.delete(url, headers=headers, verify=False)
    if response.status_code == 200:
        print("VM deleted successfully")
    else:
        print("VM delete failed")
        print(response.text)
else:
    print("VM not deleted")
