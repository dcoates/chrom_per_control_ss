# lets test out eye tracking codes. 
# calibrations
# taken from validation_v2022.1.3.py, lines 1-186


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calibrate, validate, run with GC cursor demo / test.
Select which tracker to use by setting the TRACKER variable below.
"""

from psychopy import core, visual
from psychopy import iohub
from psychopy.iohub.client.eyetracker.validation import TargetStim
from psychopy.iohub.util import hideWindow, showWindow

# Eye tracker to use ('mouse', 'eyelink', 'gazepoint', or 'tobii')
TRACKER = 'eyelink'

eyetracker_config = dict(name='tracker')
devices_config = {}

if TRACKER == 'mouse':
    devices_config['eyetracker.hw.mouse.EyeTracker'] = eyetracker_config
    eyetracker_config['calibration'] = dict(auto_pace=True,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0, 0, 0),
                                            type='NINE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=50,
                                                                   inner_diameter=25,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1],
                                                                   animate=dict(enable=True,
                                                                                expansion_ratio=1.5,
                                                                                contract_only=False)
                                                                   )
                                            )
elif TRACKER == 'eyelink':
    eyetracker_config['model_name'] = 'EYELINK 1000 DESKTOP'
    eyetracker_config['simulation_mode'] = False
    eyetracker_config['runtime_settings'] = dict(sampling_rate=1000, track_eyes='RIGHT')
    eyetracker_config['calibration'] = dict(auto_pace=True,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0, 0, 0),
                                            type='NINE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=50,
                                                                   inner_diameter=25,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1]
                                                                   )
                                            )
    devices_config['eyetracker.hw.sr_research.eyelink.EyeTracker'] = eyetracker_config
elif TRACKER == 'gazepoint':
    eyetracker_config['device_timer'] = {'interval': 0.005}
    eyetracker_config['calibration'] = dict(use_builtin=False,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0,0,0),
                                            type='NINE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=50,
                                                                   inner_diameter=25,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1],
                                                                   animate=dict(enable=True,
                                                                                expansion_ratio=1.5,
                                                                                contract_only=False)
                                                                   )
                                            )
    devices_config['eyetracker.hw.gazepoint.gp3.EyeTracker'] = eyetracker_config
elif TRACKER == 'tobii':
    eyetracker_config['calibration'] = dict(auto_pace=True,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0, 0, 0),
                                            type='NINE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=50,
                                                                   inner_diameter=25,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1],
                                                                   animate=dict(enable=True,
                                                                                expansion_ratio=1.5,
                                                                                contract_only=False)
                                                                   )
                                            )
    devices_config['eyetracker.hw.tobii.EyeTracker'] = eyetracker_config
else:
    print("{} is not a valid TRACKER name; please use 'mouse', 'eyelink', 'gazepoint', or 'tobii'.".format(TRACKER))
    core.quit()


win = visual.Window((1920, 1200),
                    units='pix',
                    fullscr=True,
                    allowGUI=False,
                    colorSpace='rgb',
                    monitor='55w_60dist',
                    color=[0, 0, 0]
                    )

win.setMouseVisible(False)



text_stim = visual.TextStim(win, text="Start of Experiment",
                            pos=[0, 0], height=24,
                            color='black', units='pix', colorSpace='named',
                            wrapWidth=1600)



#text_stim.draw()
#win.flip()

# Since no experiment_code or session_code is given, no iohub hdf5 file
# will be saved, but device events are still available at runtime.
io = iohub.launchHubServer(window=win, **devices_config)

# Get some iohub devices for future access.
keyboard = io.getDevice('keyboard')
tracker = io.getDevice('tracker')

# Minimize the PsychoPy window if needed
#hideWindow(win)

if TRACKER != 'mouse':
    # Display calibration gfx window and run calibration.
    result = tracker.runSetupProcedure()
    print("Calibration returned: ", result)
# Maximize the PsychoPy window if needed
#showWindow(win)

# Validation


if TRACKER != 'mouse':

    # Create a target stim. iohub.client.eyetracker.validation.TargetStim provides a standard doughnut style
    # target. Or use any stim that has `.setPos()`, `.radius`, `.innerRadius`, and `.draw()`.
    target_stim = TargetStim(win, radius=25, fillcolor=[.5, .5, .5], edgecolor=[-1, -1, -1], edgewidth=2,
                             dotcolor=[1, -1, -1], dotradius=5, units='pix', colorspace='rgb')

    # target_positions: Provide your own list of validation positions,
    # target_positions = [(0.0, 0.0), (0.85, 0.85), (-0.85, 0.0), (0.85, 0.0), (0.85, -0.85), (-0.85, 0.85),
    #                    (-0.85, -0.85), (0.0, 0.85), (0.0, -0.85)]
    target_positions = 'FIVE_POINTS'

    # Create a validation procedure, iohub must already be running with an
    # eye tracker device, or errors will occur.
    validation_proc = iohub.ValidationProcedure(win,
                                                target=target_stim,  # target stim
                                                positions=target_positions,  # string constant or list of points
                                                randomize_positions=True,  # boolean
                                                expand_scale=1.5,  # float
                                                target_duration=1.5,  # float
                                                target_delay=1.0,  # float
                                                enable_position_animation=True,
                                                color_space='rgb',
                                                unit_type='pix',
                                                progress_on_key="",  # str or None
                                                gaze_cursor=(-1.0, 1.0, -1.0),  # None or color value
                                                show_results_screen=True,  # bool
                                                save_results_screen=False,  # bool, only used if show_results_screen == True
                                                )

    # Run the validation procedure. run() does not return until the validation is complete.
    validation_proc.run()
    if validation_proc.results:
        results = validation_proc.results
        print("++++ Validation Results ++++")
        print("Passed:", results['passed'])
        print("failed_pos_count:", results['positions_failed_processing'])
        print("Units:", results['reporting_unit_type'])
        print("min_error:", results['min_error'])
        print("max_error:", results['max_error'])
        print("mean_error:", results['mean_error'])
    else:
        print("Validation Aborted by User.")