# Proxmox Test Automation Script

## Descrizione
Il seguente script serve ad automatizzare una serie di test da effettuare sulle nuove distribuzioni o aggiornamenti rilasciati, verificando che le modifiche apportate da Proxmox siano effettive all'interno della macchina. Nota: Lo script funziona solamente su distribuzioni Linux.
Il branch 'nice' differisce solo negli output, che sono stati resi più leggibili e colorati. Tuttavia, attenzione, in caso di automazioni, potrebbero esserci delle incompatibilità.

## Configurazione
Prima di eseguire lo script, è necessario configurare alcuni file:

### config.py:
Questo è il primo file da modificare. Dovrai aggiornare tutti i parametri in modo da adattarli al tuo ambiente.

- **API_TOKEN**: I test eseguiti utilizzavano un token con livelli di autorizzazione massimi. Non è chiaro esattamente quali permessi siano necessari, quindi potresti voler creare un token con privilegi di root se non hai altre indicazioni.
- **Chiavi pubbliche e private**: Queste possono rimanere quelle predefinite, a meno che tu non voglia testare la compatibilità con chiavi più sofisticate.
- **Cloud-init**: È particolarmente delicato. Assicurati che la chiave pubblica sia formattata correttamente (con gli spazi specifici) e, se possibile, mantieni lo stesso nome del file.

### os_list.json:
Verifica che la distribuzione sia presente in questo file. È consigliabile scrivere il nome della distribuzione tutto in minuscolo per sicurezza.

## Modalità di Esecuzione
Lo script può essere eseguito in due modalità e in entrambi i casi si aspetta un parametro, per esempio:

```
python3 script.py 100010
```
Il numero passato (es. 100010) corrisponde all'ID del template che si desidera testare.

1. Esecuzione Nativa (Sulla Macchina)
Setup:
Esegui lo script bash setup.sh, che controllerà se Python è installato e se tutte le dipendenze sono presenti.

Avvio:
Una volta completato il setup, puoi eseguire lo script con:
```
python3 script.py 100010
```
2. Esecuzione Tramite Docker
Costruzione dell'Immagine Docker:
All'interno della directory che contiene il Dockerfile, esegui:
```
docker build -t proxmox_script .
```
Avvio del Container:
Esegui il container e passa il parametro (ad esempio, 100010) al tuo script:
```
docker run proxmox_script 100010
```
Note Finali
Configurazione: Assicurati di configurare accuratamente config.py in base al tuo ambiente.
API_TOKEN: Presta particolare attenzione a questo parametro e ai relativi permessi.
Cloud-init: La formattazione della chiave pubblica è critica.
Distribuzioni: Verifica che il nome della distribuzione in os_list.json sia scritto in minuscolo.
Modalità d'Esecuzione: Scegli tra esecuzione nativa o tramite Docker in base alle tue esigenze.
