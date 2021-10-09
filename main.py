import sys

import pygame as pg
from pygame.locals import *

from FourierTransform import fourierdata
from createmodel import Ladder

def run():

#   outermost loop, things I only have to call once
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

    #refresh button
    refreshbutton = pg.image.load('refresh-icon.png')


    iconholder = pg.Surface((100,100))
    iconholder.fill((0,255,0))
    iconholder.blit(refreshbutton,(0,0))

    screen.blit(iconholder, (451,504))
    button = pg.Rect(451,504,100,100)
    print(button)



    while True:

        flag = False
        drawmode = True

        pointlist = []

        oldpos = (0,0)
        newpos = (0,0)

        drawpanel.fill((255,255,255))
        screen.blit(drawpanel, (2,2))

        cyclepanel.fill((200,200,200))
        screen.blit(cyclepanel,(504,2))

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

                    oldpos = pg.mouse.get_pos()
                    newpos = pg.mouse.get_pos()
                    #if click in the drawing canvas, start drawing
                    if left_border.collidepoint(oldpos):
                        flag = True
                        pointlist.append(newpos)

                        pg.draw.circle(screen, (0,0,0),newpos, 2)

                if event.type == MOUSEMOTION:
                    if flag == False:
                        continue
                    oldpos = newpos
                    newpos = pg.mouse.get_pos()
                    #don't let mouse outside drawing boundary
                    if left_border.collidepoint(newpos) == False:
                        pg.mouse.set_pos(oldpos)
                        newpos = oldpos
                        continue

                    #only log every 15 points. if there are too many
                    #points, computation takes too long and the epicycles
                    #will be to small to follow. And that's no fun.
                    marker += 1
                    if marker%15 == 0:
                        pointlist.append(newpos)
                    pg.draw.line(screen, (0,0,0), oldpos, newpos,4)

                if event.type == MOUSEBUTTONUP:
                    #if drawing hasn't started yet, ignore
                    if flag == False:
                        continue
                    #end drawing
                    flag = False
                    #add last point so nothing gets completely cut off.
                    pointlist.append(pg.mouse.get_pos())

                    #basically if they click accidentally, don't run it
                    if len(pointlist) < 3:
                        pointlist = []
                        drawpanel.fill((255,255,255))
                        continue

                    #ready for animation!
                    drawmode = False
                    #transform list of points to array of rotating arms

                    fourier_points = fourierdata(pointlist,2*len(pointlist))
                    #configure the model
                    fourier = Ladder(fourier_points, (0,0))




            pg.display.flip()



            fpsClock.tick(fps)

        while drawmode == False:

            #this is the surface the model arms are on
            #it gets cleared ever frame
            cyclepanel.fill((255,255,255))

            #track where tip starts to trace line
            start_tip = fourier.get_tip()
            #update arms
            for i in range(1,len(fourier.ladder)-1):
                pg.draw.line(cyclepanel, (0,255,0),fourier.ladder[i].get_pos(),
                             fourier.ladder[i+1].get_pos(),4)
                pg.draw.circle(cyclepanel,(0,0,255),fourier.ladder[i].get_pos(),2)

            fourier.ladderstep(.1) #slow the model down
            #draw line from where are tip started to where it is
            end_tip = fourier.get_tip()
            pg.draw.line(trace_surface,(0,0,0),start_tip, end_tip, 4)
            #combine our surfaces
            cyclepanel.blit(trace_surface,(0,0))
            screen.blit(cyclepanel,(504,2))

            #exit pygame after sim/display quit
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    print(pg.mouse.get_pos())
                    if button.collidepoint(pg.mouse.get_pos()):
                        print('hit')
                        drawmode = True


            pg.display.flip()
            fpsClock.tick(fps)




run()
