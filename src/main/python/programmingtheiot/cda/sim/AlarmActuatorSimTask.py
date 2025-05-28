import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask

class AlarmActuatorSimTask(BaseActuatorSimTask):
    def __init__(self):
        super(AlarmActuatorSimTask, self).__init__(
            name=ConfigConst.ALARM_ACTUATOR_NAME,
            typeID=ConfigConst.ALARM_ACTUATOR_TYPE
        )
