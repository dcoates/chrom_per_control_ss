# TODO
# figure out 0,1,2,3... output pos
 

import psychopy
psychopy.prefs.hardware['audioLib'] = ['PTB', 'pyo','pygame']

from psychopy import core, visual, sound, data, event, gui
import psychtoolbox as ptb

import clab_staircase as cstairs
from clab_grating import GratingStim
from clab_joystick import controller 
from clab_shader_AIM2 import shader, dimensions

import numpy as np
import random
import os
import time

vol=0.1

# global settings values
cie_col_range = 1.0
noise_range = 0.8
stair_init_value = 0.9

# 200 pix on projector is 140 on the external screen
dimensions.min_pix = 1.19 / (200/140.0)

size_deg = 10/60.0   #diameter
stim_size = (1/dimensions.min_pix) * 60 * size_deg     # invert minutes/pix = pixels/min, *60 = pixels/deg * 1.0 deg = TOTAL PIXELS
num_ecc = 1     # total number of rings (ecc tested)
deg_ecc = 2.5     # degree steps for each ring (ecc)

print( size_deg, stim_size, dimensions.min_pix)


stim_dur = 0.30
nontarget_dur_min = 0.2
nontarget_dur_max = 0.4
resp_timeout_seconds=30.0

do_instructions=True
do_countdown=False
do_eye_tracker=False
do_fixation=True
do_fixation_first=True
do_fixation_after=False
do_pport=False
do_sound=True

if do_pport:
    import parallel64
    pport=parallel64.StandardPort(spp_base_address=0x3efc)

## more eye tracker stuff
# eye tracker calibration
# all following code requiring eye tracking, refer as et. 
if do_eye_tracker: #exp_params['et_cali'] == True:
    import clab_eyetracker as et

    win = et.win # Reuse the stupid iohub Window for our expt.
    win.winHandle.activate()
else:
    win = visual.Window([1920,1080], allowGUI=True, fullscr=True,
        monitor='testMonitor', color=(-1,-1,-1), units='pix', screen=1)

    # NEC in the real world
    nec_fix_pos = (-100,0)
    win2 = visual.Window([1920,1200], allowGUI=True, fullscr=True,
        monitor='testMonitor', color=(0,0,0), units='pix', screen=0)
    fix2 = visual.TextStim(win2, text='+', color=(1,1,1), colorSpace='rgb', height=80,pos=nec_fix_pos)
    fix2.draw()
    win2.flip()
        #monitor='testMonitor', color=(-0.67, -0.67, -0.67), units='pix', screen=1)
# settings/ drawing
gaze_ok_region = visual.Circle(win, lineColor='black', radius = 300)
gaze_dot = visual.GratingStim(win, tex=None, mask='gauss', pos=(0,0), size=(20,20), color='green', colorSpace='named', units='pix')

# shader stuff
shader=shader(win.backend.GL) # Create our new shader object
shader.load_shader()  # Load vertex and frag

bg = GratingStim(win, sf=0, size=dimensions.win_pix*2, pos=(0,0), color=(-1.0, -1.0, -1.0), shader_program=shader.program)
fix = visual.TextStim(win, text='+', color=-0.8, colorSpace='rgb', height=80)

if do_fixation_first:
    bg.draw()   
    fix.draw()  
    win.flip() 
    
# setting curr_exp parameters
dlg = gui.Dlg(title='Current Experiment Setup')
dlg.addField('Subject', 'test')
dlg.addField('Color Direction', choices=['1 Red','2 Green','3 Blue','4 Yellow','0 Achromatic'])
dlg.addField('Eye', choices=['OD','OS'])
dlg.addField('Adaptation', initial=False)
dlg.addField('Eye Tracker', initial=False)

exp_setup = dlg.show()  # show dialog and wait for OK or Cancel

if dlg.OK:  # or if ok_data is not None
    labels = ['subj_name', 'color_dir', 'eye', 'adapt', 'et_cali']
    exp_params = {}
    for index,each in enumerate(exp_setup):
        exp_params[labels[index]] = each
    print(exp_params)
    exp_params['color_dir']=int(exp_params['color_dir'][0])
    
    file_name = exp_params['subj_name'] + '_' + exp_params['eye'] + '_col' + str(exp_params['color_dir']) + '_r0'

    path = 'trial_data/aim_2'
    # in data folder, if file_name exists, add 1 to trial #
    
    next_ind = 1

    file_name = os.path.join(os.getcwd(),path,'%s'%file_name)
    while os.path.exists(file_name+'.xlsx'):
        file_name = file_name[:-1] + str(next_ind)
        next_ind += 1
        
    print('fn',file_name)
else:
    print('user cancelled')
    core.quit()

# Set shader parameters after we know condition
shader.init_uniforms(exp_params['color_dir'])

#WE used this to save the exact background luminance
#win.getMovieFrame()
#win.saveMovieFrames('test.mp4')

# setting circle coords
rad_length = (1/dimensions.min_pix) * 60 * deg_ecc
rad_steps = 2
coords_temp = []
coords = []
thetas = [-np.pi/2 - np.pi/16, -np.pi/2+np.pi/16]
cx=150
cy=20
for i in np.arange(num_ecc + 1):
    for j in np.arange(rad_steps):
        # Compute angle, counterclockwise. 0=right, 1=upper right, 2=up, etc.

        theta = thetas[j]
        coords_temp.append([np.cos(theta) * i * rad_length+cx,
            np.sin(theta) * i * rad_length+cy])

        print(i,j)

# killing the repeated zeroes
coords_temp = coords_temp[rad_steps:]     #[rad_steps-1:]   #kill all or kill all but 1, make sure to change below

# killing the + orientation circs
for i in range(0,len(coords_temp),1):
    coords.append(coords_temp[i])
# coords is [x],[y] coordinates



## define some functions for randomization

# Return a random number uniformly between rmin and rmax
def rand_range_float(rmin, rmax):
    t = random.random() * (rmax-rmin) + rmin
    return t

# noise randomizer   (centers on 0, +/- noise_range)
def noi_col():
    if exp_params['color_dir'] == 0:
        c = 0
    else:
        c = random.random() * (noise_range)+(1-noise_range) # to go to max
    return c

# sounds
if do_sound:
    init_tone = sound.Sound('A', secs=0.2, volume=vol)
    corr_tone = sound.Sound('B', secs=0.2, volume=vol)
    incorr_tone = sound.Sound('C', secs=0.2, volume=vol)
    done_tone = sound.Sound('D', secs=0.2, volume=vol)
    i1_tone = sound.Sound('A', secs=0.2, volume=vol)
    i2_tone = sound.Sound('D', secs=0.2, volume=vol)

# all circles
circs = []
for coord in coords:
    circ = GratingStim(win, sf=0, size=stim_size, mask='circle', pos=coord, shader_program=shader.program)
    circ.setColor((-1.0, noi_col(), -1.0), 'rgb')   # bg_color, bg_noise, randomization
    circ.num_deaths = 0
    # Lifespan is the time at which each element die. Initialize is to 0-avg. nontarget duration,
    # so that the onsets between nontarget switches are random.
    circ.lifespan = rand_range_float( 0, (nontarget_dur_max-nontarget_dur_min)/2.0 ) 
    circs.append(circ)


'''
# just the target circs (based on ecc)
target_circs = []
#target_circs.append(circs[0]) # Add the foveal target
for i in range(2,9,2):
    i = i + (8 * (ecc-1))
    target_circs.append(circs[i])
'''

#they are now all target circs
target_circs = circs

joy = controller()
# Map from radial position on the screen of potential targets to correct button to press
# E.g. target 0 is 45 degrees (upper right), which on the PXN-0082 controller
# Is the green button, mapped to #3 in the array returned by getAllButtons()
# On the EasySMX xbox controller, yellow in upper right

# setting list of dictionaries for exp conditions, initializing stairs. 
conditions = []
for i in np.arange(len(target_circs)):
    if i==0:
        pos='1'
        key='1'
        joystick_button=0
    else:
        pos='2'
        key='2'
        joystick_button=1

    # full stairs
    temp = {'label':str(i), 'name':str(i), 'coord':target_circs[i].pos, 'startVal':stair_init_value,
            'quad_pos':pos, 'corr_key':key, 'corr_joy':joystick_button,
            'nReversals':6, 'stepType':'log', 'stepSizes':[0.2, 0.15, 0.10, 0.05, 0.05, 0.025],
            'nUp':1, 'nDown':1, 'minVal':0.0, 'maxVal':1.0}
            # log stepSizes... [1.26,1.26,1.26,1.13,1.13,1.13] same as [0.10037,0.10037,0.10037,0.05307,0.05307,0.05307],   formatted as 10^-x = y
            # try [0.15, 0.1, 0.1, 0.05, 0.05, 0.025]
    conditions.append(temp)

stairs = cstairs.MultiStairHandler(conditions=conditions, method='fullRandom', nTrials=20)

##
## pre-adaptation
if exp_params['adapt'] == True:
    
    bg.draw()
    fix.draw()
    win.flip()
    core.wait(30)

    now = ptb.GetSecs()
    if do_sound:
        corr_tone.play(when=now)

# This will now have correct background

bg.draw()
fix.draw()
win.flip()
#win.getMovieFrame()
#win.saveMovieFrames('background.png')

if do_fixation_after:
    # allow button press or keyboard press to continue
    buttons = joy.getAllButtons()
    keys = event.getKeys()

    while any(joy.getAllButtons()) == False:
        bg.draw()
        fix.draw()
        win.flip()
        if event.getKeys():
            break

if do_instructions:
    ##
    ## main exp instructions + countdown
    instructions = visual.TextStim(win, 
        text='Please keep your eyes on the cross in the center of the screen,  press the button corresponding to the position of the colored spot. \n\nPress any button to continue',
        alignText='left', wrapWidth=1600, height=80,pos=(0,100) )

    # allow button press or keyboard press to continue
    buttons = joy.getAllButtons()
    keys = event.getKeys()

    while any(joy.getAllButtons()) == False:
        instructions.draw()
        fix.draw()
        win.flip()
        if event.getKeys():
                break



if do_countdown:
# countdown
    for i in np.arange(1,4)[::-1]:
        countdown = visual.TextStim(win, text=u'%s' %i, height = 600)
        countdown.draw()
        win.flip()
        core.wait(1)

trial_counter = 0
##
## main exp loop

TIME_BEFORE_I1 = 1.000
STIM_DURATION = 0.300
TIME_BETWEEN = 1.000
NOISE_AFTER = 1.000 # Prevent offset difference cue

trial_counter = 0
##
## main exp loop
for curr_val, curr_cond in stairs:
    trial_counter += 1
    curr_pos = curr_cond['coord']
    curr_index = int(curr_cond['label'])
    trialClock = core.Clock() # trialClock start at zero for each trial

    now = ptb.GetSecs()
    if do_sound:
        init_tone.play(when= now + 0.5)

    # reset circ values
    for circ in circs:
        circ.lifespan = rand_range_float( 0, nontarget_dur_max-nontarget_dur_min)
        circ.num_deaths = 0
        circ.birth = 0

    print('\n\n\n  NEW TRIAL!  ')
    print('position: ',curr_cond['quad_pos'], '     val: ', curr_val)

    print('\ncurrent stair...')
    print(' - pos: ', stairs.currentStaircase.name, '     ', stairs.currentStaircase)

    # lets try to print some debugging logs
    print('\nupcoming stairs in block...')
    for each in stairs.thisPassRemaining:
        print(' - pos: ', each.name, '     ', each)
        print(each._nextIntensity)
    print('\n')

    # For each trial
    in_trial = True
    is_stim_on = False
    allow_resp = False

    # These are mostly for logging to output file:
    resp_timeout=False
    time_resp=-1
    resp=''

    while in_trial:

        if do_pport:
            pport.write_data_register(0xff) # Normally high: nothing happening. May get set on this frame if stim comes on.

        timeCurr = trialClock.getTime()
        shader.set_time(timeCurr) # send time to shader (for randomizing noise)
        bg.draw()

        #fix.draw()
        #if do_fixation:
            #fix_vert.draw()
            #fix_hori.draw()
        #fix_buff.draw()
        circ = circs[-1]

        if timeCurr < TIME_BEFORE_I1:
            #print("S1",end='')
            circ.setColor((-1.0, noi_col(), -1.0), 'rgb')
        elif timeCurr <= TIME_BEFORE_I1+STIM_DURATION:
            i1_tone.play(when=now)
            #print("S2",end='')
            # Int1
            stairs.addOtherData('time_stim',time.time())
            if do_pport:
                pport.write_data_register(0); # Set it low on this frame (will be cleared next frame)

            # Make it colored.
            if curr_index == 0: 
                circ.setColor(((curr_val*2.0)-1.0, 0, -1.0), 'rgb')
            else:
                circ.setColor((-1.0, noi_col(), -1.0), 'rgb')
                #circ.setColor((-1.0, curr_val, -1.0), 'rgb')

            is_stim_on = True
            allow_resp = True
        elif timeCurr <= TIME_BEFORE_I1+STIM_DURATION+TIME_BETWEEN:
            print("S3",end='')
            # (noise) if age is up, give it new color, +deaths
            circ.setColor((-1.0, noi_col(), -1.0), 'rgb')
            circ.lifespan = rand_range_float(nontarget_dur_min,nontarget_dur_max) + timeCurr
            circ.num_deaths +=1 # Increment death counter for both targets and nontargets

            is_stim_on = False # Target turned off
        elif timeCurr <= TIME_BEFORE_I1+STIM_DURATION+TIME_BETWEEN+STIM_DURATION:
            i2_tone.play(when=now)
            #print("S4",end='')
            # Int2
            stairs.addOtherData('time_stim',time.time())
            if do_pport:
                pport.write_data_register(0); # Set it low on this frame (will be cleared next frame)

            # Make it colored.
            if curr_index==1:
                circ.setColor(((curr_val*2.0)-1.0, 0, -1.0), 'rgb')
            else:
                circ.setColor((-1.0, noi_col(), -1.0), 'rgb')
                #circ.setColor((-1.0, curr_val, -1.0), 'rgb')

            is_stim_on = True
            allow_resp = True
        elif timeCurr <= TIME_BEFORE_I1+STIM_DURATION+TIME_BETWEEN+STIM_DURATION:
            #print("S5",end='')
            circ.setColor((-1.0, noi_col(), -1.0), 'rgb')
        else:
            # After:
            #print("S5",end='')
            circ.setColor((-1.0, -1.0, -1.0), 'rgb')

        circ.draw()
        win.flip()

        if allow_resp:
            # keyboard responses
            keys=event.getKeys()
            
            resp_correct=False
            for key in keys:
                #print('key:   ', key)
                time_resp=time.time()
                resp=key

                key_time = core.Clock()

                if key in [ 'q','escape' ]:
                    win.close()
                    core.quit()
                if curr_cond['corr_key'] in key:
                    resp_correct=True
                else:
                    resp_correct=False
                in_trial = False
            
            # joystick button responses
            buttons = joy.getAllButtons()
            if any(buttons) > 0: # any button pressed
                
                time_resp=time.time()
                resp=buttons
                print(buttons)
                
                if buttons[curr_cond['corr_joy'] ]: # Is it the correct button for this target?
                    resp_correct=True
                else:  # wrong button
                    resp_correct=False
                in_trial=False

        else:
            # clear any logged 'double clicks'
            # BUG: this only allows quitting after stim presentation..
            event.clearEvents()

        ## lets implement eyetracker
        ## initialize eye tracker
        if exp_params['et_cali'] == True:
            et.io.clearEvents()
            et.tracker.setRecordingState(True)

            # get latest gaze position in display coord
            gpos = et.tracker.getLastGazePosition()
            # update stim based on gaze pozition
            valid_gaze_pos = isinstance(gpos, (tuple, list))
            gaze_in_region = valid_gaze_pos and gaze_ok_region.contains(gpos)
            
            valid_gaze_during_stim = True
            
            if valid_gaze_pos:
                # draw gaze dot
                #gaze_dot.draw()

                # if we have gaze position from tracker, update gc stim and text stim
                if gaze_in_region:
                    
                    gaze_in_region = 'YES'
                    fix.color = 'green'
                    
                else:

                    gaze_in_region = 'NO'
                    fix.color = 'red'
                    
                    if is_stim_on:
                        valid_gaze_during_stim = False
                        
                        now = ptb.GetSecs()
                        if do_sound:
                            incorr_tone.play(when = now)
                        
                        stairs.next()
                        in_trial = False

                #gaze_dot.setPos(gpos)
            else:
                fix.color = 'gray'
                
        # timeout trial
        # Check in_trial because they may have clicked on the very last flip,
        # want to record it correct if so.
        if in_trial and (timeCurr > resp_timeout_seconds):
            key_time = core.Clock()
            
            print('timeout')
            resp_correct=False
            in_trial = False
            resp_timeout=True


    # stop exiting tones, play finished tone. 
    if do_sound:
        init_tone.stop()
        corr_tone.stop()
        now = ptb.GetSecs()
        corr_tone.play(when=now)

    # trial done, closing down et, adding response to stair
    if exp_params['et_cali'] == True:
        #et.tracker.setRecordingState(False)
        
        print(valid_gaze_during_stim)
        
        if valid_gaze_during_stim:
            stairs.addResponse(resp_correct)
        else:
            print('et, else')
            pass
    
    else:
        print('Correct?:', resp_correct, '     stairs updated')
        stairs.addOtherData('time_resp',time_resp);
        stairs.addOtherData('resp',resp)
        stairs.addOtherData('resp_timeout',resp_timeout)
        stairs.addResponse(resp_correct)

    for aStaircase in stairs.staircases:
        print ('\nStaircase #%s'%(aStaircase.name), flush=True)
        if len (aStaircase.intensities)>0:
            print(' - Reversals: %d  of  %d'  %(len(aStaircase.reversalIntensities),aStaircase.nReversals), flush=True)
        if len(aStaircase.intensities)>0:
            print(' - Trials: %i  of  %i'  %(len(aStaircase.intensities), aStaircase.nTrials), flush=True)
        if len(aStaircase.intensities)>0:
            print(' - last intensity: %f'%(aStaircase.intensities[-1]), flush=True)
        if len(aStaircase.reversalIntensities)>0:
            print(' - last reversal intensity: %f'%(aStaircase.reversalIntensities[-1]), flush=True)

    running_stairs = []
    finished_stairs = []
    
    for each in stairs.staircases:
        if each in stairs.runningStaircases:
            running_stairs.append(each.name)
        if each.finished:
            finished_stairs.append(each.name)

    print('current stairs: ', running_stairs)
    print('finished stairs: ', finished_stairs)

    print('\nTOTAL TRIALS COMPLETED:  ', trial_counter)

    ##
    ##
    ## trying multistair fix here
    #print('fixing...')

    '''
    for ind,each in reversed(list(enumerate(stairs.thisPassRemaining))):
        if each.finished:
            print('*** cleaning thisPassRemaining ***')
            del stairs.thisPassRemaining[ind]
    '''
print('\nOUT OF THE EXP LOOP!')

# exp done, closing down et
if exp_params['et_cali'] == True:
    et.tracker.setConnectionState(False)
else:
    pass

stairs.saveAsExcel(file_name)

if do_sound:
    now = ptb.GetSecs()
    if do_sounds:
        done_tone.play(when=now)

##
## exp done, thank you screen
thankyou = visual.TextStim(win, 
    text='Finished!\nPlease wait as we set up the next trial\nThank You!',
    alignText='center', wrapWidth=1600, height=80)

thankyou.draw()
win.flip()
core.wait(5)

win.close()
core.quit()
