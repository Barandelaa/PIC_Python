#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import paho.mqtt.client as mqttClient

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientConnector(IPubSubClient):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, clientID: str = None):
		"""
		Default constructor. This will set remote broker information and client connection
		information based on the default configuration file contents.
		
		@param clientID Defaults to None. Can be set by caller. If this is used, it's
		critically important that a unique, non-conflicting name be used so to avoid
		causing the MQTT broker to disconnect any client using the same name. With
		auto-reconnect enabled, this can cause a race condition where each client with
		the same clientID continuously attempts to re-connect, causing the broker to
		disconnect the previous instance.
		"""
		self.config = ConfigUtil()
		self.dataMessageListener = None
		self.host = self.config.getProperty(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.HOST_KEY,
			ConfigConst.DEFAULT_HOST
		)
		self.port =self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.PORT_KEY, 
			ConfigConst.DEFAULT_MQTT_PORT)
		
		self.keepAlive = self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.KEEP_ALIVE_KEY, 
			ConfigConst.DEFAULT_KEEP_ALIVE
			)
		
		self.defaultQoS = self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.DEFAULT_QOS_KEY, 
			ConfigConst.DEFAULT_QOS
		)

		self.enableEncryption = \
			self.config.getBoolean( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.ENABLE_CRYPT_KEY)

		self.pemFileName = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.CERT_FILE_KEY)

		self.mqttClient = None

		if clientID is None:
			self.clientID = self.config.getProperty(
				ConfigConst.CONSTRAINED_DEVICE, 
				ConfigConst.DEVICE_LOCATION_ID_KEY
			)
		else:
			self.clientID = clientID

		start_message = f"\n\tMQTT Client ID: {self.clientID}\n\tMQTT Broker Host: {self.host}\n\tMQTT Broker Port: {self.port}\n\tMQTT Keep Alive: {self.keepAlive}"
		logging.info(start_message)

	def connectClient(self, cleanSession: bool = True) -> bool:
		if not self.mqttClient:
			self.mqttClient = mqttClient.Client(
				client_id = self.clientID, clean_session = cleanSession)
			
			try:
				if self.enableEncryption:
					logging.info("Enabling TLS encryption...")

					self.port = self.config.getInteger(
						ConfigConst.MQTT_GATEWAY_SERVICE, 
						ConfigConst.SECURE_PORT_KEY, 
						ConfigConst.DEFAULT_MQTT_SECURE_PORT
						)

					# see https://docs.python.org/3/library/ssl.html for more options.
					self.mqttClient.tls_set(self.pemFileName, tls_version = ssl.PROTOCOL_TLS_CLIENT)
			except:
				logging.warning("Failed to enable TLS encryption. Using unencrypted connection.")

			self.mqttClient.on_connect = self.onConnect
			self.mqttClient.on_disconnect = self.onDisconnect
			self.mqttClient.on_message = self.onMessage
			self.mqttClient.on_publish = self.onPublish
			self.mqttClient.on_subscribe = self.onSubscribe

		if not self.mqttClient.is_connected():
			try:
				self.mqttClient.connect(self.host, self.port, self.keepAlive)
				self.mqttClient.loop_start()
				logging.info('MQTT client connecting to broker at host: ' + self.host)
				return True
			except Exception as e:
				logging.error("Failed to connect to MQTT broker. Exception: " + str(e))
				return False
		else:
			logging.warning('MQTT client is already connected. Ignoring connect request.')

			return True
		
	def disconnectClient(self) -> bool:
		if self.mqttClient.is_connected():
			try:
				self.mqttClient.loop_stop()
				self.mqttClient.disconnect()
				logging.info('Disconnecting MQTT client from broker: ' + self.host)
				return True
			except Exception as e:
				logging.error("Failed to disconnect from MQTT broker. Exception: " + str(e))
				return False
			
		else:
			logging.warning('MQTT client already disconnected. Ignoring.')

			return True
		
	def onConnect(self, client, userdata, flags, rc):
		logging.info('[Callback] Connected to MQTT broker. Result code: ' + str(rc))

		self.mqttClient.subscribe( \
			topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value, qos = self.defaultQoS)

		self.mqttClient.message_callback_add( \
			sub = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value, \
			callback = self.onActuatorCommandMessage)		
		
	def onDisconnect(self, client, userdata, rc):
		logging.info('MQTT client disconnected from broker: ' + str(client))
		
	def onMessage(self, client, userdata, msg: mqttClient.MQTTMessage):
		payload = msg.payload
		
		if payload:
			payload = payload.decode('utf-8')
			logging.info('Received message with payload: ' + payload)
		
		else:
			logging.warning('Received message with empty payload.')

	def onPublish(self, client, userdata, mid):
		logging.info('MQTT client published message: ' + str(client))
	
	def onSubscribe(self, client, userdata, mid, granted_qos):
		logging.info('MQTT client subscribed: ' + str(client))
	
	def onActuatorCommandMessage(self, client, userdata, msg):
		"""
		This callback is defined as a convenience, but does not
		need to be used and can be ignored.
		
		It's simply an example for how you can create your own
		custom callback for incoming messages from a specific
		topic subscription (such as for actuator commands).
		
		@param client The client reference context.
		@param userdata The user reference context.
		@param msg The message context, including the embedded payload.
		"""
		logging.info('[Callback] Actuator command message received. Topic: %s.', msg.topic)

		if self.dataMessageListener:
			try:
				# assumes all data is encoded using UTF-8 (between GDA and CDA)
				actuatorData = DataUtil().jsonToActuatorData(msg.payload.decode('utf-8'))
				#logging.info('Actuator command message payload converted to ActuatorData: ' + str(actuatorData))

				self.dataMessageListener.handleActuatorCommandMessage(actuatorData)
			except:
				logging.exception("Failed to convert incoming actuation command payload to ActuatorData: ")
		
	def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		logging.info('Publishing message to topic: ' + str(resource))
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot publish message.')
			return False

		# check validity of message
		if not msg:
			logging.warning('No message specified. Cannot publish message to topic: ' + resource.value)
			return False

		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		# publish message, and wait for publish to complete before returning
		msgInfo = self.mqttClient.publish(topic = resource.value, payload = msg, qos = qos)
		#msgInfo.wait_for_publish()

		return True
	
	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot subscribe.')
			return False

		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		# subscribe to topic
		logging.info(f'Subscribing to topic {resource.value}')
		self.mqttClient.subscribe(resource.value, qos)

		return True
	
	def unsubscribeFromTopic(self, resource: ResourceNameEnum = None):
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot unsubscribe.')
			return False

		logging.info(f'Unsubscribing to topic {resource.value}')
		self.mqttClient.unsubscribe(resource.value)

		return True
	
	def pingBroker(self) -> bool:
		# check if client is connected
		if self.mqttClient.is_connected():
			self.mqttClient._send_pingreq()
			logging.info('PINGREQ sent to broker: ' + self.host)
			return True
		else:
			logging.warning('MQTT client not connected. Cannot send PINGREQ.')
			return False

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		if listener:
			self.dataMessageListener = listener
			return True
		else:
			return False