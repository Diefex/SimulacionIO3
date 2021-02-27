#imports
import tkinter
from tkinter import Tk
from tkinter import Frame
from tkinter import Label
from tkinter import Canvas
from tkinter import Button
from tkinter import Text
from tkinter import DISABLED
from tkinter import NORMAL
from tkinter import INSERT
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
from copy import copy
import random

#Clases
class Producto():

    def __init__(self, n):
        self.num = n
        self.estado = "N"
        self.valor = 0
        '''
        N = Normal
        D = Desechable
        R = Reprocesable
        F = Reparable
        C = Reclasificable
        '''
        
        self.tiempo = 0
        self.costo = 0
        self.valor = 0

        self.procesado_1 = False
        self.procesado_2 = False

        self.reprocesado_1 = False
        self.reprocesado_2 = False
        self.reparado = False
        self.reclasificado = False
        self.desechado = False

        self.exito_1 = False
        self.exito_2 = False

        self.revisado_1 = False
        self.revisado_2 = False

        self.reembolsado = False
        self.pbn = False


class Fabrica():
    def __init__(self, pe, pd, pr, pf, tmin, tmax, cost):
        #Condiciones Iniciales
        self.prob_exito = pe
        self.prob_Des = pd
        self.prob_Rep = pr
        self.prob_Fix = pf
        self.t_min = tmin
        self.t_max = tmax
        self.costo_min = cost
        
        #Datos recogidos
        self.procesados = 0
        self.reprocesados_prev = 0
        self.reprocesados_posv = 0
        self.conformes = 0
        self.no_conformes = 0
        self.desechables = 0
        self.reprocesables = 0
        self.reparables = 0
        self.reclasificables = 0

        self.tiempo_proceso = 0
        self.costo_proceso = 0

        self.tiempo_reproceso_prev = 0
        self.costo_reproceso_prev = 0

        self.tiempo_reproceso_posv = 0
        self.costo_reproceso_posv = 0

        self.tiempo_total = 0
        self.costo_total = 0

    def procesar(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_proceso += t
        self.costo_proceso += t * self.costo_min

        producto.tiempo += t
        producto.costo += t * self.costo_min

        self.procesados += 1

        if(producto.estado == "R" or producto.estado == "D"):
            self.no_conformes += 1
            self.desechables += 1
            producto.estado = "D"
            return False

        if(random.random() < self.prob_exito):
            self.conformes += 1
            return True
        else:
            self.no_conformes +=1
            r = random.random()
            if(r < self.prob_Des):
                producto.estado = "D"
                self.desechables += 1
            else:
                if(r < self.prob_Des+self.prob_Rep):
                    producto.estado = "R"
                    self.reprocesables += 1
                else:
                    if(r < self.prob_Des+self.prob_Rep+self.prob_Fix):
                        producto.estado = "F"
                        self.reparables += 1
                    else:
                        producto.estado = "C"
                        self.reclasificables += 1
        
            return False

    def reprocesar_prev(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_reproceso_prev += t
        self.costo_reproceso_prev += t * self.costo_min

        producto.tiempo += t
        producto.costo += t * self.costo_min

        self.reprocesados_prev += 1

        producto.estado = "N"

        return True

    def reprocesar_posv(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_reproceso_posv += t
        self.costo_reproceso_posv += t * self.costo_min

        producto.tiempo += t
        producto.costo += t * self.costo_min

        self.reprocesados_posv += 1

        producto.estado = "N"

        return True

class Taller():
    def __init__(self, tmin, tmax, cost):
        #Condiciones Iniciales
        self.t_min = tmin
        self.t_max = tmax
        self.costo_min = cost

        #Datos Recogidos
        self.reparados_prev = 0
        self.reparados_posv = 0
        self.tiempo_prev = 0
        self.costo_prev = 0
        self.tiempo_posv = 0
        self.costo_posv = 0

    def reparar_prev(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_prev += t
        self.costo_prev += t * self.costo_min

        producto.tiempo += t
        producto.costo += t * self.costo_min

        self.reparados_prev += 1
        producto.estado = "N"
        producto.reparado = True

    def reparar_posv(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_posv += t
        self.costo_posv += t * self.costo_min

        producto.tiempo += t
        producto.costo += t * self.costo_min

        self.reparados_posv += 1
        producto.estado = "N"
        producto.reparado = True


class Operario():
    def __init__(self, pr,  tmin, tmax, cost):
        #Condiciones Iniciales
        self.prob_rev = pr
        self.t_min = tmin
        self.t_max = tmax
        self.costo_min = cost

        #Datos Recogidos
        self.revisados = 0
        self.aprobados = 0
        self.reprocesados = 0
        self.desechados = 0
        self.reparados = 0
        self.reclasificados = 0

        self.tiempo_total = 0
        self.costo_total = 0

    def revisar(self, producto):
        t = self.t_min+(self.t_max-self.t_min)*random.random()

        self.tiempo_total += t
        self.costo_total += self.costo_min

        producto.tiempo += t
        producto.costo += self.costo_min

        self.revisados += 1

        if(producto.estado == "N"):
            self.aprobados += 1
            return "Pasar"
        if(producto.estado == "D"):
            self.desechados += 1
            return "Desechar"
        if(producto.estado == "R"):
            self.reprocesados += 1
            return "Reprocesar"
        if(producto.estado == "F"):
            self.reparados += 1
            return "Reparar"
        if(producto.estado == "C"):
            self.reclasificados += 1
            return "Reclasificar"

class Cliente():
    def __init__(self, num, pv, p):
        #Condiciones Iniciales
        self.num = num
        self.prob_volver = pv
        self.producto = p

        #Datos Recogidos
        self.satisfecho = False
        self.revisado = False
        self.vuelve = False
        self.reclamo_atendido = False
        self.reembolsado = False

    def revisar(self):
        self.revisado = True
        for mal_estado in ["D", "R", "F", "C"]:
            if (self.producto.estado == mal_estado):
                self.satisfecho = False
                if(random.random() < self.prob_volver):
                    self.vuelve = True
                return False
        self.satisfecho = True
        return True


#Simulacion
def crear_prouductos_brutos():
    productos_brutos = []
    for i in range(0,1000):
        productos_brutos.append(Producto(i+1))
    
    return productos_brutos

def procesar_productos_1(productos, fabrica):
    productos_procesados = []
    for pr in productos:
        p = copy(pr)
        if(fabrica.procesar(p)):
            p.exito_1 = True
        p.procesado_1 = True
        productos_procesados.append(p)

    return productos_procesados

def reprocesar_productos_1(productos, fabrica):
    productos_reprocesados = []
    for pr in productos:
        p = copy(pr)
        fabrica.reprocesar_prev(p)
        p.reprocesado_1 = True
        productos_reprocesados.append(p)

    return productos_reprocesados

def revisar_productos_1(productos, operario, fabrica):
    productos_revisados = []
    productos_norevisados = []
    productos_reproceso = []
    for pr in productos:
        p = copy(pr)
        if(random.random() < operario.prob_rev):
            p.revisado_1 = True
            decision = operario.revisar(p)
            if(decision == "Pasar"):
                productos_revisados.append(p)
            else:
                if(decision == "Reprocesar"):
                    productos_reproceso.append(p)
        else:
            productos_norevisados.append(p)
            
    productos_revisados.extend(reprocesar_productos_1(productos_reproceso, fabrica))
    productos_revisados.extend(productos_norevisados)
    return productos_revisados

def procesar_productos_2(productos, fabrica):
    productos_procesados = []
    for pr in productos:
        p = copy(pr)
        if(fabrica.procesar(p)):
            p.exito_2 = True
        p.procesado_2 = True
        productos_procesados.append(p)

    return productos_procesados

def reprocesar_productos_2(productos, fabrica):
    productos_reprocesados = []
    for pr in productos:
        p = copy(pr)
        fabrica.reprocesar_prev(p)
        p.reprocesado_2 = True
        productos_reprocesados.append(p)
    return productos_reprocesados

def reparar_productos(productos, taller):
    productos_reparados = []
    for pr in productos:
        p = copy(pr)
        taller.reparar_prev(p)
        productos_reparados.append(p)

    return productos_reparados

def reclasificar_productos(productos):
    productos_reclasificados = []
    for pr in productos:
        p = copy(pr)
        p.estado = "N"
        p.reclasificado = True
        productos_reclasificados.append(p)

    return productos_reclasificados

def desechar_productos(productos):
    productos_desechados = []
    for pr in productos:
        p = copy(pr)
        p.estado = "N"
        p.desechado = True
        productos_desechados.append(p)

    return productos_desechados

def revisar_productos_2(productos, operario, fabrica):
    productos_revisados = []
    productos_norevisados = []
    productos_desecho = []
    productos_reproceso = []
    productos_reparacion = []
    productos_reclasificacion = []
    for pr in productos:
        p = copy(pr)
        if(random.random() < operario.prob_rev):
            p.revisado_2 = True
            decision = operario.revisar(p)
            if(decision == "Pasar"):
                productos_revisados.append(p)
            else:
                if(decision == "Desechar"):
                    productos_desecho.append(p)
                if(decision == "Reprocesar"):
                    productos_reproceso.append(p)
                if(decision == "Reparar"):
                    productos_reparacion.append(p)
                if(decision == "Reclasificacion"):
                    productos_reclasificacion.append(p)
        else:
            productos_norevisados.append(p)
    
    productos_revisados.extend(reprocesar_productos_2(productos_reproceso, fabrica))
    productos_revisados.extend(reparar_productos(productos_reparacion, taller))
    productos_revisados.extend(reclasificar_productos(productos_reclasificacion))
    productos_revisados.extend(desechar_productos(productos_desecho))
    productos_revisados.extend(productos_norevisados)
    return productos_revisados

def valorizar_productos(productos):
    productos_valorizados = []
    for pr in productos:
        p = copy(pr)
        p.valor = 2800
        if(p.reclasificado):
            p.valor = 1800
        if(p.desechado):
            p.valor = 9
        productos_valorizados.append(p)

    return productos_valorizados

def vender_productos(productos):
    clientes = []  
    for pr in productos:
        p = copy(pr)
        c = Cliente(p.num, 0.75, p)
        clientes.append(c)
    return clientes

def clientes_reclamar(clientes):
    clientes_rec = []
    for cli in clientes:
        c = copy(cli)
        c.revisar()
        clientes_rec.append(c)
    return clientes_rec

def atender_reclamos(clientes, fabrica, taller):
    clientes_atendidos = []
    for cli in clientes:
        c = copy(cli)
        if(c.vuelve):
            if(c.producto.estado == "D" or c.producto.estado == "C"):
                c.reembolsado = True
                c.satisfecho = True
            else:
                if(c.producto.estado == "R"):
                    fabrica.reprocesar_posv(c.producto)
                    c.producto.reprocesado_2 = True
                    c.satisfecho = True
                else:
                    taller.reparar_posv(c.producto)
                    c.satisfecho = True
            c.reclamo_atendido = True
        clientes_atendidos.append(c)
    return clientes_atendidos


productos0 = crear_prouductos_brutos()

fabrica_1 = Fabrica(0.840, 0.181, 0.819, 0, 4.3, 7.1, 78)
fabrica_2 = Fabrica(0.927, 0.123, 0.493, 0.233, 9.1, 11.4, 82)
taller = Taller(5.2, 7.3, 5)

operario_1 = Operario(0.5, 2.5, 3.2, 7)
operario_2 = Operario(0.5, 3.7, 9.9, 7)

productos1 = procesar_productos_1(productos0, fabrica_1)
productos2 = revisar_productos_1(productos1, operario_1, fabrica_1)
productos3 = procesar_productos_2(productos2, fabrica_2)
productos4 = revisar_productos_2(productos3, operario_2, fabrica_2)
productos5 = valorizar_productos(productos4)
clientes0 = vender_productos(productos5)
clientes1 = clientes_reclamar(clientes0)
clientes2 = atender_reclamos(clientes1, fabrica_2, taller)

pasos = [[productos0, "Productos en Bruto"], 
    [productos1, "Operación 1"],
    [productos2, "Revisión 1"], 
    [productos3, "Operación 2"], 
    [productos4, "Revisión 2"],
    [productos5, "Productos listos"],
    [clientes0, "Puesta en venta de productos"],
    [clientes1, "Compra de productos"],
    [clientes2, "Atención de reclamos"]]
paso = 0

#Interfaz de Usuario
def label(texto, frame, tam):
    return Label(frame, text=texto, bg="#2d3e52", fg="white", font=("Arial", tam, "bold"))
def label_valor(valor, frame, tam):
    color = "green"
    if(valor < 0):
        color = "red"
    return Label(frame, text=str(round(valor,2))+" $", bg="#2d3e52", fg=color, font=("Arial", tam, "bold"))
def label_tiempo(tiempo, frame, tam):
    return Label(frame, text=str(round(tiempo,2))+ " mins | "+str(round(tiempo/60,2))+" hrs", bg="#2d3e52", fg="white", font=("Arial", tam, "bold"))

def dibujar_producto(p, canvas_sim):
    x = int((p.num-1)%50)*17+4
    y = int((p.num-1)/50)*17+4

    color = "cyan"
    if(p.estado == "N" and p.procesado_1):
        color = "green"
    if(p.estado == "D"):
        color = "red"
    if(p.estado == "R"):
        color = "orange"
    if(p.estado == "F"):
        color = "blue"
    if(p.estado == "C"):
        color = "purple"
    
    borde = "white"
    if((p.revisado_1 and (p.procesado_2 == False)) or p.revisado_2):
        borde = "black"

    canvas_sim.create_rectangle(x, y, x+14, y+14, fill=color, width=2, outline=borde)

def dibujar_cliente(c, canvas_sim):
    x = int((c.num-1)%50)*17+4
    y = int((c.num-1)/50)*17+4

    color = "cyan"
    if(c.satisfecho):
        color = "green"
    else:
        if(c.revisado):
            color = "red"
    
    borde = "white"
    if(c.vuelve):
        borde = "black"
    if(c.vuelve and c.satisfecho and(c.reembolsado==False)):
        if(c.producto.reparado):
            borde = "blue"
        else:
            borde = "orange"
    if(c.reembolsado):
        borde = "red"

    canvas_sim.create_oval(x, y, x+14, y+14, fill=color, width=2, outline=borde)

def dibujar_conv(canvas_conv, i, texto, color, borde, p):
    x = 10+(int(i/3)*300)
    y = 10+((i%3)*35)
    if(p):
        if(borde):
            canvas_conv.create_rectangle(x, y, x+24, y+24, outline=color, width=4)
        else:
            canvas_conv.create_rectangle(x, y, x+28, y+28, fill=color, width=0)
    else:
        if(borde):
            canvas_conv.create_oval(x, y, x+24, y+24, outline=color, width=4)
        else:
            canvas_conv.create_oval(x, y, x+28, y+28, fill=color, width=0)
    canvas_conv.create_text(x+100, y+14, text=texto, fill="white", font=("Arial", 14, "bold"))

def dibujar_convenciones(frm_sim, n):
    label("Convenciones", frm_sim, 14).grid(row=5, column=0, sticky="w")
    canvas_conv = Canvas(frm_sim, bg="#3d4e62", width="851", height="120", highlightthickness=0)
    canvas_conv.config(bg="#5d3e52")
    canvas_conv.grid(row=6, column=0, sticky="we", pady=10)

    if (n == 1):
        dibujar_conv(canvas_conv, 0, "En Bruto", "cyan", False, True)
        dibujar_conv(canvas_conv, 1, "Conforme", "green", False, True)
        dibujar_conv(canvas_conv, 2, "No Conforme", "Red", False, True)
        dibujar_conv(canvas_conv, 3, "Reprocesable", "orange", False, True)
        dibujar_conv(canvas_conv, 4, "Reparable", "blue", False, True)
        dibujar_conv(canvas_conv, 5, "Reclasificable", "purple", False, True)
        dibujar_conv(canvas_conv, 6, "revisado", "black", True, True)
        dibujar_conv(canvas_conv, 7, "No revisado", "white", True, True)
    
    if(n == 2):
        dibujar_conv(canvas_conv, 0, "Sin Producto", "cyan", False, False)
        dibujar_conv(canvas_conv, 1, "Satisfecho", "green", False, False)
        dibujar_conv(canvas_conv, 2, "No Satisfecho", "Red", False, False)
        dibujar_conv(canvas_conv, 3, "Garantía Repro.", "orange", True, False)
        dibujar_conv(canvas_conv, 4, "Garantía Repar.", "blue", True, False)
        dibujar_conv(canvas_conv, 5, "Reembolsado", "red", True, False)
        dibujar_conv(canvas_conv, 6, "Volvió", "black", True, False)
        dibujar_conv(canvas_conv, 7, "No Volvió", "white", True, False)

def obtener_datos(i):
    global productos0, productos5, clientes0
    global fabrica_1, fabrica_2, operario_1, operario_2, taller

    datos = ""
    if(i == 0):
        datos += "PRODUCTOS EN BRUTO "+"\n"
        datos += "\n"
        datos += "Total Productos ingresados: "+str(len(productos0))
    
    if(i == 1):
        datos += "OPERACIÓN 1 "+"\n"
        datos += "\n"
        datos += "Total Productos procesados: "+str(fabrica_1.procesados)+"\n"
        datos += "\n"
        datos += "Productos Conformes: "+str(fabrica_1.conformes)+"\n"
        datos += "Productos No Conformes: "+str(fabrica_1.no_conformes)+"\n"
        datos += "\n"
        datos += "Productos Desechables: "+str(fabrica_1.desechables)+"\n"
        datos += "Productos Reprocesables: "+str(fabrica_1.reprocesables)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(fabrica_1.tiempo_proceso/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(fabrica_1.costo_proceso,2))+" $"+"\n"

    if(i == 2):
        datos += "REVISIÓN 1 "+"\n"
        datos += "\n"
        datos += "Total Productos revisados: "+str(operario_1.revisados)+"\n"
        datos += "\n"
        datos += "Productos Aprobados: "+str(operario_1.aprobados)+"\n"
        datos += "Productos Desechados: "+str(operario_1.desechados)+"\n"
        datos += "Productos Reprocesados: "+str(operario_1.reprocesados)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(operario_1.tiempo_total/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(operario_1.costo_total,2))+" $"+"\n"
        datos += "\n"
        datos += "REPROCESOS 1 "+"\n"
        datos += "\n"
        datos += "Total Productos reprocesados: "+str(fabrica_1.reprocesados_prev)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(fabrica_1.tiempo_reproceso_prev/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(fabrica_1.costo_reproceso_prev,2))+" $"+"\n"

    if(i == 3):
        datos += "OPERACIÓN 2 "+"\n"
        datos += "\n"
        datos += "Total Productos procesados: "+str(fabrica_2.procesados)+"\n"
        datos += "\n"
        datos += "Productos Conformes: "+str(fabrica_2.conformes)+"\n"
        datos += "Productos No Conformes: "+str(fabrica_2.no_conformes)+"\n"
        datos += "\n"
        datos += "Productos Desechables: "+str(fabrica_2.desechables)+"\n"
        datos += "Productos Reprocesables: "+str(fabrica_2.reprocesables)+"\n"
        datos += "Productos Reparables: "+str(fabrica_2.reparables)+"\n"
        datos += "Productos Reclasificables: "+str(fabrica_2.reclasificables)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(fabrica_2.tiempo_proceso/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(fabrica_2.costo_proceso,2))+" $"+"\n"

    if(i == 4):
        datos += "REVISIÓN 2 "+"\n"
        datos += "\n"
        datos += "Total Productos revisados: "+str(operario_2.revisados)+"\n"
        datos += "\n"
        datos += "Productos Aprobados: "+str(operario_2.aprobados)+"\n"
        datos += "Productos Desechados: "+str(operario_2.desechados)+"\n"
        datos += "Productos Reprocesados: "+str(operario_2.reprocesados)+"\n"
        datos += "Productos Reparados: "+str(operario_2.reparados)+"\n"
        datos += "Productos Reclasificados: "+str(operario_2.reclasificados)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(operario_2.tiempo_total/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(operario_2.costo_total,2))+" $"+"\n"
        datos += "\n"
        datos += "REPROCESOS 2 "+"\n"
        datos += "\n"
        datos += "Total Productos reprocesados: "+str(fabrica_2.reprocesados_prev)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(fabrica_2.tiempo_reproceso_prev/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(fabrica_2.costo_reproceso_prev,2))+" $"+"\n"
        datos += "\n"
        datos += "REPARACIONES "+"\n"
        datos += "\n"
        datos += "Total Productos reparados: "+str(taller.reparados_prev)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(taller.tiempo_prev/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(taller.costo_prev,2))+" $"+"\n"

    if(i == 5):
        datos += "PRODUCTOS LISTOS PARA VENTA"+"\n"
        datos += "\n"
        datos += "Total productos: "+str(len(productos5))+"\n"
        datos += "\n"
        aux = 0
        for p in productos5:
            if(p.estado == "N"):
                aux+=1
        datos += "Conformes: "+str(aux)+"\n"
        aux = 0
        for p in productos5:
            if(p.estado == "D"):
                aux+=1
        datos += "Desechables: "+str(aux)+"\n"
        aux = 0
        for p in productos5:
            if(p.estado == "R"):
                aux+=1
        datos += "Reprocesables: "+str(aux)+"\n"
        aux = 0
        for p in productos5:
            if(p.estado == "F"):
                aux+=1
        datos += "Reparables: "+str(aux)+"\n"
        aux = 0
        for p in productos5:
            if(p.estado == "C"):
                aux+=1
        datos += "Reclasificables: "+str(aux)+"\n"
        datos += "\n"
        aux = 0
        for p in productos5:
            aux += p.valor
        datos += "Ganancias esperadas: "+str(aux)+" $"+"\n"
        aux = 0
        for p in productos5:
            aux += p.tiempo
        datos += "Tiempo Total Invertido: "+str(round(aux/60,2))+" hrs"+"\n"
        aux = 0
        for p in productos5:
            aux += p.costo
        datos += "Costo total: "+str(round(aux,2))+" $"+"\n"

    if(i == 6):
        datos += "CLIENTES COMPRANDO "+"\n"
        datos += "\n"
        datos += "Total Clientes: "+str(len(clientes0))

    if(i == 7):
        datos += "REACCIÓN CLIENTES "+"\n"
        datos += "\n"
        aux1 = 0
        aux2 = 0
        for c in clientes1:
            if(c.satisfecho):
                aux1 += 1
            else:
                aux2 += 1
        datos += "Satisfechos: "+str(aux1)+"\n"
        datos += "Insatisfechos: "+str(aux2)+"\n"
        datos += "\n"
        aux1 = 0
        aux2 = 0
        for c in clientes1:
            if(c.vuelve):
                aux1 += 1
            else:
                if(c.satisfecho == False):
                    aux2 += 1
        datos += "Reclamando: "+str(aux1)+"\n"
        datos += "Sin reclamar: "+str(aux2)+"\n"

    if(i == 8):
        datos += "ATENCIÓN DE RECLAMOS "+"\n"
        datos += "\n"
        aux1 = 0
        aux2 = 0
        aux3 = 0
        aux4 = 0
        for c in clientes2:
            if(c.reclamo_atendido):
                aux1 += 1
                if(c.producto.reparado):
                    aux2 += 1
                if(c.producto.reprocesado_2):
                    aux3 += 1
                if(c.reembolsado):
                    aux4 += 1
        datos += "Reclamos atendidos: "+str(aux1)+"\n"
        datos += "Reparados por Garantía: "+str(aux2)+"\n"
        datos += "Reprocesados por Garantía: "+str(aux3)+"\n"
        datos += "Reembolsados: "+str(aux4)+"\n"
        datos += "\n"
        datos += "REPROCESOS "+"\n"
        datos += "\n"
        datos += "Total Productos reprocesados: "+str(fabrica_2.reprocesados_posv)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(fabrica_2.tiempo_reproceso_posv/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(fabrica_2.costo_reproceso_posv,2))+" $"+"\n"
        datos += "\n"
        datos += "REPARACIONES "+"\n"
        datos += "\n"
        datos += "Total Productos reparados: "+str(taller.reparados_posv)+"\n"
        datos += "\n"
        datos += "Tiempo Invertido: "+str(round(taller.tiempo_posv/60,2))+" hrs"+"\n"
        datos += "Costo total: "+str(round(taller.costo_posv,2))+" $"+"\n"


    return datos


def dibujar_sim(frm_sim, siguiente, canvas_sim, lbl_est, lbl_des, txt_res):
    global pasos, paso

    lbl_est.config(text="Estado actual: En proceso "+pasos[paso][1])
    siguiente['state'] = DISABLED
    if(paso==2 or paso==6):
        canvas_sim.delete("all")
    if(paso==0):
        dibujar_convenciones(frm_sim, 1)
    if(paso==6):
        lbl_des.config(text="Cada uno de los circulos representa un cliente")
        dibujar_convenciones(frm_sim, 2)
    if(paso==5):
        pass
    else:
        for p in pasos[paso][0]:
            if(paso < 5):
                dibujar_producto(p, canvas_sim)
            else:
                dibujar_cliente(p, canvas_sim)
            canvas_sim.update()
    lbl_est.config(text="Estado actual: Finalizada "+pasos[paso][1])
    txt_res.delete("1.0","end")
    txt_res.insert(INSERT, obtener_datos(paso))
    
    paso += 1

    siguiente['state'] = NORMAL
    if(paso > 8):
        siguiente['command'] = mostrar_resultados_finales
        

def mostar_simulacion(fondo):
    frm_sim = Frame(fondo)
    frm_sim.config(bg="#2d3e52")
    frm_sim.grid(row=0, column=0)

    frm_res = Frame(fondo)
    frm_res.config(bg="#2d3e52")
    frm_res.grid(row=0, column=1, sticky="ns", pady=50, padx=10)

    label("Resultados:", frm_res, 20).grid(row=0, column=0)
    txt_res = Text(frm_res, bg="#0d3e52", fg="white", font=("Arial", 12), width="30", height="26")
    txt_res.grid(row=1, column=0)

    label("Simulación", frm_sim, 30).grid(row=0, column=0, sticky="n")

    lbl_estado = label("Estado actual: "+pasos[0][1], frm_sim, 15)
    lbl_estado.grid(row=1, column=0, sticky="ws", pady=10)

    canvas_sim = Canvas(frm_sim, bg="#3d4e62", width="851", height="341")
    canvas_sim.grid(row=2, column=0, sticky="we")

    descripcion = label("Cada uno de los cuadros representa un producto", frm_sim, 11)
    descripcion.grid(row=3, column=0, sticky="w")

    siguiente = Button(frm_sim, text="Siguiente", relief="flat", bg="#e67f22", fg="white", font=("Arial", 14, "bold"))
    siguiente['command'] = lambda arg1=frm_sim, arg2=siguiente, arg3=canvas_sim, arg4=lbl_estado, arg5=descripcion, arg6=txt_res : dibujar_sim(arg1 , arg2, arg3, arg4, arg5, arg6)
    siguiente.grid(row=4,column=0, pady=5)

    dibujar_sim(frm_sim, siguiente, canvas_sim, lbl_estado, descripcion, txt_res)

def label_res(frm, lbls, fil, col):
    for i in range(0, len(lbls)):
        label(lbls[i][0], frm, 15).grid(row=i+fil,column=col, sticky="e", padx=5)
        if(lbls[i][2]):
            label_valor(lbls[i][1], frm, 15).grid(row=i+fil,column=col+1, sticky="w")
        else:
            label_tiempo(lbls[i][1], frm, 15).grid(row=i+fil,column=col+1, sticky="w")

def mostrar_resultados_finales():
    global fondo, clientes2, productos5, taller, fabrica_2, fabrica_1, operario_2, operario_1

    ventas = 0
    for p in productos5:
        ventas += p.valor

    costos_prod = 0
    for p in productos5:
        costos_prod -= p.costo

    tiempo_prod = 0
    for p in productos5:
        tiempo_prod += p.tiempo

    perdidas_garan = -(fabrica_2.costo_reproceso_posv + taller.costo_posv)
    tiempo_garan = fabrica_2.tiempo_reproceso_posv + taller.tiempo_posv

    reembolso = 0
    for c in clientes2:
        if(c.reembolsado):
            reembolso -= c.producto.valor

    pbn = 0
    for c in clientes2:
        if((c.vuelve==False) and (c.satisfecho==False)):
            pbn -= 170000

    ganancias = ventas + costos_prod + perdidas_garan + reembolso
    ganancia_pp = ganancias/len(clientes2)
    precio_pp = ventas/len(clientes2)
    costo_pp = (costos_prod + perdidas_garan)/len(clientes2)
    tiempo_pp = (tiempo_prod + tiempo_garan)/len(clientes2)
    ganancias_pbn = ganancias + pbn

    for w in fondo.winfo_children():
        w.destroy()

    frm_res = Frame(fondo)
    frm_res.config(bg="#2d3e52")
    frm_res.grid(row=0, column=0)

    k = 0
    label("Resultados de la Simulación", frm_res, 30).grid(row=k,column=0, columnspan=4, sticky="we", pady=10)

    resultados = [
        ["Ganancias (sin PBN): ", ganancias, True],
        ["Ventas: ", ventas, True],
        ["Costos de Producción: ", costos_prod, True],
        ["Tiempo de Producción: ", tiempo_prod, False],
        ["Costos por Garantías: ", perdidas_garan, True],
        ["Tiempo de Procesos por Garantía: ", tiempo_garan, False],
        ["Perdidas por Reembolsos: ", reembolso, True],
        ["Perdida del Buen Nombre: ", pbn, True],
        ["Ganancias (con PBN): ", ganancias_pbn, True]]

    label_res(frm_res, resultados, 1, 0)

    resultados = [
        ["Ganancia Medio por Producto: ", ganancia_pp, True],
        ["Precio Medio por Producto: ", precio_pp, True],
        ["Costo Medio por Producto: ", costo_pp, True],
        ["Tiempo Medio por Producto: ", tiempo_pp, False]]

    label_res(frm_res, resultados, 1, 2)


    frm_graf = Frame(fondo)
    frm_graf.config(bg="#2d3e52")
    frm_graf.grid(row=1, column=0, pady=10)

    label("Tiempos de Produccion", frm_graf, 15).grid(row=0, column=0)
    label("Costos de Produccion", frm_graf, 15).grid(row=0, column=1)

    fram_t = Frame(frm_graf)
    fram_t.config(bg="#2d3e52")
    fram_t.grid(row=1, column=0, sticky="we")

    f_t = Figure(figsize=(4, 3), dpi=100 )
    f_t.patch.set_facecolor('#4d5e72')
    tiempos = [fabrica_1.tiempo_proceso,operario_1.tiempo_total,fabrica_2.tiempo_proceso,operario_2.tiempo_total]
    procesos = ["Operacion 1","Revision 1","Operacion 2","Revision 2"]
    f_t.add_subplot(111).pie(tiempos, labels=procesos, autopct="%0.1f %%")

    canvas_t = FigureCanvasTkAgg(f_t, master=fram_t)
    canvas_t.draw()  
    canvas_t.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    fram_c = Frame(frm_graf)
    fram_c.config(bg="#2d3e52")
    fram_c.grid(row=1, column=1, sticky="we")

    f_c = Figure(figsize=(4, 3), dpi=100 )
    f_c.patch.set_facecolor('#4d5e72')
    costos = [fabrica_1.costo_proceso,operario_1.costo_total,fabrica_2.costo_proceso,operario_2.costo_total]
    procesos = ["Operacion 1","Revision 1","Operacion 2","Revision 2"]
    f_c.add_subplot(111).pie(costos, labels=procesos, autopct="%0.1f %%")

    canvas_c = FigureCanvasTkAgg(f_c, master=fram_c)
    canvas_c.draw()  
    canvas_c.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


ventana = Tk()
ventana.geometry("1190x740")
ventana.config(bg="#2d3e52")
ventana.resizable(0,0)

fondo = Frame(ventana)
fondo.config(bg="#2d3e52")
fondo.pack(fill="both", expand="true", padx=20, pady=30)

mostar_simulacion(fondo)

ventana.mainloop()