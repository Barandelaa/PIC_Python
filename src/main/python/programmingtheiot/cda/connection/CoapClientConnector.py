#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import socket

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient

from programmingtheiot.data.DataUtil import DataUtil

import asyncio
import traceback

from aiocoap import *

from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from coapthon.utils import generate_random_token

class CoapClientConnector(IRequestResponseClient):
	"""
	Shell representation of class for student implementation.
	
	"""
	
	def __init__(self, dataMsgListener: IDataMessageListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		self.coapClient = None

		self.observeRequests = {}

		self.host = self.config.getProperty(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.HOST_KEY,
			ConfigConst.DEFAULT_HOST
		)
		self.port = self.config.getInteger(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.PORT_KEY,
			ConfigConst.DEFAULT_COAP_PORT
		)
		self.uriPath = "coap://" + self.host + ":" + str(self.port) + "/"

		logging.info('\tHost:Port: %s:%s', self.host, str(self.port))

		self.includeDebugLogDetail = True

		try:
			tmpHost = socket.gethostbyname(self.host)

			if tmpHost:
				self.host = tmpHost
				self._initClient()
			else:
				logging.error("Can't resolve host: " + self.host)

		except socket.gaierror:
			logging.info("Failed to resolve host: " + self.host)
	
	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		logging.info("Discovering remote resources...")

		return self.sendGetRequest(
				resource=None,
				name='.well-known/core',
				enableCON=False,
				timeout=timeout
			)
	
	def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None):
		resourcePath = ""
		hasResource = False

		if resource:
			resourcePath = resourcePath + resource.value
			hasResource = True

		if name:
			if hasResource:
				resourcePath = resourcePath + '/'

			resourcePath = resourcePath + name

		return resourcePath

	def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing DELETE with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.DELETE, path=resourcePath)
			request.token = generate_random_token(2)

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onDeleteResponse,
				timeout=timeout
			)
		else:
			logging.warning("Can't test DELETE - no path or path list provided.")
	
	def _onDeleteResponse(self, response):
		if not response:
			logging.warning('DELETE response invalid. Ignoring.')
			return

		logging.info('DELETE response received: %s', response.payload)


	def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing GET with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.GET, path=resourcePath)
			request.token = generate_random_token(2)

			if not enableCON:
				request.type = defines.Types["NON"]

			response = self.coapClient.send_request(request=request, timeout=timeout)

			self._onGetResponse(response=response, resourcePath=resourcePath)
		else:
			logging.warning("Can't test GET - no path or path list provided.")

	def _onGetResponse(self, response, resourcePath: str = None):
		if not response:
			logging.warning('GET response invalid. Ignoring.')
			return

		logging.info('GET response received.')

		jsonData = response.payload
		locationPath = resourcePath.split('/') if resourcePath else []

		if len(locationPath) > 2:
			dataType = locationPath[2]

			if dataType == ConfigConst.ACTUATOR_CMD:
				# TODO: convert payload to ActuatorData and verify!
				logging.info("ActuatorData received: %s", jsonData)

				try:
					ad = DataUtil().jsonToActuatorData(jsonData)

					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					return
			else:
				logging.info("Response data received. Payload: %s", jsonData)
		else:
			logging.info("Response data received. Payload: %s", jsonData)


	def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing POST with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.POST, path=resourcePath)
			request.token = generate_random_token(2)
			request.payload = payload

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onPostResponse,
				timeout=timeout
			)	
		else:
			logging.warning("Can't test POST - no path or path list provided.")
		
	def _onPostResponse(self, response):
		if not response:
			logging.warning('POST response invalid. Ignoring.')
			return

		logging.info('POST response received: %s', response.payload)


	def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			logging.info("Issuing PUT with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.PUT, path=resourcePath)
			request.token = generate_random_token(2)
			request.payload = payload

			if not enableCON:
				request.type = defines.Types["NON"]

			self.coapClient.send_request(
				request=request,
				callback=self._onPutResponse,
				timeout=timeout
			)
		else:
			logging.warning("Can't test PUT - no path or path list provided.")
	
	def _onPutResponse(self, response):
		if not response:
			logging.warning('PUT response invalid. Ignoring.')
			return

		logging.info('PUT response received: %s', response.payload)

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		"""
		Set the data message listener.
		"""
		if listener is not None:
			self.dataMsgListener = listener
			return True
		else:
			logging.error("Invalid data message listener.")
			return False

	def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
		if resource or name:
				resourcePath = self._createResourcePath(resource, name)

				if resourcePath in self.observeRequests:
					logging.warning("Already observing resource %s. Ignoring start observe request.", resourcePath)
					return

				self.observeRequests[resourcePath] = None

				observeActuatorCmdHandler = HandleActuatorEvent(
					listener=self.dataMsgListener,
					resourcePath=resourcePath,
					requests=self.observeRequests
				)

				try:
					self.coapClient.observe(
						path=resourcePath,
						callback=observeActuatorCmdHandler.handleActuatorResponse
					)
				except Exception as e:
					logging.warning("Failed to observe path: " + resourcePath)
		else:
			logging.warning("Can't start observe - no path or path list provided.")

	def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)

			if resourcePath not in self.observeRequests:
				logging.warning("Resource %s not being observed. Ignoring stop observe request.", resourcePath)
				return

			response = self.observeRequests[resourcePath]

			if response:
				logging.info("Canceling observe for resource %s.", resourcePath)

				try:
					self.coapClient.cancel_observing(response=response, send_rst=True)
					del self.observeRequests[resourcePath]
					logging.info("Canceled observe for resource %s.", resourcePath)
				except Exception as e:
					logging.warning("Failed to cancel observe for resource %s.", resourcePath)
			else:
				logging.warning("No response yet for observed resource %s. Attempting to stop anyway.", resourcePath)

				try:
					self.coapClient.cancel_observing(response=None, send_rst=True)
					logging.info("Canceled observe for resource %s.", resourcePath)
				except Exception as e:
					logging.warning("Failed to cancel observe for resource %s.", resourcePath)
		else:
			logging.warning("Can't stop observe - no path or path list provided.")

	
	def _initClient(self):
		try:
			self.coapClient = HelperClient(server=(self.host, self.port))
			logging.info('Client created. Will invoke resources at: ' + self.uriPath)
		except Exception as e:
			# obviously, this is a critical failure - you may want to handle this differently
			logging.error("Failed to create CoAP client to URI path: " + self.uriPath)
			traceback.print_exception(type(e), e, e.__traceback__)

class HandleActuatorEvent:
    def __init__(
        self,
        listener: IDataMessageListener = None,
        resourcePath: str = None,
        requests=None
    ):
        self.listener = listener
        self.resourcePath = resourcePath
        self.observeRequests = requests

    def handleActuatorResponse(self, response):
        if response:
            jsonData = response.payload

            self.observeRequests[self.resourcePath] = response

            logging.info(
                "Received actuator command response to resource %s: %s",
                self.resourcePath, jsonData
            )

            if self.listener:
                try:
                    data = DataUtil().jsonToActuatorData(jsonData=jsonData)
                    self.listener.handleActuatorCommandMessage(data=data)
                except Exception:
                    logging.warning(
                        "Failed to decode actuator data for resource %s. Ignoring: %s",
                        self.resourcePath, jsonData
                    )
