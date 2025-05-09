# python/ psychopy portion for inputting monitor gamut coordinates. 

from psychopy import gui
from psychopy.tools.filetools import fromFile, toFile
from operator import itemgetter
import math
import numpy as np
import ast


# dialogue for required user inputs
dlg = gui.Dlg(title='Color and Angle Calibrations')
dlg.addField('Setup Name', 'default_setup')

dlg.addText('\n\nColor Gamut Coordinates')
#dlg.addField('Red Coordinate:','[0.000, 0.000]')
#dlg.addField('Green Coordinate:', '[0.000, 0.000]')
#dlg.addField('Blue Coordinate:', '[0.000, 0.000]')
#dlg.addField('White Coordinate:', '[0.000, 0.000]')

dlg.addField('Red Coordinate:','[0.696, 0.302]')
dlg.addField('Green Coordinate:', '[0.168, 0.742]')
dlg.addField('Blue Coordinate:', '[0.152, 0.030]')
dlg.addField('White Coordinate:', '[0.324, 0.372]')

dlg.addText('\n\nMax Luminance per Colored Subpixel (cd/m2)')
#dlg.addField('Red Subpixel', 0.0)
#dlg.addField('Green Subpixel', 0.0)
#dlg.addField('Blue Subpixel', 0.0)
#dlg.addField('TARGET LUMINANCE', 0.0)

dlg.addField('Red Subpixel', 14.8)
dlg.addField('Green Subpixel', 43.4)
dlg.addField('Blue Subpixel', 1.6)
dlg.addField('TARGET LUMINANCE', 30.0)

dlg.addText('\n\nMonitor Distance and Required Angular Extent')
dlg.addField('Distance to Monitor (cm):', 154)
dlg.addField('Length of 1000px (cm)', 26.9)
dlg.addField('Full Visual Angle Subtending (deg)', 10)

lab_setup = dlg.show()  # show dialog and wait for OK or Cancel



if dlg.OK:  # or if ok_data is not None
    
    ## lets create a dictionary for dlg inputs for easier referencing
    labels = ['setup_name', 'r_coord', 'g_coord', 'b_coord', 'w_coord',
            'r_lum', 'g_lum', 'b_lum', 'targ_lum',
            'distance', 'width', 'angle']
    dlg_dict = {}
    for index,each in enumerate(lab_setup):
        dlg_dict[labels[index]] = each
    


    ##
    ## COLOR SPACE CALCULATIONS
    r_coord = ast.literal_eval(dlg_dict['r_coord'])
    g_coord = ast.literal_eval(dlg_dict['g_coord'])
    b_coord = ast.literal_eval(dlg_dict['b_coord'])
    w_coord = ast.literal_eval(dlg_dict['w_coord'])

    rgb_coords = np.array([r_coord,g_coord,b_coord], dtype=np.float32)

    # rgb to xyz matrix
    # zyz to rgb matrix

    def xyL2xyz(x,y,L):
        X=(x/y)*L
        Y=L
        Z=((1.0-x-y)/y)*L
        return np.array((X,Y,Z), dtype=np.float32)

    def xyz2xyL(v):
        sm=v[0]+v[1]+v[2]
        return(v[0]/sm,v[1]/sm,v[1])

    rgb2xyz_mat = np.array(xyL2xyz(rgb_coords[:,0],rgb_coords[:,1],[1,1,1]), dtype=np.float32)

    xyz2rgb_mat = np.linalg.inv(rgb2xyz_mat)

    # setting CONSTANTS
    # implement copunctal point chromaticity coordinates
    # this gives us the LMS cone primaries
    # here we take XYZ and convert to LMS relative cone excitations (tristimulus values)
    # xyz2lms_mat and lms2xyz_mat ARE CONSTANT!

    prot = np.array([0.7465,0.2535,0.0], dtype=np.float32)
    deut = np.array([1.4000,-0.4000,0.0], dtype=np.float32)
    trit = np.array([0.1748,0.0,0.8252], dtype=np.float32)

    k_l = prot[1]
    k_m = deut[1]
    k_s = 0.01327

    # A.3.14 + see A.3.15
    constants = (np.eye(3, dtype=np.float32)*np.array([k_l,k_m,k_s], dtype=np.float32))
    copunctal = np.linalg.inv(np.vstack([prot,deut,trit]).T)

    xyz2lms_mat = np.matmul(constants,copunctal)

    # A.4.3
    lms2xyz_mat = np.linalg.inv(xyz2lms_mat)

    def lms2xyz(lms):
        return np.matmul(np.linalg.inv(xyz2lms_mat),lms)

        # specifying LMS isolating lines

    #see below, from A.4.11
    deltaLum = np.array([0.2887, 0.2887, 0.000], dtype=np.float32)
    deltaLM = np.array([0.3727, -0.1863, 0.00001], dtype=np.float32)
    deltaS = np.array([-0.1667, -0.1667, 0.3333], dtype=np.float32)

    # white point
    lms = np.matmul(xyz2lms_mat,xyL2xyz(0.327,0.335,1.0))     ####

    # adding LMS isolating line coordinates to white point, scaled to extend gamut. 
    p_lm1 = xyz2xyL(lms2xyz(lms+deltaLM*2.0))
    p_lm2 = xyz2xyL(lms2xyz(lms-deltaLM*0.5))
    p_s1 = xyz2xyL(lms2xyz(lms+deltaS))
    p_s2 = xyz2xyL(lms2xyz(lms-deltaS*0.05))

    # green - red gamut line  (slope, intercept)
    trm=(rgb_coords[1][1]-rgb_coords[0][1])/(rgb_coords[1][0]-rgb_coords[0][0])
    trb=rgb_coords[0][1]-(rgb_coords[0][0]*trm)

    # blue - green gamut line  (slope, intercept)
    tgm=(rgb_coords[2][1]-rgb_coords[1][1])/(rgb_coords[2][0]-rgb_coords[1][0])
    tgb=rgb_coords[1][1]-(rgb_coords[1][0]*tgm)

    # red - blue gamut line  (slope, intercept)
    tbm=(rgb_coords[0][1]-rgb_coords[2][1])/(rgb_coords[0][0]-rgb_coords[2][0])
    tbb=rgb_coords[2][1]-(rgb_coords[2][0]*tbm)

    # L - M isolating line  (slope, intercept)
    lmm=(p_lm2[1]-p_lm1[1])/(p_lm2[0]-p_lm1[0])
    lmb=p_lm1[1]-(p_lm1[0]*lmm)

    # S - LM isolating line  (slope, intercept)
    sm=(p_s2[1]-p_s1[1])/(p_s2[0]-p_s1[0])
    sb=p_s1[1]-(p_s1[0]*sm)

    # xy of max L
    L_x = (tbb-lmb)/(lmm-tbm)
    L_y = lmm * L_x + lmb

    # xy of max M
    M_x = (tgb-lmb)/(lmm-tgm)
    M_y = lmm * M_x + lmb

    # xy of max S
    S_x = (tbb-sb)/(sm-tbm)
    S_y = sm * S_x + sb

    # xy of max LM
    LM_x = (trb-sb)/(sm-trm)
    LM_y = sm * LM_x + sb

    W_x = w_coord[0]
    W_y = w_coord[1]



    ##
    ## Luminance Calculations for Normalizations
    #max_lum = dlg_dict['r_lum'] + dlg_dict['g_lum'] + dlg_dict['b_lum']
    #r_norm = dlg_dict['r_lum'] / max_lum
    #g_norm = dlg_dict['g_lum'] / max_lum
    #b_norm = dlg_dict['b_lum'] / max_lum

    r_lum, g_lum, b_lum, targ_lum = itemgetter('r_lum', 'g_lum', 'b_lum', 'targ_lum')(dlg_dict)



    ##
    ## ANGLE CALCULATIONS
    pix_per_cm = 1000/ dlg_dict['width']

    # if we want something that subtends full 'x' deg visual angle...
    # x/2 for right triangle trigs
    tan_half = math.tan(math.radians(dlg_dict['angle']/2))

    # tan(radians) = opp / adj
    # opp = tan(radians) * adj
    # opp * 2 ... for full size window (cm)
    win_cm = tan_half * dlg_dict['distance'] * 2.0

    # height/width pixels to subtend full x degrees
    win_pix = win_cm * pix_per_cm
    # minutes/pix
    min_pix = dlg_dict['angle']*60/win_pix

    #
    # output pickle
    params_dict = {}
    output_labels = ['rgb2xyz_mat', 'xyz2rgb_mat', 'xyz2lms_mat', 'lms2xyz_mat', 
                    'W_x', 'W_y', 'L_x', 'L_y', 'M_x', 'M_y', 'S_x', 'S_y', 'LM_x', 'LM_y', 
                    'r_lum', 'g_lum', 'b_lum', 'targ_lum', 'win_pix', 'min_pix']
    output_params = [rgb2xyz_mat, xyz2rgb_mat, xyz2lms_mat, lms2xyz_mat, 
                    W_x, W_y, L_x, L_y, M_x, M_y, S_x, S_y, LM_x, LM_y, 
                    r_lum, g_lum, b_lum, targ_lum, win_pix, min_pix]
    for index, each in enumerate(output_params):
        params_dict[str(output_labels[index])] = each


    toFile('%s.pickle' %dlg_dict['setup_name'], params_dict)

else:
    print('user cancelled')