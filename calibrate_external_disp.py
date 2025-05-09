from psychopy import visual, core, monitors,event
import os
from os import path
import numpy as np
import time


import grid
grid.doit(visual,event,core)

monsize =  [1920, 1080]
window=visual.Window(monsize, units='pix', fullscr=True,allowGUI=True,color=[-1,-1,-1], screen=2)

clock = core.Clock()

subjected_id=1
outputfilename= ("results/alignment_check_S0%d.csv"%(subjected_id))

if path.exists(outputfilename):
    outputfile=open(outputfilename,'a')
else:
    outputfile=open(outputfilename,'a')
    outputfile.write('Date,RectWidth,RectHeight,RectOrientation,xloc,yloc\n')

# Initialization values
rect_height=310
rect_width=310 #initial set of values fot the separate stimulus display (with mirror setup)
rect_orientation=0
posx= -20
posy= 265

square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
user_text=visual.TextStim(window,text='Ensure that size of box and raster match', opacity=0.5, pos=(0.0,400),height=36)
user_text.draw()
square_shape.draw()
fixation_cross=visual.TextStim(window,text='+',pos=(posx,posy),height=24)
fixation_cross.draw()
window.flip()

keys=event.waitKeys()
        
                
while 'num_5' not in keys and 'q' not in keys and 'esc' not in keys:
    keys=event.waitKeys()
    print(keys)
    if len(keys)>0:
        if (keys[len(keys)-1] == 'num_3'):
            rect_width+=10
            rect_height+=10
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_1'):
            rect_width-=10
            rect_height-=10
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_9'):
            rect_orientation+=1
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_7'):
            rect_orientation-=1
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_4'):
            posx-=5
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            fixation_cross=visual.TextStim(window,text='+',pos=(posx,posy),height=24)
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_6'):
            posx+=5
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            fixation_cross=visual.TextStim(window,text='+',pos=(posx,posy),height=24)
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_2'):
            posy-=5
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            fixation_cross=visual.TextStim(window,text='+',pos=(posx,posy),height=24)
            event.clearEvents()
        if (keys[len(keys)-1] == 'num_8'):
            posy+=5                 
            square_shape=visual.Rect(window,width=rect_width, height=rect_height,units='pix', lineColor='white',ori=rect_orientation,pos=(posx,posy))
            fixation_cross=visual.TextStim(window,text='+',pos=(posx,posy),height=24)   
            event.clearEvents()
        
    user_text.draw()
    square_shape.draw()
    fixation_cross.draw()
    window.flip()

outputfile.write('%s,%d,%d,%d,%d,%d\n'%(time.strftime("%m%d%Y", time.localtime() ), rect_width,rect_height,rect_orientation,posx,posy)) 
outputfile.close()
       
