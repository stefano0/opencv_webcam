#!/bin/bash
# Script di test per il Socket Service

echo "=== Test Socket Service ==="
echo ""

# Avvia il servizio in background
echo "1. Avvio del servizio..."
python3 socket_service.py --port 9999 &
SERVICE_PID=$!

# Aspetta che il servizio sia pronto
sleep 2

# Verifica che il servizio sia in esecuzione
if ! kill -0 $SERVICE_PID 2>/dev/null; then
    echo "ERRORE: Il servizio non si è avviato correttamente"
    exit 1
fi

echo "   Servizio avviato (PID: $SERVICE_PID)"
echo ""

# Esegue i comandi di esempio
echo "2. Esecuzione comandi di esempio..."
python3 client_example.py --examples

echo ""
echo "3. Test completati!"
echo ""

# Arresta il servizio
echo "4. Arresto del servizio..."
kill $SERVICE_PID
wait $SERVICE_PID 2>/dev/null

echo "   Servizio arrestato"
echo ""
echo "=== Test completato con successo ==="
