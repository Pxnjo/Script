import requests

node = "pve-m01"
# API Token
headers = {
    'Authorization': 'PVEAPIToken=root@pam!pxnjoToken=47e7e567-d637-4146-b097-f78fbdd14c7d',
    'Content-Type': 'application/json'
}

# Clone VM from template
# Get already used VM id
url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu"
response = requests.get(url, headers=headers, verify=False)
if response.status_code == 200:
    vm_list = response.json()['data']
    vm_ids = [vm['vmid'] for vm in vm_list if vm['vmid'] < 10000]
    #print("VMIDs:", vm_ids)
else:
    print(f"Error {response.status_code}: {response.text}")
newid = 100
while newid in vm_ids:  # Se newid è già nella lista, incrementalo
    newid += 1
# Clone VM
templateId = (input("Enter the template VM ID: "))
url = f"https://10.20.82.250:8006/api2/json/nodes/{node}/qemu/{templateId}/clone"
data = {
    "newid": newid
}
response = requests.post(url, headers=headers, json=data, verify=False)
if response.status_code == 200:
    print("VM cloned successfully")
else:
    print("VM clone failed")
    print(response.text)


#Resize disk
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
