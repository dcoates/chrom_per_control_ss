#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psychopy.hardware import joystick

DEBOUNCE_THRESHOLD=3

class controller():
    """
    Wrapper class to use PsychoPy joysticks like a button box
    - Handles debounce
    - Only returns 'True' when button is first pressed
    - Returns 0s if there is no joystick (needn't check every time)
    """
    def __init__(self):
        self.nJoysticks=joystick.getNumJoysticks()
        if self.nJoysticks > 0:
            self.joy = joystick.Joystick(0)
            self.debounce_counter=[0]*len( self.joy.getAllButtons() )
            self.pressed=[False]*len( self.joy.getAllButtons() ) # cleared when read
        else:
            self.joy = None

    def getAllButtons(self):
        if self.joy is None: # No real joystick
            self.pressed=[0]*16
            return self.pressed

        buttons = self.joy.getAllButtons()

        pressed = [0] * len(buttons) # local copy, momentary

        # Loop through, debounce each button
        for idx,btn in enumerate(buttons):
            if btn != self.pressed[idx]: # Button state changed 
                self.debounce_counter[idx] += 1
                if self.debounce_counter[idx] >= DEBOUNCE_THRESHOLD: # Enough consecutives to signal reliable event
                    self.pressed[idx]=not(self.pressed[idx]) # Yes, state changed
                    pressed[idx] = self.pressed[idx] # Note state change: will only get one press
            else:
                self.debounce_counter[idx]=0 # Button state changed; reset counter

        #print (self.pressed, self.debounce_counter)

        return pressed


    def getAllButtons_raw(self):
        """ non-debounced """
        return self.joy.getAllButtons()

if __name__ == "__main__":
    
    # This test stuff copied from the joystick demo in PsychoPy Coder Demos

# joystick.backend = 'pyglet'
# # As of v1.72.00, you need the winType and joystick.backend to match:
# win = visual.Window((800.0, 800.0), allowGUI=False, winType=joystick.backend,screen=1)

# nJoysticks = joystick.getNumJoysticks()

    from psychopy import visual, core, event
    #joystick.backend = 'pyglet'
    # As of v1.72.00, you need the winType and joystick.backend to match:
    win = visual.Window((800.0, 800.0), allowGUI=False) #, winType=joystick.backend,screen=0)

    ajoy = controller()

    if ajoy.joy:
        joy=ajoy.joy
        print('found ', joy.getName(), ' with:')
        print('...', joy.getNumButtons(), ' buttons')
        print('...', joy.getNumHats(), ' hats')
        print('...', joy.getNumAxes(), ' analogue axes')
    else:
        print("You don't have a joystick connected!?")
        win.close()
        core.quit()
    
    nAxes = joy.getNumAxes()
    
    fixSpot = visual.GratingStim(win, pos=(0, 0),
        tex="none", mask="gauss",
        size=(0.05, 0.05), color='black')
    grating = visual.GratingStim(win, pos=(0.5, 0),
        tex="sin", mask="gauss",
        color=[1.0, 0.5, -1.0],
        size=(0.2, .2), sf=(2, 0))
    message = visual.TextStim(win, pos=(0, -0.95), text='Hit "q" to quit')
    
    trialClock = core.Clock()
    t = 0
    while not event.getKeys():
        # update stim from joystick
        xx = joy.getX()
        yy = joy.getY()
        grating.setPos((xx, -yy))
        # change SF
        if nAxes > 3:
            sf = (joy.getZ() + 1) * 2.0  # so should be in the range 0: 4?
            grating.setSF(sf)
        # change ori
        if nAxes > 6:
            ori = joy.getAxis(5) * 90
            grating.setOri(ori)
        # if any button is pressed then make the stimulus colored
        if sum(joy.getAllButtons()):
            grating.setColor('red')
        else:
            grating.setColor('white')
    
        # drift the grating
        t = trialClock.getTime()
        grating.setPhase(t * 2)
        grating.draw()
    
        fixSpot.draw()
        message.draw()
        print(ajoy.getAllButtons(), sum(ajoy.getAllButtons()) )  # to see what your axes are doing!
    
        event.clearEvents()  # do this each frame to avoid a backlog of mouse events
        win.flip()  # redraw the buffer

        while not event.getKeys():
            wow=ajoy.getAllButtons()
            if sum(wow)>0:
                print (wow)
            win.flip()

    core.quit()
        
    
    win.close()
    core.quit()
    
    # The contents of this file are in the public domain.
    
