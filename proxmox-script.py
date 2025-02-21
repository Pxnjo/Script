import requests
from proxmoxer import ProxmoxAPI

proxmox = ProxmoxAPI('10.20.82.250', user='root@pam', password='foobar', verify_ssl=False)
print(proxmox)













# url = "https://10.20.82.250:8006/api2/json/nodes/pve-m01/qemu/100/status/start"
# headers = {
#     'Authorization': 'PVEAPIToken=root@pam!testVM=3738178e-0d67-495c-ac89-e9eb3eff565b',
#     "Content-Type": "application/json"
# }
# response = requests.post(url, headers=headers, verify=False)

# if response.status_code == 200:
#     print("VM started successfully")
# else:
#     print(response)
#     print("Failed to start VM")



