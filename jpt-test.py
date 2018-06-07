# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 16:35:02 2018

@author: ic_admin
"""
import numba as nb
import math as m

def mod8sub(a,b): return (a - b + 4) % 8 - 4

@nb.jit(nb.i4[:](nb.i4[:],nb.i4))
def jpt_check(blocked, z): #blocked=(y1,y2,...), z=parent
    pruned = set()
    if z%2 == 0: #straight parent
        pruned.add((z+4)%8)
        for y in blocked:
            if m.fabs(mod8sub(y,z)) == 2: pruned.add(int(((y-z)%8/2+y)%8))
    else: #diagonal parent
        for i in range(3): pruned.add((z+i+3)%8)
        for y in blocked:
            if m.fabs(mod8sub(y,z)) == 1: pruned.add(int(((y-z)%8+y)%8))
    pruned = pruned.difference(blocked)
    return pruned