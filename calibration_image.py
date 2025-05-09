from psychopy import core,visual,event


win = visual.Window([1920,1200], units='pix', fullscr=True, screen=1)
square = visual.Rect(win, size=[1000,500], pos=[0,0], units='pix', color=-1)

running = True
while running:
    square.draw()
    win.flip()

    keys = event.getKeys()
    if len(keys) > 0:
        running = False

win.close()
core.quit()