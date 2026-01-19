"""
Modulo di esempio per testare il comando 'start' del Socket Service

Questo file contiene diverse funzioni che possono essere eseguite dinamicamente
tramite il comando 'start' del servizio socket.
"""

import time
from datetime import datetime
import random


def hello_world():
    """
    Funzione semplice che restituisce un saluto

    Returns:
        str: Messaggio di saluto
    """
    return "Hello, World!"


def get_current_time():
    """
    Restituisce l'ora corrente

    Returns:
        str: Timestamp corrente in formato ISO
    """
    return datetime.now().isoformat()


def add_numbers(a, b):
    """
    Somma due numeri

    Args:
        a: Primo numero
        b: Secondo numero

    Returns:
        int/float: Somma di a e b
    """
    return a + b


def multiply_numbers(x, y):
    """
    Moltiplica due numeri

    Args:
        x: Primo numero
        y: Secondo numero

    Returns:
        int/float: Prodotto di x e y
    """
    return x * y


def generate_random_number(min_val=1, max_val=100):
    """
    Genera un numero casuale nell'intervallo specificato

    Args:
        min_val: Valore minimo (default: 1)
        max_val: Valore massimo (default: 100)

    Returns:
        int: Numero casuale
    """
    return random.randint(min_val, max_val)


def calculate_factorial(n):
    """
    Calcola il fattoriale di un numero

    Args:
        n: Numero intero non negativo

    Returns:
        int: Fattoriale di n

    Raises:
        ValueError: Se n è negativo
    """
    if n < 0:
        raise ValueError("Il fattoriale è definito solo per numeri non negativi")

    if n == 0 or n == 1:
        return 1

    result = 1
    for i in range(2, n + 1):
        result *= i

    return result


def reverse_string(text):
    """
    Inverte una stringa

    Args:
        text: Stringa da invertire

    Returns:
        str: Stringa invertita
    """
    return text[::-1]


def count_words(text):
    """
    Conta il numero di parole in un testo

    Args:
        text: Testo da analizzare

    Returns:
        dict: Dizionario con statistiche sul testo
    """
    words = text.split()
    return {
        'word_count': len(words),
        'character_count': len(text),
        'character_count_no_spaces': len(text.replace(' ', ''))
    }


def fibonacci(n):
    """
    Genera i primi n numeri della sequenza di Fibonacci

    Args:
        n: Numero di elementi da generare

    Returns:
        list: Lista con i primi n numeri di Fibonacci
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]

    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    return fib_sequence


def is_prime(number):
    """
    Verifica se un numero è primo

    Args:
        number: Numero da verificare

    Returns:
        dict: Dizionario con il risultato e informazioni aggiuntive
    """
    if number < 2:
        return {
            'number': number,
            'is_prime': False,
            'reason': 'Numeri minori di 2 non sono primi'
        }

    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return {
                'number': number,
                'is_prime': False,
                'divisor': i
            }

    return {
        'number': number,
        'is_prime': True
    }


def process_list(items, operation='sum'):
    """
    Elabora una lista di numeri con l'operazione specificata

    Args:
        items: Lista di numeri
        operation: Operazione da eseguire ('sum', 'avg', 'min', 'max')

    Returns:
        dict: Risultato dell'operazione
    """
    if not items:
        return {
            'operation': operation,
            'result': None,
            'error': 'Lista vuota'
        }

    operations = {
        'sum': sum(items),
        'avg': sum(items) / len(items),
        'min': min(items),
        'max': max(items)
    }

    result = operations.get(operation)

    if result is None:
        return {
            'operation': operation,
            'result': None,
            'error': f'Operazione non valida. Disponibili: {list(operations.keys())}'
        }

    return {
        'operation': operation,
        'result': result,
        'count': len(items)
    }


def simulate_work(duration=2):
    """
    Simula un'operazione che richiede tempo

    Args:
        duration: Durata in secondi (default: 2)

    Returns:
        dict: Informazioni sull'esecuzione
    """
    start_time = time.time()
    time.sleep(duration)
    end_time = time.time()

    return {
        'duration_requested': duration,
        'duration_actual': end_time - start_time,
        'completed': True
    }


def get_system_info():
    """
    Restituisce informazioni sul sistema

    Returns:
        dict: Informazioni di sistema
    """
    import platform
    import sys

    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'python_implementation': platform.python_implementation()
    }


if __name__ == '__main__':
    # Test delle funzioni quando il modulo viene eseguito direttamente
    print("=== Test Modulo Example ===\n")

    print(f"hello_world(): {hello_world()}")
    print(f"get_current_time(): {get_current_time()}")
    print(f"add_numbers(5, 3): {add_numbers(5, 3)}")
    print(f"multiply_numbers(4, 7): {multiply_numbers(4, 7)}")
    print(f"generate_random_number(): {generate_random_number()}")
    print(f"calculate_factorial(5): {calculate_factorial(5)}")
    print(f"reverse_string('Python'): {reverse_string('Python')}")
    print(f"count_words('Hello world from Python'): {count_words('Hello world from Python')}")
    print(f"fibonacci(10): {fibonacci(10)}")
    print(f"is_prime(17): {is_prime(17)}")
    print(f"process_list([1,2,3,4,5], 'avg'): {process_list([1,2,3,4,5], 'avg')}")
