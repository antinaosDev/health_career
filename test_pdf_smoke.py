
from modules.pdf_gen import create_pdf
import os

# Mock Data
user_data = {'NOMBRE_FUNC': 'Test User', 'RUT': '1-9', 'CATEGORIA': 'A', 'NIVEL': 15, 'PTJE_CARR': 100, 'SALDO_PTJE': 50}
caps_data = [{'AÑO_PRESENTACION': 2024, 'NOMBRE_CAPACITACION': 'Test Cap', 'ENTIDAD': 'Test', 'HORAS': 20, 'PJE_POND': 10, 'NOTA': 7}]
conts_data = [{'TIPO_CONTRATO': 'Planta', 'HORAS': 44}]
extra_info = {'prox_bienio': '2026', 'meta_puntos': 10, 'cap_status_msg': '**Cupo Disponible**: Te quedan 100 puntos.', 'cap_used': 3400, 'cap_global': 3500}
summary_dict = {'ARRASTRE_PTS': 500, 'VALOR_BIENIOS': 1000, 'BASE_PLANTA': 2000}
breakdown_data = [{'AÑO': 2024, 'PUNTOS_REALES': 150, 'LIMITE': 150, 'DIFERENCIA': 0, 'SALDO_ACUMULADO': 0}]

try:
    print("Generating PDF...")
    pdf_bytes = create_pdf(user_data, caps_data, conts_data, extra_info, "logo.png", "logo2.png", {}, breakdown_data, summary_dict)
    print(f"PDF Generated. Bytes: {len(pdf_bytes)}")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
