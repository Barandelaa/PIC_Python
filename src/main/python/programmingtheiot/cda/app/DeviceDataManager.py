#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector

class DeviceDataManager(IDataMessageListener):
	"""
	Shell representation of class for student implementation.
	
	"""
	
	def __init__(self):
		self.configUtil = ConfigUtil()

		self.enableSystemPerf = self.configUtil.getBoolean(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.ENABLE_SYSTEM_PERF_KEY)
		
		self.enableSensing = self.configUtil.getBoolean(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.ENABLE_SENSING_KEY)
		
		
		self.enableMqttClient = self.configUtil.getBoolean(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.ENABLE_MQTT_CLIENT_KEY)
		
		self.enableCoapClient = self.configUtil.getBoolean(
			section=ConfigConst.CONSTRAINED_DEVICE,
			key=ConfigConst.ENABLE_COAP_CLIENT_KEY
		)
		
		self.sysPerfMgr = None
		self.sensorAdapterMgr = None
		self.actuatorAdapterMgr = None

		self.mqttClient = None
		self.coapClient = None
		self.coapServer = None

		if self.enableMqttClient:
			logging.info("MQTT client is enabled.")
			self.mqttClient = MqttClientConnector()
			self.mqttClient.setDataMessageListener(self)
		
		if self.enableCoapClient:
			self.coapClient = CoapClientConnector(dataMsgListener=self)

		if self.enableSystemPerf:
			self.sysPerfMgr = SystemPerformanceManager()
			self.sysPerfMgr.setDataMessageListener(self)
			logging.info("Local system performance is enabled.")


		if self.enableSensing:
			self.sensorAdapterMgr = SensorAdapterManager()
			self.sensorAdapterMgr.setDataMessageListener(self)
			logging.info("Local sensor tracking is enabled.")


		self.handleTempChangeOnDevice = self.configUtil.getBoolean(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY)
		
		self.triggerHvacTempFloor = self.configUtil.getFloat(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY)
		
		self.triggerHvacTempCeiling = self.configUtil.getFloat(
			section = ConfigConst.CONSTRAINED_DEVICE,
			key = ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY)
		
			
	def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
		"""
		Retrieves the named actuator data (response) item from the internal data cache.
		
		@param name
		@return ActuatorData
		"""
		pass
		
	def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
		"""
		Retrieves the named sensor data item from the internal data cache.
		
		@param name
		@return SensorData
		"""
		pass
	
	def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
		"""
		Retrieves the named system performance data from the internal data cache.
		
		@param name
		@return SystemPerformanceData
		"""
		pass
	
	def handleActuatorCommandMessage(self, data: ActuatorData) -> bool:
		"""
		This callback method will be invoked by the connection that's handling
		an incoming ActuatorData command message.
		
		@param data The incoming ActuatorData command message.
		@return boolean
		"""
		logging.info(f"Handling actuador data: {str(data)}")
		if data:
			logging.info("Processing actuator command message.")
			if self.actuatorAdapterMgr:
				return self.actuatorAdapterMgr.sendActuatorCommand(data)
			return None
		else: 
			logging.warning("Incoming atuator command is invalid (null). Ignoring")
			return None
	
	def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
		"""
		This callback method will be invoked by the actuator manager that just
		processed an ActuatorData command, which creates a new ActuatorData
		instance and sets it as a response before calling this method.
		
		@param data The incoming ActuatorData response message.
		@return boolean
		"""
		if data:
			logging.debug("Incoming actuator response received (from actuator manager): " + str(data))

			# store the data in the cache
			self.actuatorResponseCache[data.getName()] = data

			# convert ActuatorData to JSON and get the msg resource
			actuatorMsg = DataUtil().actuatorDataToJson(data)
			resourceName = ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE

			# delegate to the transmit function any potential upstream comm's
			self._handleUpstreamTransmission(resource = resourceName, msg = actuatorMsg)

			return True
		else:
			logging.warning("Incoming actuator response is invalid (null). Ignoring.")

			return False
	
	def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
		"""
		This callback method is generic and designed to handle any incoming string-based
		message, which will likely be JSON-formatted and need to be converted to the appropriate
		data type. You may not need to use this callback at all.
		
		@param data The incoming JSON message.
		@return boolean
		"""
		logging.debug("handleIncomingMessage() called")
		if msg:
			logging.debug("Incoming message received: " + str(msg))
			self._handleIncomingDataAnalysis(msg)
			return True
		else:
			logging.warning("Incoming message is invalid (null). Ignoring.")
			return False
	
	def handleSensorMessage(self, data: SensorData) -> bool:
		if data:
			logging.info("Incoming sensor data received (from sensor manager): " + str(data))

			self._handleSensorDataAnalysis(data = data)
			jsonData = DataUtil().sensorDataToJson(data = data)
			self._handleUpstreamTransmission(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, msg = jsonData)

			return True
		else:
			logging.warning("Incoming sensor data is invalid (null). Ignoring.")

			return False
	
	def handleSystemPerformanceMessage(self, data: SystemPerformanceData) -> bool:
		"""
		This callback method will be invoked by the system performance manager that just
		processed a new sensor reading, which creates a new SystemPerformanceData instance
		that will be passed to this method.
		
		@param data The incoming SystemPerformanceData message.
		@return boolean
		"""
		if data:
			logging.debug("Incoming system performance message received (from sys perf manager): " + str(data))
			return True
		else:
			logging.warning("Incoming system performance data is invalid (null). Ignoring.")
			return False
	
	def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
		pass
			
	def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
		pass
			
	def startManager(self):
		logging.info("Starting DeviceDataManager...")

		if self.sysPerfMgr:
			self.sysPerfMgr.startManager()

		if self.sensorAdapterMgr:
			self.sensorAdapterMgr.startManager()
		
		if self.mqttClient:
			self.mqttClient.connectClient()
			self.mqttClient.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, callback = None, qos = ConfigConst.DEFAULT_QOS)

		logging.info("Started DeviceDataManager.")
		
	def stopManager(self):
		logging.info("Stopping DeviceDataManager...")

		if self.sysPerfMgr:
			self.sysPerfMgr.stopManager()

		if self.sensorAdapterMgr:
			self.sensorAdapterMgr.stopManager()
		
		if self.mqttClient:
			self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
			self.mqttClient.disconnectClient()

		logging.info("Stopped DeviceDataManager.")
		
	def _handleIncomingDataAnalysis(self, msg: str):
		"""
		Call this from handleIncomeMessage() to determine if there's
		any action to take on the message. Steps to take:
		1) Validate msg: Most will be ActuatorData, but you may pass other info as well.
		2) Convert msg: Use DataUtil to convert if appropriate.
		3) Act on msg: Determine what - if any - action is required, and execute.
		"""
		pass
		
	def _handleSensorDataAnalysis(self, data: SensorData):
		"""
		Call this from handleSensorMessage() to determine if there's
		any action to take on the message. Steps to take:
		1) Check config: Is there a rule or flag that requires immediate processing of data?
		2) Act on data: If # 1 is true, determine what - if any - action is required, and execute.
		"""
		if self.handleTempChangeOnDevice and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
			logging.info(f"Handle temp change: {str(self.handleTempChangeOnDevice)} - type ID: {str(data.getTypeID())}")

			ad = ActuatorData(typeID = ConfigConst.HVAC_ACTUATOR_TYPE)

			if data.getValue() > self.triggerHvacTempCeiling:
				ad.setCommand(ConfigConst.COMMAND_ON)
				ad.setValue(self.triggerHvacTempCeiling)
			elif data.getValue() < self.triggerHvacTempFloor:
				ad.setCommand(ConfigConst.COMMAND_ON)
				ad.setValue(self.triggerHvacTempFloor)
			else:
				ad.setCommand(ConfigConst.COMMAND_OFF)

			ad.setName(ConfigConst.HVAC_ACTUATOR_NAME)
			self.handleActuatorCommandMessage(ad)
		
	def _handleUpstreamTransmission(self, resource = None, msg: str = None):
		logging.info("Upstream transmission invoked. Checking comm's integration.")

		if self.mqttClient:
			if self.mqttClient.publishMessage(resource = resource, msg = msg):
				logging.debug("Published incoming data to resource (MQTT): %s", str(resource))
			else:
				logging.warning("Failed to publish incoming data to resource (MQTT): %s", str(resource))

		if self.coapClient:
			if self.coapClient.sendPutRequest(resource = resource, payload = msg):
				logging.debug("Put incoming message data to resource (CoAP): %s", str(resource))
			else:
				logging.warning("Failed to put incoming message data to resource (CoAP): %s", str(resource))