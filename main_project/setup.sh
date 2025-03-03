#!/bin/bash

#controllo se python è installato
command -v python3 1> /dev/null
if [ $? -ne 0 ]; then
	sudo apt install python3 -y
else
	echo "Python è già installato"
fi

#Funzione che controlla se le librerie sono installate
check_library() {
	python3 -c "import $1" 1> /dev/null
	if [ $? -ne 0 ]; then
		sudo apt install python3-$1 -y
	else
		echo "La libreria $1 è gia installata"
	fi
}

# Controlliamo tutte le librerie
check_library "paramiko"
check_library "requests"
check_library "urllib3"

# Impostiamo il permesso di esecuzione su proxmox-script.py
sudo chmod 744 proxmox-script.py delete.py
if [ $? -eq 0 ]; then
	echo "Ora proxmox-script.py e delete.py sono eseguibili"
fi

# Impostiamo il permesso di read e write per error_log.txt update_log.txt
sudo chmod 644 error_log.txt update_log.txt config.py os_list.json
if [ $? -eq 0 ]; then
	echo "Impostato il permesso di read e write per error_log.txt update_log.txt config.py os_list.json"
fi

sudo chmod 400 id_ed25519 id_ed25519.pub
if [ $? -eq 0 ]; then
	echo "Impostato il permesso di read per id_ed25519 id_ed25519.pub"
fi