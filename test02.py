# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 15:31:08 2018

@author: ic_admin
"""

import pygame as pg
import traceback
import math as m
import numpy as np
from time import time
from queue import Queue, PriorityQueue
import cProfile

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()

class Engagement():
    def __init__(self, disp):
        self.disp = disp
        
        self.bgfile = "Assets\\cave01.png"
        self.bgimg = pg.image.load(self.bgfile)
        self.bgimg = pg.transform.scale(self.bgimg, tplmult(self.bgimg.get_rect().size, 2))
        
        self.cursorfiles = ("Assets\\ring-grn.png",
                            "Assets\\ring-grn-fill.png",
                            "Assets\\ring-red.png",
                            "Assets\\ring-red-fill.png")
        self.cursorimgs = []
        for file in self.cursorfiles:
            img = pg.image.load(file)
            self.cursorimgs.append(pg.transform.scale(img, tplmult(img.get_rect().size, 2)))
        
        self.mouse_hold = False
        self.t_mouse_hold = 0
        self.sc_loc = (0,0)
        
        self.activeunit = []
        self.unitlist = np.empty((0,1))
        self.loclist = None
        
    def add_unit(self, unit, loc):
        unit.loc = loc
        unit.engmt = self
        unit.eid = len(self.unitlist)
        self.unitlist = np.append(self.unitlist, unit)
        self.activeunit = unit
        
    def parse_input(self, event):
        #print(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.t_mouse_hold = time()
                self.mouse_hold = True
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.t_mouse_hold = time() - self.t_mouse_hold
                self.mouse_hold = False
                if self.t_mouse_hold < 0.2:
                    mpos_adj = tpldiff(pg.mouse.get_pos(), self.sc_loc)
                    color = self.disp.get_at(mpos_adj)
                    print(color)
                    if color[0] == 1:
                        self.activeunit = self.unitlist[color[1]]
                    if color[0] == 0:
                        self.activeunit.target = mpos_adj
        if event.type == pg.MOUSEMOTION:
            if self.mouse_hold: self.sc_loc = tplsum(self.sc_loc, event.rel)
                
    
    def check_locs(self):
        self.loclist = np.zeros((0,2))
        for unit in self.unitlist:
            self.loclist = np.append(self.loclist, np.array([unit.loc]), 0)
    
    def draw_cursor(self, loc, ally, select):
        idx = 2*(not ally) + select
        img = self.cursorimgs[idx]
        self.disp.blit(img, tplsum(tpldiff(loc, tplmult(img.get_rect().size,0.5,True)), self.sc_loc))
    
    def draw_tick(self):
        self.check_locs()
        self.disp.fill((0,0,0))
        #self.disp.fill((255,255,255))
        for unit in self.unitlist:
            unit.tick()
            pg.draw.ellipse(self.disp, (1, unit.eid, 0),
                            pg.Rect((unit.loc[0]-25, unit.loc[1]-15), (50,30)))
#    
#    def tick_units(self):
#        for unit in self.unitlist:
#            unit.tick()
            
    def draw_display(self):
        self.check_locs()
        #self.disp.fill((255,255,255))
        self.disp.fill((45, 16, 20))
        self.disp.blit(self.bgimg, tplsum((0,0), self.sc_loc))
        for unit in self.unitlist[np.argsort(self.loclist[:,1])]:
            if unit == self.activeunit: self.draw_cursor(unit.loc, 1, 1)
            else: self.draw_cursor(unit.loc, 1, 0)
            unit.draw()
        pg.display.update()
    
    def adjacent(self, origin):
        adj = []
        for th in np.arange(0, 2*m.pi, m.pi/4):
            waypoint = tplsum(origin, (int(2*m.cos(th)), int(2*m.sin(th))))
            color = self.disp.get_at(tuple(int(x) for x in waypoint))
            if color[0] == 0 and color[1] == 0:
                adj.append(waypoint)
        return adj
    
    def pathfind_bf(self, origin, target):
        frontier = Queue()
        frontier.put(origin)
        came_from = {}
        came_from[origin] = None
        
        while not frontier.empty():
            current = frontier.get()
            if tpldist(current, target) <= 3:
                target = current
                break
            for waypoint in self.adjacent(current):
                if waypoint not in came_from:
                    frontier.put(waypoint)
                    came_from[waypoint] = current
        
        current = target
        path = []
        while current != origin:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path
    
    def pathfind_astar(self, origin, target):
        frontier = PriorityQueue()
        frontier.put(origin, 0)
        came_from = {}
        cost_so_far = {}
        came_from[origin] = None
        cost_so_far[origin] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if tpldist(current, target) <= 3:
                target = current
                break
            
            for next in self.adjacent(current):
                new_cost = cost_so_far[current] + 1 #graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    if next not in came_from:
                        cost_so_far[next] = new_cost
                        priority = new_cost + tpldist(target, next)
                        frontier.put(next, priority)
                        came_from[next] = current
        
        current = target
        path = []
        while current != origin:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        return path
    
class Unit():
    def __init__(self):
        self.loc = None
        self.engmt = None
        self.eid = None
        
        self.pawnfile = "Assets\\basicV4-sheet.png"
        self.pawnsheet = pg.image.load(self.pawnfile)
        self.pawnsheet = pg.transform.scale(self.pawnsheet, tplmult(self.pawnsheet.get_rect().size, 2))
        self.pawndim = (80,120)
        self.pawn = pg.Surface(self.pawndim, pg.SRCALPHA)
        
        self.target = []
        self.path = []
        self.mvspd = 1
        
        self.animset = "stand"
        self.animsubframe = 0
        self.animframe = 0
    
    def tick(self):
        #Update animation frames
        self.animsubframe += 1
        if self.animsubframe >= 6:
            self.animsubframe = 0
            self.animframe += 1
        if self.animframe >= 4: self.animframe = 0
        
        #Update Location
        #cProfile.run(self.engmt.pathfind_bf(self.loc, self.target))
        if self.target: self.path = self.engmt.pathfind_bf(self.loc, self.target)
        if len(self.path) > 0:
            dist_wp = tpldist(self.loc, self.path[0])
            if dist_wp < self.mvspd:
                self.loc = self.path[0]
                self.path = self.path[1:]
            else:
                #print(tpldir(self.loc, self.path[0]))
                self.loc = tplsum(self.loc, tplmult(tpldir(self.loc, self.path[0]), self.mvspd))
        else: self.target = []
    
    def draw(self):
        #print(self.animframe)
        self.pawn.fill(pg.Color(0,0,0,0))
        self.pawn.blit(self.pawnsheet, (0,0), (0+self.pawndim[0]*self.animframe, 0, self.pawndim[0], self.pawndim[1]))
        self.engmt.disp.blit(self.pawn,
                             tplsum(tpldiff(self.loc, (self.pawndim[0]/2+3,101)), self.engmt.sc_loc))
        
def tplsum(a,b): return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b,return_int=False):
    if return_int: return tuple(m.floor(a[i]*b) for i in range(len(a)))
    else: return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))

def gameLoop():
    
    try:
        engmt = Engagement(gameDisplay)
        engmt.add_unit(Unit(), (200,200))
        engmt.add_unit(Unit(), (300,300))
        
        gameExit = False
        while not gameExit:
            
            engmt.draw_tick()
           # engmt.tick_units()
            
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                else: engmt.parse_input(event)
            
            engmt.draw_display()
                        
            clock.tick(30)
            
    except Exception as e:
        traceback.print_exc()
        return e
            
e = gameLoop()
pg.quit()