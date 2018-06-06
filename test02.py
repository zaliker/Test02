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

pg.init()

W = 800
H = 600
gameDisplay = pg.display.set_mode((W,H))
pg.display.set_caption('Test Window')

clock = pg.time.Clock()

class Engagement():
    def __init__(self, disp):
        self.disp = disp
        
        self.bgfile = "bridge01.jpg"
        self.bgimg = pg.image.load(self.bgfile)
        self.cursorfile = "hex2.png"
        self.cursorimg = pg.transform.scale(pg.image.load(self.cursorfile), (50,30))
        
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
                        self.activeunit.path.append(mpos_adj)
        if event.type == pg.MOUSEMOTION:
            if self.mouse_hold: self.sc_loc = tplsum(self.sc_loc, event.rel)
                
    
    def check_locs(self):
        self.loclist = np.zeros((0,2))
        for unit in self.unitlist:
            self.loclist = np.append(self.loclist, np.array([unit.loc]), 0)
    
    def draw_cursor(self, loc):
        self.disp.blit(self.cursorimg, tplsum(tpldiff(loc, (25,15)), self.sc_loc))
    
    def draw_iocheck(self):
        self.check_locs()
        self.disp.fill((0,0,0))
        #self.disp.fill((255,255,255))
        for unit in self.unitlist:
            pg.draw.ellipse(self.disp, (1, unit.eid, 0),
                            pg.Rect((unit.loc[0]-25, unit.loc[1]-15), (50,30)))
        #pg.display.update()
    
    def draw_display(self):
        self.check_locs()
        self.disp.fill((255,255,255))
        self.disp.blit(self.bgimg, tplsum((0,0), self.sc_loc))
        for unit in self.unitlist[np.argsort(self.loclist[:,1])]:
            unit.tick()
            if unit == self.activeunit: self.draw_cursor(unit.loc)
            unit.draw()
        pg.display.update()
    
class Unit():
    def __init__(self):
        self.loc = None
        self.engmt = None
        self.eid = None
        
        self.pawnfile = "sprite.png"
        self.pawnimg = pg.image.load(self.pawnfile)
        
        self.path = []
        self.mvspd = 5
    
    def draw_pawn(self, loc):
        self.engmt.disp.blit(self.pawnimg, tpldiff(loc, (25,75)))
    
    def tick(self):
        if len(self.path) > 0:
            dist_wp = tpldist(self.loc, self.path[0])
            if dist_wp < self.mvspd:
                self.loc = self.path[0]
                self.path = self.path[1:]
            else:
                print(tpldir(self.loc, self.path[0]))
                self.loc = tplsum(self.loc, tplmult(tpldir(self.loc, self.path[0]), self.mvspd))
    
    def draw(self):
        self.draw_pawn(tplsum(self.loc, self.engmt.sc_loc))
        
def tplsum(a,b): return tuple(a[i]+b[i] for i in range(len(a)))
def tpldiff(a,b): return tuple(a[i]-b[i] for i in range(len(a)))
def tplmult(a,b): return tuple(a[i]*b for i in range(len(a)))
def tpldist(a,b): return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
def tpldir(a,b): return tuple(tplmult(tpldiff(b,a),1/tpldist(a,b)))

def gameLoop():
    
    try:
        engmt = Engagement(gameDisplay)
        engmt.add_unit(Unit(), (200,200))
        engmt.add_unit(Unit(), (300,300))
        
        gameExit = False
        while not gameExit:
            engmt.draw_iocheck()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    gameExit = True
                else: engmt.parse_input(event)
            
            engmt.draw_display()
            clock.tick(30)
            
    except Exception as e:
        traceback.print_exc()
        return e
            
e = gameLoop()
pg.quit()