
from datetime import datetime

def calculo_años(fecha_inicio, fecha_termino=None):
    from datetime import datetime

    if not isinstance(fecha_inicio, str):
        return 0

    try:
        inicio = datetime.strptime(fecha_inicio.strip(), '%d/%m/%Y')
        fin_str = fecha_termino.strip() if fecha_termino and isinstance(fecha_termino, str) else None
        fin = datetime.strptime(fin_str, '%d/%m/%Y') if fin_str else datetime.now()
        # Logic Restore: (fin - inicio).days // 365
        return (fin - inicio).days // 365
    except Exception as e:
        print(f"[ERROR] calculo_años: {e} | inicio: {fecha_inicio} - fin: {fecha_termino}")
        return 0

# Test cases
print("Testing empty string:")
calculo_años("")

print("\nTesting ISO format:")
calculo_años("1958-07-23")

print("\nTesting valid format:")
print(f"Result: {calculo_años('12/01/2000')}")
