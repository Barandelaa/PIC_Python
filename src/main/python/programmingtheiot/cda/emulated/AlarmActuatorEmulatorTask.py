import logging

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

from pisense import SenseHAT

class AlarmActuatorEmulatorTask(BaseActuatorSimTask):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        super(AlarmActuatorEmulatorTask, self).__init__(
            name=ConfigConst.ALARM_ACTUATOR_NAME,
            typeID=ConfigConst.ALARM_ACTUATOR_TYPE,
            simpleName="Alarm"
        )

        enableEmulation = ConfigUtil().getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY)

        self.sh = SenseHAT(emulate=enableEmulation)

    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        if self.sh.screen:
            self.sh.screen.scroll_text("ALARM ACTIVATED", size=8)
            return 0
        else:
            logging.warning("No SenseHAT LED screen instance to write.")
            return -1

    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        if self.sh.screen:
            self.sh.screen.clear()
            return 0
        else:
            logging.warning("No SenseHAT LED screen instance to clear / close.")
            return -1 