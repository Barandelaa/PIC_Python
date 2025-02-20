#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import random

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.data.ActuatorData import ActuatorData

class BaseActuatorSimTask():
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, name: str = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, simpleName: str = "Actuator"):
		self.latestActuatorResponse = ActuatorData(typeID = typeID, name = name)
		self.latestActuatorResponse.setAsResponse()

		self.name = name
		self.typeID = typeID
		self.simpleName = simpleName
		self.lastKnownCommand = ConfigConst.DEFAULT_COMMAND
		self.lastKnownValue = ConfigConst.DEFAULT_VAL
		
	def getLatestActuatorResponse(self) -> ActuatorData:
		"""
		This can return the current ActuatorData response instance or a copy.
		"""
		pass
	
	def getSimpleName(self) -> str:
		pass
	
	def updateActuator(self, data: ActuatorData) -> bool:
		"""
		NOTE: If 'data' is valid, the actuator-specific work can be delegated
		as follows:
		 - if command is ON: call self._activateActuator()
		 - if command is OFF: call self._deactivateActuator()
		
		Both of these methods will have a generic implementation (logging only) within
		this base class, although the sub-class may override if preferable.
		"""
		if data and self.typeID == data.getTypeID():
			statusCode = ConfigConst.DEFAULT_STATUS

		curCommand = data.getCommand()
		curVal     = data.getValue()

		# check if the command or value is a repeat from previous
		# if so, ignore the command and return None to caller
		#
		# but - whether ON or OFF - allow a new value to be set
		if curCommand == self.lastKnownCommand and curVal == self.lastKnownValue:
			logging.debug( \
				"New actuator command and value is a repeat. Ignoring: %s %s", \
				str(curCommand), str(curVal))
		else:
			logging.debug( \
				"New actuator command and value to be applied: %s %s", \
				str(curCommand), str(curVal))

			if curCommand == ConfigConst.COMMAND_ON:
				logging.info("Activating actuator...")
				statusCode = self._activateActuator(val = data.getValue(), stateData = data.getStateData())
			elif curCommand == ConfigConst.COMMAND_OFF:
				logging.info("Deactivating actuator...")
				statusCode = self._deactivateActuator(val = data.getValue(), stateData = data.getStateData())
			else:
				logging.warning("ActuatorData command is unknown. Ignoring: %s", str(curCommand))
				statusCode = -1

			# update the last known actuator command and value
			self.lastKnownCommand = curCommand
			self.lastKnownValue = curVal

			# create the ActuatorData response from the original command
			actuatorResponse = ActuatorData()
			actuatorResponse.updateData(data)
			actuatorResponse.setStatusCode(statusCode)
			actuatorResponse.setAsResponse()

			self.latestActuatorResponse.updateData(actuatorResponse)

			return actuatorResponse

		return None
		
	def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Implement basic logging. Actuator-specific functionality should be implemented by sub-class.
		
		@param val The actuation activation value to process.
		@param stateData The string state data to use in processing the command.
		"""
		msg = "\n*******"
		msg = msg + "\n* O N *"
		msg = msg + "\n*******"
		msg = msg + "\n" + self.name + " VALUE -> " + str(val) + "\n======="

		logging.info("Simulating %s actuator ON: %s", self.name, msg)

		return 0
		
	def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
		"""
		Implement basic logging. Actuator-specific functionality should be implemented by sub-class.
		
		@param val The actuation activation value to process.
		@param stateData The string state data to use in processing the command.
		"""
		msg = "\n*******"
		msg = msg + "\n* OFF *"
		msg = msg + "\n*******"

		logging.info("Simulating %s actuator OFF: %s", self.name, msg)

		return 0
			