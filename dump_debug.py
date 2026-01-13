from firebase_bd import leer_registro
import json

c = leer_registro('contrato')
res = [v for v in c.values() if '18581575-7' in str(v.get('RUT',''))]
with open('contracts_dump.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
print("Dumped", len(res), "records")
