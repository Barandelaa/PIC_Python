import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import (
    DefaultDataMessageListener,
)
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.DataUtil import DataUtil

from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil


class MqttClientControlPacketTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    MqttClientConnector. It should not be considered complete,
    but serve as a starting point for the student implementing
    additional functionality within their Programming the IoT
    environment.
    """

    @classmethod
    def setUpClass(self):
        logging.basicConfig(
            format="%(asctime)s:%(module)s:%(levelname)s:%(message)s",
            level=logging.DEBUG,
        )
        logging.info("Testing MqttClientConnector class...")

        self.cfg = ConfigUtil()

        # Be sure to use a DIFFERENT clientID than that which is used
        # for your CDA when running separately from this test
        self.mcc = MqttClientConnector(clientID="MyTestMqttClient123")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConnectAndDisconnect(self):
        self.assertTrue(self.mcc.connectClient())

        sleep(5)

        self.assertTrue(self.mcc.disconnectClient())

    def testServerPing(self):
        self.mcc.connectClient()

        sleep(2)

        self.assertTrue(self.mcc.mqttClient.is_connected())

        self.mcc.disconnectClient()

    def testPubSub(self):
        # IMPORTANT: be sure to use QoS 1 and 2 to see ALL control packets

        self.mcc.setDataMessageListener(DefaultDataMessageListener())
        self.mcc.connectClient()

        for qos in [1, 2]:

            # Test publishing a message
            actuatorData = ActuatorData()
            actuatorDataJson = DataUtil().actuatorDataToJson(actuatorData)

            self.mcc.publishMessage(
                resource=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
                msg=actuatorDataJson,
                qos=qos,
            )

            sleep(2)

            # Test subscribing to a message
            self.mcc.subscribeToTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos)

            sleep(2)

            # Now with sensor data
            sensorData = SensorData()
            sensorDataJson = DataUtil().sensorDataToJson(sensorData)

            self.mcc.publishMessage(
                resource=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE,
                msg=sensorDataJson,
                qos=qos,
            )

            sleep(2)

            self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mcc.subscribeToTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, qos)

            # Now with system performance data
            sysPerfData = SystemPerformanceData()
            sysPerfDataJson = DataUtil().systemPerformanceDataToJson(sysPerfData)

            self.mcc.publishMessage(
                resource=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                msg=sysPerfDataJson,
                qos=qos,
            )

            sleep(2)

            self.mcc.unsubscribeFromTopic(ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE)
            self.mcc.subscribeToTopic(
                ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, qos
            )

        sleep(2)
        self.mcc.disconnectClient()


if __name__ == "__main__":
    unittest.main()