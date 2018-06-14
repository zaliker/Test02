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
from queue import PriorityQueue
import random
#import numba as nb
#import cProfile

pf_test = []

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()


class Engagement():
    def __init__(self, disp):
        self.disp = disp
        self.mask = {}
        self.mask["allies"] = pg.mask.Mask((800,600))
        self.mask["enemies"] = pg.mask.Mask((800,600))
        self.mask["map"] = pg.mask.Mask((800,600))
        self.mask["all"] = pg.mask.Mask((800,600))
        
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
        #self.activeunit = unit
        
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
                    #color = self.disp.get_at(mpos_adj)
                    #print(color)
                    if self.mask["allies"].get_at(mpos_adj):
                        select_dist = None
                        for unit in self.unitlist:
                            dist = tpldist(mpos_adj, unit.loc)
                            if select_dist:
                                if dist < select_dist:
                                    select_dist = dist
                                    self.activeunit = unit
                            else:
                                select_dist = dist
                                self.activeunit = unit
                    else:
                        if self.activeunit:
                            self.activeunit.target = mpos_adj
                            self.activeunit.pathcheck = 10
        if event.type == pg.MOUSEMOTION:
            if self.mouse_hold: self.sc_loc = tplsum(self.sc_loc, event.rel)
        if event.type == pg.KEYDOWN:
            if event.key == 109:
                self.activeunit.target = (400,300)
                
    
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
            
    def draw_masks(self):
        self.mask["allies"].clear()
        for unit in self.unitlist:
            unit.tick()
            self.mask["allies"].draw(unit.mask, tplint(tpldiff(unit.loc, tplmult(unit.maskdim, 0.5))))
        #print(self.mask["all"].get_at(pg.mouse.get_pos()))
        self.mask["all"].clear()
        self.mask["all"].draw(self.mask["allies"], (0,0))
        self.mask["all"].draw(self.mask["enemies"], (0,0))
        self.mask["all"].draw(self.mask["map"], (0,0))
        pg.draw.lines(self.disp, (200,150,150), 1, self.mask["allies"].outline())
            
    def draw_display(self):
        self.check_locs()
        #self.disp.fill((255,255,255))
        self.disp.fill((45, 16, 20))
        self.disp.blit(self.bgimg, tplsum((0,0), self.sc_loc))
        for unit in self.unitlist[np.argsort(self.loclist[:,1])]:
            unit.draw()
            pg.draw.lines(self.disp, (200,150,150), 1, unit.mask.outline())
#            pg.draw.ellipse(self.disp, (1, unit.eid, 0),
#                            pg.Rect((unit.loc[0]-25, unit.loc[1]-15), (50,30)))
        pg.display.update()
    
    def adj_set(self, S):
        return set(((S, 0), (S, -S), (0, -S), (-S, -S), (-S, 0), (-S, S), (0, S), (S, S)))
    
    def adjacent(self, current, s, unitmask, pathmask):
        adj = set()
        for next in self.adj_set(s):
#            if not pathmask.get_at(tplint(tplsum(origin, next))):
#                adj.add(tplsum(origin, next))
            if self.moveable(current, tplsum(current, next), unitmask, pathmask):
                adj.add(tplsum(current, next))
        #print("adj:", adj)
        return adj
    
    def moveable(self, origin, target, unitmask, pathmask):
        
        step = origin
        heading = tpldir(origin, target)
        
        moveable = True
        while moveable:
            step = tplsum(step, heading)
            if pathmask.overlap(unitmask, tplint(tpldiff(step, tplmult(unitmask.get_size(), 0.5)))):
                moveable = False
            if tpldist(step, target) <= 1: break
        
        return moveable
    
    def move_cost(self, current, next):
        return tpldist(current, next)
      
    #Find path from <unit.loc> to <target> using the A* algorithm
    def pathfind_astar(self, unit,  loc, target, s):
        origin = loc
        pathmask = self.mask["all"]
        pathmask.erase(unit.mask, tplint(tpldiff(unit.loc, tplmult(unit.maskdim, 0.5))))
        
        frontier = PriorityQueue()
        frontier.put((0, origin))
        came_from = {}
        cost_so_far = {}
        came_from[origin] = None
        cost_so_far[origin] = 0
        
        i = 0
        while not frontier.empty():
            current = frontier.get()[1]
            
            i+=1
            if i > 10000: break
            
            if current == target: break
            
            if tpldist(current, target) <= m.sqrt(2)*s:
                came_from[target] = current
                #target = current
                break
            
#            try: self.adjacent(current, s, pathmask)
#            except: traceback.print_exc()
            #print("current:", current)
            for next in self.adjacent(current, s, unit.mask, pathmask):
                new_cost = cost_so_far[current] + self.move_cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    if next not in came_from:
                        cost_so_far[next] = new_cost
                        priority = new_cost + tpldist(next, target)
                        frontier.put((priority, next))
                        came_from[next] = current
        
        #print(None)
        current = target
        path = []
        while current != origin:
            path.append(current)
            try: current = came_from[current]
            except:
                traceback.print_exc()
                #print(came_from)
        path.reverse()
        
        return path
    
class Unit():
    def __init__(self):
        self.loc = None
        self.engmt = None
        self.eid = None
        
        #Define pawn animation set
        self.pawnfile = "Assets\\basicV5-sheet.png"
        self.pawnsheet = pg.image.load(self.pawnfile)
        self.pawnsheet = pg.transform.scale(self.pawnsheet, tplmult(self.pawnsheet.get_rect().size, 2))
        self.pawndim = (80,120)
        self.pawn = pg.Surface(self.pawndim, pg.SRCALPHA)
        
        self.target = []
        self.path_course = []
        self.path = []
        self.mvspd = 2
        
        self.maskdim = (50,30)
        self.mask = pg.Surface(self.maskdim, pg.SRCALPHA)
        pg.draw.ellipse(self.mask, (0,0,0), pg.Rect((0,0), self.maskdim))
        self.mask = pg.mask.from_surface(self.mask)
        
        self.animset = "stand"
        self.animsubframe = 0
        self.animframe = 0
        
        #self.animtile = (40,60)
        self.animattr = {} #index and duration of animation
        self.animattr["stand"] = (0,4)
        self.animattr["run"] = (1,6)
        
        self.pathcheck = 0
    
    def tick(self):
        #update animation set
        if self.animset != "run" and self.target:
            self.animset = "run"
            self.animframe = 0
        if self.animset != "stand" and not self.target:   
            self.animset = "stand"
        
        #Update animation frames
        self.animsubframe += 1
        if self.animsubframe >= 6:
            self.animsubframe = 0
            self.animframe += 1
        if self.animframe >= self.animattr[self.animset][1]: self.animframe = 0
        
        #Check path
        #print(self.loc)
        if self.target:
            try:
                self.path_course = self.engmt.pathfind_astar(self, self.loc, self.target, 3)
                
                pathmask = self.engmt.mask["all"]
                pathmask.erase(self.mask, tplint(tpldiff(self.loc, tplmult(self.maskdim, 0.5))))
                last_visible = -1
                for waypoint in self.path_course:
                    if self.engmt.moveable(self.loc, waypoint, self.mask, pathmask): last_visible += 1
                    else: break
                #numwp = len(self.path_course)
                #print("last: ", last_visible, ", numwp: ", numwp-1)
                self.path = [self.path_course[last_visible]]
#                if last_visible == (numwp-1): self.path = [self.target]
#                else: self.path = self.engmt.pathfind_astar(self, self.loc, self.path_course[min(1,numwp-1)], 3)
#                elif last_visible <= 0: self.engmt.pathfind_astar(self, self.loc, self.path_course[-1], 3)
##                else:
##                    start_loc = self.path_course[max(0, mve_idx - 1)]
##                    end_loc = self.path_course[mve_idx + 1]
##                    self.path = self.path_course[:mve_idx]
##                    self.path += self.engmt.pathfind_astar(self, start_loc, end_loc, 3)
#                else: self.path = self.path_course
            except: traceback.print_exc()
            #print(self.path)
        
        #Update location
        mvmt = self.mvspd
        while mvmt > 0 and self.path:
            dist_wp = tpldist(self.loc, self.path[0])
            if dist_wp <= mvmt:
                self.loc = self.path[0]
                self.path = self.path[1:]
                mvmt -= dist_wp
            else:
                self.loc = tplsum(self.loc, tplmult(tpldir(self.loc, self.path[0]), self.mvspd))
                mvmt = 0
        #self.loc = tplint(self.loc)
        if not self.path: self.target = []
        
    def draw(self):
        #print(self.animframe)
        if self == self.engmt.activeunit: self.engmt.draw_cursor(self.loc, 1, 1)
        else: self.engmt.draw_cursor(self.loc, 1, 0)
        self.pawn.fill(pg.Color(0,0,0,0))
        self.pawn.blit(self.pawnsheet, (0,0), (self.pawndim[0]*self.animframe, self.pawndim[1]*self.animattr[self.animset][0], self.pawndim[0], self.pawndim[1]))
        self.engmt.disp.blit(self.pawn,
                             tplsum(tpldiff(self.loc, (self.pawndim[0]/2+3,101)), self.engmt.sc_loc))
        #pg.draw.lines(self.engmt.disp, (200,150,150), 1, self.mask.outline())
        
def tplsum(a,b): return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b,return_int=False): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b,return_int=False):
    if return_int: return tuple(int(a[i]*b) for i in range(len(a)))
    else: return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))
def tplint(a): return tuple(int(a[i]) for i in range(len(a)))
def sign(x): return (x > 0) - (x < 0)
def mod8sub(a,b): return (a - b + 4) % 8 - 4

def jpt_check(blocked, z): #blocked=(y1,y2,...), z=parent
    pruned = set()
    if z%2 == 0: #straight parent
        pruned.add(int((z+4)%8))
        for y in blocked:
            if m.fabs(mod8sub(y,z)) == 2: pruned.add(int(((y-z)%8/2+y)%8))
    else: #diagonal parent
        for i in range(3): pruned.add(int((z+i+3)%8))
        for y in blocked:
            if m.fabs(mod8sub(y,z)) == 1: pruned.add(int(((y-z)%8+y)%8))
    pruned = pruned.difference(blocked)
    return pruned

def gameLoop():
    
    try:
        engmt = Engagement(gameDisplay)
        engmt.add_unit(Unit(), (350,200))
        engmt.add_unit(Unit(), (350,250))
        
        t_fps = pg.time.get_ticks()
        frameticks = 0
        
        gameExit = False
        
#        engmt.activeunit = engmt.unitlist[0]
#        engmt.activeunit.target = (350, 300)
        
        while not gameExit:
            
            #engmt.draw_tick()
            engmt.draw_masks()
            #engmt.tick_units()
            
#            result = [[],[]]
#            for i in range(25, 100):
#                origin = (300,400)
#                th = random.random()*2*m.pi
#                target = tplsum(origin,(i*m.cos(th), i*m.sin(th)))
#                print(i, origin, target)
#                t0 = time()
#                engmt.pathfind_astar(origin, target)
#                t1 = time()
#                engmt.pathfind_jpt(origin, target)
#                t2 = time()
#                result[0].append(t1-t0)
#                result[1].append(t2-t1)
#            return result
           
           
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == 27):
                    gameExit = True
                else: engmt.parse_input(event)
            
            engmt.draw_display()
                        
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