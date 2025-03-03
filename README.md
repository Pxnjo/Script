# Proxmox Test Automation Script
## Description
This script is designed to automate a series of tests to be performed on new distributions or updates released, verifying that the changes made by Proxmox are effective within the machine. Note: The script works only on Linux distributions.
The 'nice' branch differs only in the output, which has been made more readable and colorful. However, please be aware that there could be incompatibilities in case of automations.

## Configuration
Before running the script, you need to configure a few files:

### config.py:
This is the first file to modify. You will need to update all the parameters to suit your environment.

- **API_TOKEN**: The tests were performed using a token with maximum authorization levels. It is unclear exactly which permissions are needed, so you might want to create a token with root privileges if you don’t have other indications.
- **Public and private keys**: These can remain the default ones unless you want to test compatibility with more sophisticated keys.
- **Cloud-init**: This is quite delicate. Make sure the public key is formatted correctly (with the specific spaces) and, if possible, keep the same file name.
### os_list.json:
Check that the distribution is present in this file. It is recommended to write the distribution name in lowercase for safety.

## Execution Modes
The script can be run in two modes, and in both cases, it expects a parameter, for example:
```
python3 script.py 100010
```
The number passed (e.g., 100010) corresponds to the ID of the template you wish to test.

1. Native Execution (On the Machine)
Setup:
Run the bash script setup.sh, which will check if Python is installed and if all dependencies are present.
Launch:
Once the setup is complete, you can run the script with:
```
python3 script.py 100010
```
2. Execution via Docker
Build the Docker Image:
Within the directory containing the Dockerfile, run:
```
docker build -t proxmox_script .
```
Run the Container:
Execute the container and pass the parameter (e.g., 100010) to your script:
```
docker run proxmox_script 100010
```
In case it's needed, an easy way to delete cloned machines is by using the delete.py script, which allows for quickly removing the machines.

## Final Notes
- Configuration: Ensure that you configure config.py accurately for your environment.
- API_TOKEN: Pay close attention to this parameter and its associated permissions.
- Cloud-init: The formatting of the public key is critical.
- Distributions: Verify that the distribution name in os_list.json is written in lowercase.
- Execution Modes: Choose between native execution or via Docker depending on your needs.

