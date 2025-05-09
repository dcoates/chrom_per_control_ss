import sys

import u3

CHANNEL_RLED=0
CHANNEL_GLED=1
CHANNEL_ON_OFF=2
CHANNEL_STIM=3
CHANNEL_FIX=4
CHANNEL_HIT=5
CHANNEL_FA=6

dev = u3.U3()
dev.getCalibrationData()

channels=["RLED","GLED", # 01
       "on_off", "stim", "stim_fix", #234 ("stimulusprogram","stimulus","fixstimulus")
       "hit","fa"] #56: ("good","bad")

def labjack_config():
    fios = 0x03 # Make FIO0 and FIO1 analog, the rest digital
    dev.configIO(FIOAnalog=fios)

def labjack_read():
    """ returns values as both an array and (for convenience)
        a dictionary. Can access dict like: dict_values["GLED"]
        """

    values=[dev.getDIOState(n) for n in [2,2,2,3,4,5,6]]
    values[0] = dev.getAIN(0)
    values[1] = dev.getAIN(1)

    values_dict={}
    for key,item in zip(channels,values):
        values_dict[key] = item
    return values,values_dict

