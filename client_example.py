#!/usr/bin/env python3
"""
Client di esempio per il Socket Service
"""

import socket
import json
import sys


class SocketClient:
    """Client per comunicare con il Socket Service"""

    def __init__(self, host: str = 'localhost', port: int = 9999):
        """
        Inizializza il client

        Args:
            host: Indirizzo del server
            port: Porta del server
        """
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Stabilisce la connessione al server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            # Riceve il messaggio di benvenuto
            welcome = self.socket.recv(4096).decode('utf-8')
            print(f"Server: {welcome.strip()}")
            return True

        except ConnectionRefusedError:
            print(f"Errore: impossibile connettersi a {self.host}:{self.port}")
            print("Assicurati che il servizio sia in esecuzione.")
            return False
        except Exception as e:
            print(f"Errore connessione: {e}")
            return False

    def send_command(self, command: str, **params) -> dict:
        """
        Invia un comando al server

        Args:
            command: Nome del comando
            **params: Parametri aggiuntivi del comando

        Returns:
            Risposta del server come dizionario
        """
        if not self.socket:
            raise RuntimeError("Non connesso al server")

        # Prepara il comando JSON
        command_data = {'command': command, **params}
        command_json = json.dumps(command_data) + '\n'

        # Invia il comando
        self.socket.send(command_json.encode())

        # Riceve la risposta
        response = self.socket.recv(4096).decode('utf-8')
        return json.loads(response.strip())

    def close(self):
        """Chiude la connessione"""
        if self.socket:
            self.socket.close()
            self.socket = None


def interactive_mode(client: SocketClient):
    """Modalità interattiva per inviare comandi"""
    print("\n=== Modalità Interattiva ===")
    print("Comandi disponibili:")
    print("  help              - Mostra i comandi del servizio")
    print("  ping              - Verifica la connessione")
    print("  status            - Mostra lo stato del servizio")
    print("  info              - Mostra informazioni sul sistema")
    print("  echo <messaggio>  - Ritrasmette un messaggio")
    print("  exec <comando>    - Esegue un comando shell")
    print("  shutdown          - Arresta il servizio")
    print("  quit              - Esce dal client")
    print()

    while True:
        try:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print("Disconnessione...")
                break

            # Parse del comando
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ''

            # Prepara i parametri
            params = {}
            if command == 'echo' and args:
                params['message'] = args
            elif command == 'exec' and args:
                params['command'] = args

            # Invia il comando
            response = client.send_command(command, **params)

            # Mostra la risposta
            print(f"\nRisposta:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print()

        except KeyboardInterrupt:
            print("\n\nInterruzione da tastiera")
            break
        except Exception as e:
            print(f"Errore: {e}")


def run_examples(client: SocketClient):
    """Esegue alcuni comandi di esempio"""
    print("\n=== Esempi di Comandi ===\n")

    examples = [
        ('ping', {}),
        ('help', {}),
        ('status', {}),
        ('info', {}),
        ('echo', {'message': 'Ciao dal client!'}),
    ]

    for command, params in examples:
        print(f"Comando: {command} {params}")
        response = client.send_command(command, **params)
        print(f"Risposta: {json.dumps(response, indent=2, ensure_ascii=False)}\n")


def main():
    """Funzione principale"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Client per Socket Service'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Indirizzo del server (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9999,
        help='Porta del server (default: 9999)'
    )
    parser.add_argument(
        '--examples',
        action='store_true',
        help='Esegui comandi di esempio e poi esci'
    )

    args = parser.parse_args()

    # Crea il client e connetti
    client = SocketClient(host=args.host, port=args.port)

    if not client.connect():
        sys.exit(1)

    try:
        if args.examples:
            run_examples(client)
        else:
            interactive_mode(client)
    finally:
        client.close()


if __name__ == '__main__':
    main()
