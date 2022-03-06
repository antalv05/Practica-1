#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 19:11:09 2022

@author: antalv05
"""


from multiprocessing import Process
from multiprocessing import Semaphore
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep

import random
#los productores producen en un array común. Solo hay un consumidor que 
#escoge el producto de menor valor y lo guarda en otro.

N = 4
NPROD = 5

#función para que el productor produzca.
def add_data(almacen, pid, data): 
    almacen[pid] = data
    #sleep(random.random()/3)

#fución para que el consumidor consuma.    
def get_data(almacen):
    otro=[0]*len(almacen)
    maximo=max(almacen)
    for i in range (len(almacen)):
        if almacen[i]==-1:
            otro[i]=maximo+1
        else:
            otro[i]=almacen[i]
    min_almacen = otro[0]
    posicion=0
    for i in range(1,len(otro)):
        if otro[i] < min_almacen and otro[i]!=-1:
            min_almacen = otro[i]
            posicion = i
    return min_almacen, posicion
        
    
        
    
        
def producer(almacen, pid, sem_empty, sem_nonempty, running, N_prod):
    #print("funcion producer")
    #el productor va produciendo en orden creciente valores arbitrarios.
    v = random.randint(0,5)
    while running[pid]: 
        #print("bucle running")
        print (f"producer {current_process().name} produciendo")
        sleep(random.random()/3)
        v += random.randint(0,5) #orden creciente!!
        sem_empty[pid].acquire() #wait, el productor espera a que su buffer este vacio.
        add_data(almacen, pid, v) #el productor produce.
        print (f"producer {current_process().name} produciendo {almacen[pid]}")
      

        sem_nonempty[pid].release() #signal, el productor_i ha producido y lo almacena.
        
        print (f"producer {current_process().name} almacenado {v}")
        
        N_prod[pid] -= 1 #la lista de producciones se rebaja en una.
        if N_prod[pid] == 0:
            almacen[pid] = -1 #cuando ya acaba de producir (acaba el running), ya no produce
            #y debe poner un -1, para avisar al consumidor de que ha acabado.
            running[pid] = 0
            print(f"producer {current_process().name}            terminado") 
            
def consumer(almacen, sem_empty, sem_nonempty, running):
    #print("funcion consumer")
    #tiene que gacer un for esperando a que produzcan todos 1, y luego empieza a consumir..
    #si siguen produciendo un array de trues. Si el min es -1, ese False. 
    #Y al calcular min no tengas en cuenta
    for i in range(NPROD):
        sem_nonempty[i].acquire() #wait, debe esperar a que todos consumen
    while 1 in running:
        #print("bucle consumer")
        print (f"consumer {current_process().name} desalmacenando")
        dato, posicion = get_data(almacen) #consume el minimo de todos los producidos.
        sem_empty[posicion].release() #signal, como ya puede consumir, consume, 
        #y avisa al productor de que debe consumir otra vez.
        print (f"consumer {current_process().name} consumiendo {dato}")
        sleep(random.random()/3)
        #sem_empty[posicion].release()
        sem_nonempty[posicion].acquire() #wait, debe esperar a que el productor
        #vuelva a producir.
    print (f" STOP {current_process().name}  ya no puede consumir,todos los productores acabaron de producir!!")


def main():
    almacen= Array('i', NPROD) #tiene tamaño NPROD*N
    #index = Value('i', 0)
    running = Array('i', NPROD)
    N_prod = Array('i', NPROD)
    for i in range(NPROD):
        almacen[i] = 0
        running[i] = 1
        N_prod[i] = N
    print ("almacen inicial", almacen[:])

    sem_emptyArr=[]
    sem_nonemptyArr=[]
    for i in range(NPROD):
        non_emptyArr = Semaphore(0)
        emptyArr = Semaphore(1)
        sem_emptyArr.append(emptyArr)
        sem_nonemptyArr.append(non_emptyArr)

    prodlist = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(almacen, i, sem_emptyArr, sem_nonemptyArr, running, N_prod))
                for i in range(NPROD) ]

    conslist = [ Process(target=consumer,
                      name="cons",
                      args=(almacen, sem_emptyArr, sem_nonemptyArr, running))]

    for p in prodlist + conslist:
        p.start()

    for p in prodlist + conslist:
        p.join()


if __name__ == '