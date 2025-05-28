import logging
import random

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.data.SensorData import SensorData

class LightSensorEmulatorTask(BaseSensorSimTask):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        super(LightSensorEmulatorTask, self).__init__(
            name=ConfigConst.LIGHT_SENSOR_NAME,
            typeID=ConfigConst.LIGHT_SENSOR_TYPE
        )

    def generateTelemetry(self) -> SensorData:
        """
        Generate simulated light sensor data.
        """
        sensorData = SensorData(name=self.name, typeID=self.typeID)
        sensorData.setValue(random.uniform(0.0, 1000.0))  # Simular valores de luz entre 0 y 1000
        return sensorData 