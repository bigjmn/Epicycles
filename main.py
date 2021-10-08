import sys
import pygame as pg
from pygame.locals import *

from FourierTransform import fourierdata
from createmodel import Ladder

def run():
    pg.init()



    fps = 60
    fpsClock = pg.time.Clock()
    screen = pg.display.set_mode((1008,604))

    drawpanel = pg.Surface((500,500))
    drawpanel.fill((255,255,255))
    screen.blit(drawpanel, (2,2))
    left_border = drawpanel.get_rect()

    cyclepanel = pg.Surface((500,500))
    cyclepanel.fill((200,200,200))
    screen.blit(cyclepanel,(504,2))



    flag = False
    drawmode = True

    pointlist = []

    oldposx = 0
    oldposy = 0
    newposx = 0
    newposy = 0

    dim = cyclepanel.get_size()

    trace_surface = pg.Surface(dim)
    trace_surface.fill((255,255,255))
    trace_surface.set_colorkey((255,255,255))

    fourier = None

    marker = 0

    while drawmode == True:

        for event in pg.event.get():

            if event.type == QUIT:
                pg.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN:
                flag = True
                oldpos = pg.mouse.get_pos()
                newpos = pg.mouse.get_pos()

                pg.draw.circle(screen, (0,0,0),newpos, 2)

            if event.type == MOUSEMOTION:
                if flag == False:
                    continue
                oldpos = newpos
                newpos = pg.mouse.get_pos()
                marker += 1
                if marker%15 == 0:
                    pointlist.append(newpos)
                pg.draw.line(screen, (0,0,0), oldpos, newpos,4)

            if event.type == MOUSEBUTTONUP:
                flag = False
                pointlist.append(pg.mouse.get_pos())
                print(len(pointlist))

                if len(pointlist) < 3:
                    pointlist = []
                    drawpanel.fill((255,255,255))
                    continue

                drawmode = False
                fourier_points = fourierdata(pointlist,2*len(pointlist))
                print(fourier_points)
                fourier = Ladder(fourier_points, (0,0))




        pg.display.flip()



        fpsClock.tick(fps)

    while drawmode == False:


        cyclepanel.fill((255,255,255))

        start_tip = fourier.get_tip()

        for i in range(1,len(fourier.ladder)-1):
            pg.draw.line(cyclepanel, (0,255,0),fourier.ladder[i].get_pos(),
                         fourier.ladder[i+1].get_pos(),4)
            pg.draw.circle(cyclepanel,(0,0,255),fourier.ladder[i].get_pos(),2)

        fourier.ladderstep(.1) #make the rate 1 frame for simplicity
        end_tip = fourier.get_tip()
        pg.draw.line(trace_surface,(0,0,0),start_tip, end_tip, 4)
        cyclepanel.blit(trace_surface,(0,0))
        screen.blit(cyclepanel,(504,2))

            #exit pygame after sim/display quit
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()


        pg.display.flip()
        fpsClock.tick(fps)




run()
