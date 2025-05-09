import numpy as np
import matplotlib.pyplot as plt

size_win=(1920,1080)
#size_win=(2560,1440) # Dan's big LG

PSYCHOPY=True
DRAW_FIXATION=True
TWO_AFC=True

fixloc=(0,0)
fixheight=50

colr=0.5

def doit(visual,event,core):
        myWin = visual.Window(size_win,fullscr=True,allowGUI=False, units='pix', screen=1,color=-1)
        myMouse = event.Mouse(visible=False)

        fixation = visual.TextStim(myWin,pos=(fixloc), text='+',
                                   anchorHoriz='center',anchorVert='center',height=fixheight, color=colr)
        fixation.draw()

        for x in np.arange(-(size_win[0]//2//100)*100, size_win[0]//2,100):
            line = visual.Line(myWin,start=(x,-size_win[1]/2),end=(x,size_win[1]/2), color=colr)
            line.draw()

            t1 = visual.TextStim(myWin,pos=(x,400), text=str('%04d'%x), anchorVert='center',
                                   anchorHoriz='left',height=fixheight, color='red',ori=90)
            t1.draw()
        for y in np.arange(-(size_win[1]//2//100) * 100, size_win[1]//2,100):
            line = visual.Line(myWin,start=(-size_win[0]/2,y),end=(size_win[0]/2,y), color=colr)
            line.draw()

            t1 = visual.TextStim(myWin,pos=(0,y), text=str('%04d'%y),
                                   anchorHoriz='left',height=fixheight, color='green')
            t1.draw()

        myWin.flip()

if __name__ == "__main__":
    if PSYCHOPY:
        from psychopy import visual, event, core
        doit(visual,event,core)
        keys=event.waitKeys()
