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
check_library "requests"
check_library "urllib3"
check_library "urllib"
check_library "paramiko"

# Impostiamo il permesso di esecuzione su proxmox-script.py
sudo chmod 744 proxmox-script.py
if [ $? -eq 0 ]; then
	echo "Ora proxmox-script.py è eseguibile"
fi
