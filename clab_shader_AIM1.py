#import calibration_setup_FULL as cc
from psychopy import gui
from psychopy.visual.shaders import compileProgram
from psychopy.tools.filetools import fromFile

import numpy as np
from operator import itemgetter
import ctypes



##
## pulling in setup information + color matrixes from params pickle
from psychopy.tools.filetools import fromFile

try:
    setup_file = 'NEC_PA241W_AIM1.pickle'
    setup_params = fromFile(setup_file)
    print('\nsetup parameters read from %s' % setup_file)
except:
    try:
        file = gui.fileOpenDlg(prompt='Select Lab Setup File to open')[0]
        file_name = file.split('/')[-1]
        setup_params = fromFile(file)
        print('\nsetup parameters read from %s' % file_name)
    except:
        print('\nno setup parameters file found, \nplease run calibration_setup.py')
        pass






##
## unpacking dimension calcs into variables
class dimensions:
    win_pix, min_pix = itemgetter('win_pix', 'min_pix')(setup_params)



##
## shader stuffs. 
class shader:
    def __init__(self,GL):
        self.program=None
        self.GL=GL

    def load_shader(self):
        shader_vert = open('clab_vertex.vert').readlines()
        shader_frag = open('clab_fragment.frag').readlines()
        self.program = compileProgram(
            vertexSource=shader_vert,
            fragmentSource=shader_frag
        )
        return self.program


    def init_uniforms(self,color_dir):

        # ok so after selecting current color direction...  AND setting up shaders...
        # lets first set proper line. 
        # pass in white coords

        self.w_unif = self.GL.glGetUniformLocation(self.program, b'w_unif')
        self.GL.glProgramUniform2f(self.program, self.w_unif, setup_params['W_x'], setup_params['W_y'])

        # pass in 2nd coord to vary to. 
        self.rgb_unif = self.GL.glGetUniformLocation(self.program, b'rgb_unif')
        if color_dir == 0:
            self.GL.glProgramUniform2f(self.program, self.rgb_unif, setup_params['W_x'], setup_params['W_y'])
        elif color_dir == 1:
            self.GL.glProgramUniform2f(self.program, self.rgb_unif, setup_params['L_x'], setup_params['L_y'])
        elif color_dir == 2:
            self.GL.glProgramUniform2f(self.program, self.rgb_unif, setup_params['M_x'], setup_params['M_y'])
        elif color_dir == 3:
            self.GL.glProgramUniform2f(self.program, self.rgb_unif, setup_params['S_x'], setup_params['S_y'])
        elif color_dir == 4:
            self.GL.glProgramUniform2f(self.program, self.rgb_unif, setup_params['LM_x'], setup_params['LM_y'])
 
        '''
        # Debugging: For use to make sure values are passing into the mat correctly
        x = np.array([[1,1,1],[1,1,1],[1,1,1]], dtype=np.float32)

        test_unif = self.GL.glGetUniformLocation(self.program, b'test_m')
        self.GL.glProgramUniformMatrix3fv(self.program, test_unif, 1, False,
            x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        '''

        ##
        ## setting colorspace conversion matrix unifs
        self.rgb2xyz_unif = self.GL.glGetUniformLocation(self.program, b'rgb2xyz_unif')
        self.GL.glProgramUniformMatrix3fv(self.program, self.rgb2xyz_unif, 1, True,
                setup_params['rgb2xyz_mat'].ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        self.xyz2rgb_unif = self.GL.glGetUniformLocation(self.program, b'xyz2rgb_unif')
        self.GL.glProgramUniformMatrix3fv(self.program, self.xyz2rgb_unif, 1, True,
                setup_params['xyz2rgb_mat'].ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        self.xyz2lms_unif = self.GL.glGetUniformLocation(self.program, b'xyz2lms_unif')
        self.GL.glProgramUniformMatrix3fv(self.program, self.xyz2lms_unif, 1, True,
                setup_params['xyz2lms_mat'].ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        self.lms2xyz_unif = self.GL.glGetUniformLocation(self.program, b'lms2xyz_unif')
        self.GL.glProgramUniformMatrix3fv(self.program, self.lms2xyz_unif, 1, True,
                setup_params['lms2xyz_mat'].ctypes.data_as(ctypes.POINTER(ctypes.c_float)))



        ##
        ## setting luminance normalization unifs
        self.lum_unifs = self.GL.glGetUniformLocation(self.program, b'lum_unifs')
        self.GL.glProgramUniform3f(self.program, self.lum_unifs, setup_params['r_lum'], setup_params['g_lum'], setup_params['b_lum'])

        self.targlum_unif = self.GL.glGetUniformLocation(self.program, b'targlum_unif')
        self.GL.glProgramUniform1f(self.program, self.targlum_unif, setup_params['targ_lum'])


        ##
        ## passing in time?  dont think this is working properly actually...
        self.time_unif = self.GL.glGetUniformLocation(self.program, b'time_unif')

        

    def set_time(self,current_time):
        self.GL.glProgramUniform1f(self.program, self.time_unif, current_time )
