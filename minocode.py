from firebase_bd import *
from indices import *
from funciones import *

data_capacitacion = leer_registro('capacitaciones')

horas_cap = [hora.get('HORAS') for hora in data_capaciacion.values()
             if hora.get('RUT') == '18.581.575-7' and hora.get('ES_POSTGRADO') == 'SI']

suma_horas = sum(horas_cap)
porcentaje_asig = porcentaje_postgrado(suma_horas,'18.581.575-7')


print(porcentaje_asig)