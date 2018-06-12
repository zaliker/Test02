# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 10:42:34 2018

@author: ic_admin
"""
import pygame as pg
from queue import PriorityQueue
import math as m
import traceback

def adj_tpl(S):
    return ((S, 0), (S, -S), (0, -S), (-S, -S), (-S, 0), (-S, S), (0, S), (S, S))
def adj_set(S): return set(adj_tpl(S))

def tplsum(a,b): return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b,return_int=False):
    if return_int: return tuple(m.floor(a[i]*b) for i in range(len(a)))
    else: return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))
def sign(x): return (x > 0) - (x < 0)
def mod8sub(a,b): return (a - b + 4) % 8 - 4

def adjacent(origin):
    adj = set()
    for next in adj_set(7):
        adj.add(tplsum(origin, next))
    return adj

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

def pathfind_astar(origin, target):
    frontier = PriorityQueue()
    frontier.put((0, origin))
    came_from = {}
    cost_so_far = {}
    came_from[origin] = None
    cost_so_far[origin] = 0
    
    while not frontier.empty():
        current = frontier.get()[1]
        #print(current)
        if tpldist(current, target) <= 3:
            came_from[target] = came_from[current]
            target = current
            break
        
#        try: self.adj_jpt(current, came_from[current])
#        except: print('no')
        
        for next in adjacent(current):#adj_jpt(current, came_from[current]):
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
        
        blob_loc = (400,300)
        #blob_loc = (0,0)
        target = []
        path = []
        def blob(loc):
            pg.draw.ellipse(gameDisplay, (0,0,255), pg.Rect(loc[0]-5, loc[1]-5, 10, 10))
        target = (556, 477)
        
        gameExit = False
        while not gameExit:
           
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        target = pg.mouse.get_pos()
                        #target = (556, 477)
            
            if target:
                path = pathfind_astar(blob_loc, target)
            
            if path:
                #print(path)
                blob_loc = path[0]
                path = path[1:]
            
            gameDisplay.fill((255,255,255))
            blob(blob_loc)
            pg.display.update()
                        
            clock.tick(30)
            
            frameticks += 1
            if frameticks > 15:
                print("FPS: %f"%(15*1000./(pg.time.get_ticks()-t_fps)))
                t_fps = pg.time.get_ticks()
                frameticks = 0
            
    except Exception as e:
        traceback.print_exc()
        return e
            
e = gameLoop()
pg.quit()