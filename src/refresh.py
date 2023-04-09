from common import *

class RefreshRate:
    def __init__(self):
        pass

    def get():
        if debug:
            logging.debug(str(var_refresh) + "Hz")
            return str(var_refresh) + "Hz"
        else:
            var: str = device.shell("getprop debug.oculus.refreshRate")
            logging.debug(var.strip() + "Hz")
            return var.strip() + "Hz"

    def set(value):
        logging.debug("setprop debug.oculus.refreshRate " + value.replace("Hz", ""))
        if not debug:
            device.shell("setprop debug.oculus.refreshRate " + value.replace("Hz", ""))