import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator

class LightSensorSimTask(BaseSensorSimTask):
    def __init__(self, dataSet=None):
        super(LightSensorSimTask, self).__init__(
            name=ConfigConst.LIGHT_SENSOR_NAME,
            typeID=ConfigConst.LIGHT_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=0.0,      # Valor mínimo de luz (puedes ajustar)
            maxVal=1000.0    # Valor máximo de luz (puedes ajustar)
        )
