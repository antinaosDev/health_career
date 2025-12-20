from indices import *

class Funcionario:
    def __init__(self, nombre, rut, genero, profesion, categoria, dia_nac, mes_nac, año_nac):
        self.nombre = nombre
        self.rut = rut
        self.genero = genero
        self.profesion = profesion
        self.categoria = categoria
        self.dia_nac = int(dia_nac or 0)
        self.mes_nac = int(mes_nac or 0)
        self.año_nac = int(año_nac or 0)

    def crear_dict_func(self):
        return {
            'NOMBRE_FUNC': self.nombre,
            'RUT': self.rut,
            'GENERO': self.genero,
            'PROFESION': self.profesion,
            'CATEGORIA': self.categoria,
            'FECHA_NAC': f"{self.dia_nac:02d}/{self.mes_nac:02d}/{self.año_nac}"
        }



class Contrato:
    def __init__(self, rut, tipo_cont, horas_cont, dependencia, cargo, reemplazo,inst,
                  nom_inst,dia_inic, mes_inic, año_inic, dia_ter, mes_ter, año_ter):
        
        self.rut = rut
        self.tipo_contrato = tipo_cont
        self.horas_contrato = int(horas_cont or 0)
        self.dependencia = dependencia
        self.cargo = cargo
        self.reemplazo = reemplazo
        self.t_inst = inst
        self.nom_inst = nom_inst
        self.dia_inicio = int(dia_inic or 0)
        self.mes_inicio = int(mes_inic or 0)
        self.año_inicio = int(año_inic or 0)
        self.dia_termino = int(dia_ter or 0)
        self.mes_termino = int(mes_ter or 0)
        self.año_termino = int(año_ter or 0)

    def crear_dict_contrato(self):
        return {
            'RUT': self.rut,
            'TIPO_CONTRATO': self.tipo_contrato,
            'HORAS': self.horas_contrato,
            'DEPENDENCIA': self.dependencia,
            'CARGO': self.cargo,
            'REEMPLAZO': self.reemplazo,
            'TIPO_INSTITUCION':self.t_inst, #Estos son nuevos  campos
            'NOMBRE_INSTITUCION':self.nom_inst,#Estos son nuevos campos
            'FECHA_INICIO': f"{self.dia_inicio:02d}/{self.mes_inicio:02d}/{self.año_inicio}",
            'FECHA_TERMINO': f"{self.dia_termino:02d}/{self.mes_termino:02d}/{self.año_termino}"
        }




class Capacitacion:
    def __init__(self, rut, cat, nombre_cap, entidad, horas_cap, nv_tec, nota, año_inic, año_pres,cont_press,post, tipo_cap=''):
        self.cat = cat
        self.rut = rut
        self.nombre_capacitacion = nombre_cap
        self.entidad = entidad
        self.horas = int(horas_cap or 0)
        self.nivel_tecnico = nv_tec
        try:
            nota = str(nota).replace(",", ".")  # Reemplazar coma por punto en la nota
            self.nota = float(nota)
        except (ValueError, TypeError):
            self.nota = 0.0
        self.año_inicio = int(año_inic or 0)
        self.año_presentacion = int(año_pres or 0)
        self.cont_press = cont_press
        self.post = post
        self.tipo_cap = tipo_cap



    def crear_dict_capacitacion(self):
        dict_cap = {
            'RUT': self.rut,
            'NOMBRE_CAPACITACION': self.nombre_capacitacion,
            'ENTIDAD': self.entidad,
            'HORAS': self.horas,
            'NIVEL_TECNICO': self.nivel_tecnico,
            'NOTA': self.nota,
            'AÑO_INICIO': self.año_inicio,
            'AÑO_PRESENTACION': self.año_presentacion,
            'CONTEXTO_PRESS':self.cont_press,
            'ES_POSTGRADO':self.post,#Se agregó
            'TIPO_CAPACITACION': self.tipo_cap
        }

        # Calcular PJE_NV_TEC según categoría y nivel técnico
        if self.cat in ('A', 'B'):
            for k, v in nv_tec_AB.items():
                if k == self.nivel_tecnico:
                    dict_cap['PJE_NV_TEC'] = v
        else:
            for k, v in nv_tec_CF.items():
                if k == self.nivel_tecnico:
                    dict_cap['PJE_NV_TEC'] = v

        # Calcular PJE_HORAS
        for k, v in horas_cap.items():
            if k[0] <= self.horas <= k[1]:
                dict_cap['PJE_HORAS'] = v

        # Calcular PJE_NOTA
        for k, v in aprobacion.items():
            if k[0] <= self.nota <= k[1]:
                dict_cap['PJE_NOTA'] = v

        # Calcular ponderado final
        dict_cap['PJE_POND'] = (
            round(dict_cap.get('PJE_NV_TEC', 0),2) *
            round(dict_cap.get('PJE_HORAS', 0),2) *
            round(dict_cap.get('PJE_NOTA', 0),2)
        )
        dict_cap['PJE_POND'] = round(dict_cap['PJE_POND'],2) 
        return dict_cap
