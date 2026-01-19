# Socket Service - Servizio Python per Comandi via Socket

Un servizio Python che ascolta su un socket TCP e gestisce comandi inviati in formato JSON.

## Caratteristiche

- **Server Socket TCP** con gestione multi-client
- **Comandi multipli** con gestione estensibile
- **Logging completo** su file e console
- **Thread-safe** - ogni client viene gestito in un thread separato
- **Formato JSON** per comandi e risposte
- **Client di esempio** incluso

## Requisiti

- Python 3.6 o superiore
- Nessuna dipendenza esterna (usa solo librerie standard)

## Installazione

```bash
# Clona il repository
git clone <repository-url>
cd opencv_webcam

# Rendi eseguibili i file Python
chmod +x socket_service.py client_example.py
```

## Utilizzo

### Avvio del Servizio

```bash
# Avvia il servizio sulla porta di default (9999)
python3 socket_service.py

# Avvia su una porta specifica
python3 socket_service.py --port 8080

# Avvia su un indirizzo specifico
python3 socket_service.py --host 127.0.0.1 --port 8080
```

### Utilizzo del Client

```bash
# Modalità interattiva
python3 client_example.py

# Connetti a un server specifico
python3 client_example.py --host 192.168.1.100 --port 9999

# Esegui comandi di esempio
python3 client_example.py --examples
```

### Test con netcat

Puoi anche testare il servizio usando netcat:

```bash
# Connetti al servizio
nc localhost 9999

# Invia comandi JSON
{"command": "ping"}
{"command": "help"}
{"command": "echo", "message": "Ciao!"}
{"command": "status"}
```

### Test con curl (HTTP non supportato direttamente)

Per testare tramite TCP con telnet:

```bash
telnet localhost 9999
```

## Comandi Disponibili

### ping
Verifica la connessione al servizio.

**Richiesta:**
```json
{"command": "ping"}
```

**Risposta:**
```json
{
  "status": "success",
  "message": "pong",
  "timestamp": "2026-01-19T12:00:00.000000"
}
```

### help
Mostra la lista dei comandi disponibili.

**Richiesta:**
```json
{"command": "help"}
```

**Risposta:**
```json
{
  "status": "success",
  "commands": ["ping", "echo", "status", "help", "exec", "info", "shutdown"],
  "description": {
    "ping": "Verifica la connessione al servizio",
    "echo": "Ritrasmette il messaggio ricevuto (parametro: message)",
    ...
  }
}
```

### echo
Ritrasmette il messaggio ricevuto.

**Richiesta:**
```json
{"command": "echo", "message": "Il mio messaggio"}
```

**Risposta:**
```json
{
  "status": "success",
  "echo": "Il mio messaggio"
}
```

### status
Restituisce lo stato del servizio.

**Richiesta:**
```json
{"command": "status"}
```

**Risposta:**
```json
{
  "status": "success",
  "service": "running",
  "clients_connected": 2,
  "uptime": "2026-01-19T12:00:00.000000"
}
```

### info
Restituisce informazioni sul sistema.

**Richiesta:**
```json
{"command": "info"}
```

**Risposta:**
```json
{
  "status": "success",
  "system": "Linux",
  "platform": "Linux-4.4.0",
  "python_version": "3.8.0",
  "hostname": "server",
  "cwd": "/home/user/opencv_webcam"
}
```

### exec
Esegue un comando shell.

**ATTENZIONE:** Usare con cautela! Questo comando può eseguire qualsiasi comando shell.

**Richiesta:**
```json
{"command": "exec", "command": "ls -la"}
```

**Risposta:**
```json
{
  "status": "success",
  "returncode": 0,
  "stdout": "total 24\ndrwxr-xr-x...",
  "stderr": ""
}
```

### start
Esegue un metodo da un file Python specificato.

**Parametri:**
- `filename`: Path del file Python (.py)
- `method`: Nome del metodo da eseguire
- `params` (opzionale): Parametri da passare al metodo (dizionario o lista)

**Richiesta senza parametri:**
```json
{
  "command": "start",
  "filename": "example_module.py",
  "method": "hello_world"
}
```

**Risposta:**
```json
{
  "status": "success",
  "result": "Hello, World!",
  "module": "example_module",
  "method": "hello_world"
}
```

**Richiesta con parametri (dizionario):**
```json
{
  "command": "start",
  "filename": "example_module.py",
  "method": "add_numbers",
  "params": {"a": 10, "b": 20}
}
```

**Risposta:**
```json
{
  "status": "success",
  "result": 30,
  "module": "example_module",
  "method": "add_numbers"
}
```

**Richiesta con parametri (lista):**
```json
{
  "command": "start",
  "filename": "example_module.py",
  "method": "fibonacci",
  "params": {"n": 10}
}
```

**Risposta:**
```json
{
  "status": "success",
  "result": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34],
  "module": "example_module",
  "method": "fibonacci"
}
```

**Errore - File non trovato:**
```json
{
  "status": "error",
  "message": "File non trovato: myfile.py"
}
```

**Errore - Metodo non trovato:**
```json
{
  "status": "error",
  "message": "Metodo \"mymethod\" non trovato nel file example_module.py",
  "available_methods": ["hello_world", "add_numbers", "fibonacci", ...]
}
```

### shutdown
Arresta il servizio.

**Richiesta:**
```json
{"command": "shutdown"}
```

**Risposta:**
```json
{
  "status": "success",
  "message": "Servizio in arresto..."
}
```

## Esempi di Utilizzo

### Esempio Python

```python
import socket
import json

# Connetti al servizio
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 9999))

# Ricevi il messaggio di benvenuto
welcome = sock.recv(4096)
print(welcome.decode())

# Invia un comando ping
command = {"command": "ping"}
sock.send((json.dumps(command) + '\n').encode())

# Ricevi la risposta
response = sock.recv(4096)
print(json.loads(response.decode()))

# Chiudi la connessione
sock.close()
```

### Esempio con il Client Interattivo

```bash
$ python3 client_example.py

=== Modalità Interattiva ===
Comandi disponibili:
  help              - Mostra i comandi del servizio
  ping              - Verifica la connessione
  status            - Mostra lo stato del servizio
  ...

>>> ping
Risposta:
{
  "status": "success",
  "message": "pong",
  "timestamp": "2026-01-19T12:00:00.000000"
}

>>> echo Ciao a tutti!
Risposta:
{
  "status": "success",
  "echo": "Ciao a tutti!"
}

>>> start example_module.py hello_world
Risposta:
{
  "status": "success",
  "result": "Hello, World!",
  "module": "example_module",
  "method": "hello_world"
}

>>> start example_module.py add_numbers {"a":5,"b":3}
Risposta:
{
  "status": "success",
  "result": 8,
  "module": "example_module",
  "method": "add_numbers"
}

>>> quit
Disconnessione...
```

### File di Esempio (example_module.py)

Il progetto include un file `example_module.py` con diverse funzioni che possono essere eseguite tramite il comando `start`:

- `hello_world()`: Restituisce un saluto
- `get_current_time()`: Restituisce l'ora corrente
- `add_numbers(a, b)`: Somma due numeri
- `multiply_numbers(x, y)`: Moltiplica due numeri
- `fibonacci(n)`: Genera i primi n numeri di Fibonacci
- `is_prime(number)`: Verifica se un numero è primo
- `calculate_factorial(n)`: Calcola il fattoriale
- E molte altre...

Puoi usare questo file per testare il comando `start` o creare i tuoi moduli personalizzati.

## Architettura

Il servizio è composto da:

1. **SocketService**: Classe principale che gestisce il server socket
2. **Command Handlers**: Metodi che gestiscono i singoli comandi
3. **Client Handler**: Thread separato per ogni client connesso
4. **Logging**: Sistema di log su file e console

### Aggiungere Nuovi Comandi

Per aggiungere un nuovo comando, modifica il metodo `_register_commands()` e aggiungi un nuovo handler:

```python
def _register_commands(self):
    self.command_handlers = {
        # ... comandi esistenti ...
        'mycommand': self._handle_mycommand,
    }

def _handle_mycommand(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Gestisce il mio comando personalizzato"""
    param = data.get('param', '')
    # ... logica del comando ...
    return {
        'status': 'success',
        'result': 'risultato'
    }
```

## Sicurezza

⚠️ **IMPORTANTE:**

- Il comando `exec` può eseguire qualsiasi comando shell - usare solo in ambienti controllati
- Il comando `start` può eseguire qualsiasi codice Python dai file specificati - verificare sempre i file prima dell'esecuzione
- Non esporre il servizio su Internet senza adeguate misure di sicurezza
- Considera l'aggiunta di autenticazione per ambienti di produzione
- Valuta l'uso di SSL/TLS per connessioni crittografate
- Limita l'accesso ai file che possono essere eseguiti con il comando `start`

## Log

I log vengono salvati in:
- **Console**: Output standard
- **File**: `socket_service.log` nella directory corrente

## Troubleshooting

### Il servizio non si avvia

```bash
# Verifica che la porta non sia già in uso
netstat -tuln | grep 9999

# Prova con una porta diversa
python3 socket_service.py --port 8080
```

### Impossibile connettersi

- Verifica che il firewall permetta connessioni sulla porta
- Controlla che l'indirizzo host sia corretto
- Assicurati che il servizio sia in esecuzione

### Errori di formato JSON

I comandi devono essere JSON validi e terminare con `\n`:

```json
{"command": "ping"}
```

## Licenza

MIT License

## Contributi

Contributi, issues e feature requests sono benvenuti!
