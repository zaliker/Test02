# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 10:42:34 2018

@author: ic_admin
"""
import pygame as pg
from queue import PriorityQueue
import math as m
import traceback
import imageio
import numpy as np
import numba as nb
from time import time
import jps
import matplotlib.pyplot as plt

#def adj_tpl(S):
#    return ((S, 0), (S, -S), (0, -S), (-S, -S), (-S, 0), (-S, S), (0, S), (S, S))
def adj_set(S): return set(adj_tpl(S))


def tplsum(a,b):
    return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b,return_int=False):
    if return_int: return tuple(m.floor(a[i]*b) for i in range(len(a)))
    else: return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))
def tplint(a): return tuple(int(a[i]) for i in range(len(a)))
def sign(x): return (x > 0) - (x < 0)
def mod8sub(a,b): return (a - b + 4) % 8 - 4

def adj_tpl(S): return ((S, 0), (S, -S), (0, -S), (-S, -S), (-S, 0), (-S, S), (0, S), (S, S))

@nb.jit#(nb.i4[:,:](nb.i4[:], nb.b1[:,:], nb.i4))
def adjacent(origin, pathmask, S):
    adj = []
    for next in ((S, 0), (S, -S), (0, -S), (-S, -S), (-S, 0), (-S, S), (0, S), (S, S)):
        next = (origin[0]+next[0], origin[1]+next[1])
        if pathmask[next]:
            adj.append(next)
    return adj

#def adjacent(origin, pathmask):
#    adj = set()
#    for next in adj_set(3):
#        if pathmask[tplsum(origin, next)]:
#            adj.add(tplsum(origin, next))
#    return adj

def adj_jpt(current, prev):
    if not prev:
        adj = adjacent(current)
    else:
        delta_current = tpldiff(current, prev)
        adj = set()
        for delta_next in adj_set(1):
            if all(delta_current[i]!=0 for i in range(2)): #Check for parent diagonality
                if any(delta_current[i]==delta_next[i] for i in range(2)):
                    if all(delta_current[i]*delta_next[i]>=0 for i in range (2)):
                        adj.add(tplsum(current, delta_next))
            else:
                if all(delta_current[i]==delta_next[i] for i in range(2)):
                    adj.add(tplsum(current, delta_next))
    #print(adj)
    return adj

def move_cost(current, next):
    return tpldist(current, next)

def moveable(current, target, pathmask):
    None

def pathfind_astar(origin, target, pathmask, S):
    frontier = PriorityQueue()
    frontier.put((0, origin))
    came_from = {}
    cost_so_far = {}
    came_from[origin] = None
    cost_so_far[origin] = 0
    
    while not frontier.empty():
        current = frontier.get()[1]
        #print(current)
        if tpldist(current, target) <= m.sqrt(2)*S:
            came_from[target] = current
            #target = current
            break
        
#        try: self.adj_jpt(current, came_from[current])
#        except: print('no')
        
        for next in adjacent(current, pathmask, S):#adj_jpt(current, came_from[current]):
            new_cost = cost_so_far[current] + move_cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                if next not in came_from:
                    cost_so_far[next] = new_cost
                    priority = new_cost + tpldist(next, target)
                    frontier.put((priority, next))
                    came_from[next] = current
    
    current = target
    path = []
    while current != origin:
        path.append(current)
        try: current = came_from[current]
        except: None
    path.reverse()
    
    return path

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()

def gameLoop():
    
    try:

        t_fps = pg.time.get_ticks()
        frameticks = 0
        cpu_pct = 0
        
        blob_loc = (400,300)
        #blob_loc = (0,0)
        target = []
        path = []
        mvspd = 5
        def blob(loc):
            pg.draw.ellipse(gameDisplay, (0,0,255), pg.Rect(loc[0]-5, loc[1]-5, 9, 9))
        #target = (556, 477)
        
        bgimg = pg.image.load("Test Assets\\testmap02.png")
        bgrgb = np.array(imageio.imread("Test Assets\\testmap02.png"))
        bgbool = np.transpose(np.sum(bgrgb, axis=2)!=0)
        
        jps_field = jps.load_path_image("Test Assets\\testmap02.png", path_colour=0xFFFFFF)
        jps.jps(jps_field, blob_loc[0], blob_loc[1], 700, 300)
        
        print(bgbool[(0,0)])
        
        gameExit = False
        while not gameExit:
            t0 = time()
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        target = pg.mouse.get_pos()
                        print(bgbool[pg.mouse.get_pos()])
                        #target = (556, 477)
            
            if target:
                path = pathfind_astar(tplint(blob_loc), target, bgbool, 10)
                #path = jps.jps(jps_field, int(blob_loc[0]), int(blob_loc[1]), target[0], target[1])
                
            
            remaining = mvspd
            while remaining > 0 and path:
                dist_wp = tpldist(blob_loc, path[0])
                if dist_wp <= remaining:
                    blob_loc = path[0]
                    path = path[1:]
                    remaining -= dist_wp
                else:
                    blob_loc = tplsum(blob_loc, tplmult(tpldir(blob_loc, path[0]), mvspd))
                    remaining = 0
#                blob_loc = path[0]
#                path = path[1:]
            if not path: target = []
            
            gameDisplay.fill((255,255,255))
            gameDisplay.blit(bgimg, (0,0))
            blob(blob_loc)
            pg.display.update()
            
            t1 = time()
            clock.tick(30)
            
            cpu_pct = 0.1*cpu_pct + 0.9*((t1-t0)/(time()-t0)*100)
            frameticks += 1
            if frameticks > 15:
                print("FPS: %f"%(15*1000./(pg.time.get_ticks()-t_fps)))
                #print("CPU: %.2f"%cpu_pct)
                t_fps = pg.time.get_ticks()
                frameticks = 0
            
    except Exception as e:
        traceback.print_exc()
        return e
    
    return jps_field
            
e = gameLoop()
pg.quit()