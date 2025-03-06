#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

from programmingtheiot.data.SensorData import SensorData

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask

from pisense import SenseHAT

class TemperatureSensorEmulatorTask(BaseSensorSimTask):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, dataSet = None):
		super( \
			TemperatureSensorEmulatorTask, self).__init__( \
				name = ConfigConst.TEMP_SENSOR_NAME, \
				typeID = ConfigConst.TEMP_SENSOR_TYPE)

		enableEmulation = \
			ConfigUtil().getBoolean( \
				ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY)

		self.sh = SenseHAT(emulate = enableEmulation)
	
	def generateTelemetry(self) -> SensorData:
		sensorData = SensorData(name = self.getName() , typeID = self.getTypeID())
		sensorVal = self.sh.environ.temperature

		sensorData.setValue(sensorVal)
		self.latestSensorData = sensorData

		return sensorData
