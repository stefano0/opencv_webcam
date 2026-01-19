#!/usr/bin/env python3
"""
Socket Service - Servizio Python per ricevere e gestire comandi tramite socket
"""

import socket
import threading
import json
import logging
import sys
import os
import subprocess
import importlib.util
import inspect
from datetime import datetime
from typing import Dict, Any, Callable

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('socket_service.log')
    ]
)
logger = logging.getLogger(__name__)


class SocketService:
    """Servizio che gestisce connessioni socket e comandi"""

    def __init__(self, host: str = '0.0.0.0', port: int = 9999):
        """
        Inizializza il servizio socket

        Args:
            host: Indirizzo IP su cui ascoltare
            port: Porta su cui ascoltare
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.clients = []
        self.command_handlers: Dict[str, Callable] = {}

        # Registra i comandi disponibili
        self._register_commands()

    def _register_commands(self):
        """Registra i gestori dei comandi disponibili"""
        self.command_handlers = {
            'ping': self._handle_ping,
            'echo': self._handle_echo,
            'status': self._handle_status,
            'help': self._handle_help,
            'exec': self._handle_exec,
            'info': self._handle_info,
            'start': self._handle_start,
            'shutdown': self._handle_shutdown,
        }

    def _handle_ping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Risponde a un ping"""
        return {
            'status': 'success',
            'message': 'pong',
            'timestamp': datetime.now().isoformat()
        }

    def _handle_echo(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ritrasmette il messaggio ricevuto"""
        message = data.get('message', '')
        return {
            'status': 'success',
            'echo': message
        }

    def _handle_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restituisce lo stato del servizio"""
        return {
            'status': 'success',
            'service': 'running',
            'clients_connected': len(self.clients),
            'uptime': datetime.now().isoformat()
        }

    def _handle_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restituisce la lista dei comandi disponibili"""
        commands = list(self.command_handlers.keys())
        return {
            'status': 'success',
            'commands': commands,
            'description': {
                'ping': 'Verifica la connessione al servizio',
                'echo': 'Ritrasmette il messaggio ricevuto (parametro: message)',
                'status': 'Restituisce lo stato del servizio',
                'help': 'Mostra questa lista di comandi',
                'exec': 'Esegue un comando shell (parametro: command)',
                'info': 'Restituisce informazioni sul sistema',
                'start': 'Esegue un metodo da un file Python (parametri: filename, method)',
                'shutdown': 'Arresta il servizio'
            }
        }

    def _handle_exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Esegue un comando shell
        ATTENZIONE: Usare con cautela in ambienti di produzione
        """
        command = data.get('command', '')
        if not command:
            return {
                'status': 'error',
                'message': 'Comando non specificato'
            }

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'status': 'success',
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'message': 'Comando scaduto (timeout 30s)'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Errore esecuzione: {str(e)}'
            }

    def _handle_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Restituisce informazioni sul sistema"""
        import platform
        return {
            'status': 'success',
            'system': platform.system(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': socket.gethostname(),
            'cwd': os.getcwd()
        }

    def _handle_start(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Esegue un metodo da un file Python specificato

        Args:
            data: Dizionario con 'filename' (nome del file Python) e 'method' (nome del metodo)

        Returns:
            Risultato dell'esecuzione del metodo
        """
        filename = data.get('filename', '')
        method_name = data.get('method', '')

        # Valida i parametri
        if not filename:
            return {
                'status': 'error',
                'message': 'Parametro "filename" non specificato'
            }

        if not method_name:
            return {
                'status': 'error',
                'message': 'Parametro "method" non specificato'
            }

        # Verifica che il file esista
        if not os.path.isfile(filename):
            return {
                'status': 'error',
                'message': f'File non trovato: {filename}'
            }

        # Verifica che il file sia un file Python
        if not filename.endswith('.py'):
            return {
                'status': 'error',
                'message': f'Il file deve essere un file Python (.py): {filename}'
            }

        try:
            # Carica dinamicamente il modulo
            module_name = os.path.splitext(os.path.basename(filename))[0]
            spec = importlib.util.spec_from_file_location(module_name, filename)

            if spec is None or spec.loader is None:
                return {
                    'status': 'error',
                    'message': f'Impossibile caricare il modulo: {filename}'
                }

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Verifica che il metodo esista
            if not hasattr(module, method_name):
                available_methods = [
                    name for name, obj in inspect.getmembers(module)
                    if inspect.isfunction(obj) and not name.startswith('_')
                ]
                return {
                    'status': 'error',
                    'message': f'Metodo "{method_name}" non trovato nel file {filename}',
                    'available_methods': available_methods
                }

            method = getattr(module, method_name)

            # Verifica che sia effettivamente una funzione
            if not callable(method):
                return {
                    'status': 'error',
                    'message': f'"{method_name}" non è una funzione chiamabile'
                }

            # Ottiene i parametri aggiuntivi passati al comando
            params = data.get('params', {})

            # Esegue il metodo
            logger.info(f"Esecuzione {filename}::{method_name} con parametri: {params}")

            # Se params è un dizionario, passa come kwargs, altrimenti come args
            if isinstance(params, dict):
                result = method(**params)
            elif isinstance(params, list):
                result = method(*params)
            else:
                result = method()

            return {
                'status': 'success',
                'result': result,
                'module': module_name,
                'method': method_name
            }

        except TypeError as e:
            return {
                'status': 'error',
                'message': f'Errore nei parametri della funzione: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Errore esecuzione {filename}::{method_name}: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Errore durante l\'esecuzione: {str(e)}',
                'exception_type': type(e).__name__
            }

    def _handle_shutdown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Arresta il servizio"""
        logger.info("Comando di shutdown ricevuto")
        threading.Thread(target=self._delayed_shutdown, daemon=True).start()
        return {
            'status': 'success',
            'message': 'Servizio in arresto...'
        }

    def _delayed_shutdown(self):
        """Arresta il servizio dopo un breve ritardo"""
        import time
        time.sleep(1)
        self.stop()

    def process_command(self, command_str: str) -> str:
        """
        Elabora un comando ricevuto

        Args:
            command_str: Stringa JSON con il comando

        Returns:
            Risposta JSON come stringa
        """
        try:
            # Parse del comando JSON
            command_data = json.loads(command_str)
            command = command_data.get('command', '').lower()

            # Verifica se il comando esiste
            if command not in self.command_handlers:
                response = {
                    'status': 'error',
                    'message': f'Comando sconosciuto: {command}',
                    'available_commands': list(self.command_handlers.keys())
                }
            else:
                # Esegue il gestore del comando
                handler = self.command_handlers[command]
                response = handler(command_data)

            return json.dumps(response)

        except json.JSONDecodeError:
            return json.dumps({
                'status': 'error',
                'message': 'Formato JSON non valido'
            })
        except Exception as e:
            logger.error(f"Errore elaborazione comando: {e}", exc_info=True)
            return json.dumps({
                'status': 'error',
                'message': f'Errore interno: {str(e)}'
            })

    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        Gestisce la comunicazione con un singolo client

        Args:
            client_socket: Socket del client
            address: Indirizzo del client
        """
        logger.info(f"Nuova connessione da {address}")
        self.clients.append(client_socket)

        try:
            # Invia messaggio di benvenuto
            welcome = json.dumps({
                'status': 'connected',
                'message': 'Benvenuto al Socket Service',
                'hint': 'Invia {"command": "help"} per la lista dei comandi'
            })
            client_socket.send((welcome + '\n').encode())

            # Buffer per i dati ricevuti
            buffer = ""

            while self.is_running:
                # Riceve dati dal client
                data = client_socket.recv(4096).decode('utf-8')

                if not data:
                    break

                buffer += data

                # Elabora i comandi completi (terminati da newline)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()

                    if line:
                        logger.info(f"Comando ricevuto da {address}: {line}")
                        response = self.process_command(line)
                        client_socket.send((response + '\n').encode())

        except ConnectionResetError:
            logger.info(f"Connessione chiusa da {address}")
        except Exception as e:
            logger.error(f"Errore gestione client {address}: {e}", exc_info=True)
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            logger.info(f"Client {address} disconnesso")

    def start(self):
        """Avvia il servizio socket"""
        try:
            # Crea il socket del server
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)

            self.is_running = True

            logger.info(f"Socket Service avviato su {self.host}:{self.port}")

            # Loop principale per accettare connessioni
            while self.is_running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()

                    # Gestisce ogni client in un thread separato
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    continue
                except OSError:
                    if self.is_running:
                        raise
                    break

        except KeyboardInterrupt:
            logger.info("Interruzione da tastiera ricevuta")
        except Exception as e:
            logger.error(f"Errore nel server: {e}", exc_info=True)
        finally:
            self.stop()

    def stop(self):
        """Arresta il servizio"""
        logger.info("Arresto del servizio...")
        self.is_running = False

        # Chiude tutti i client connessi
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass

        # Chiude il socket del server
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        logger.info("Servizio arrestato")


def main():
    """Funzione principale"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Socket Service - Servizio per gestire comandi via socket'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Indirizzo IP su cui ascoltare (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9999,
        help='Porta su cui ascoltare (default: 9999)'
    )

    args = parser.parse_args()

    # Crea e avvia il servizio
    service = SocketService(host=args.host, port=args.port)
    service.start()


if __name__ == '__main__':
    main()
