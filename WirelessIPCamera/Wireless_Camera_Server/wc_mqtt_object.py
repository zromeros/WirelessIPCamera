import logging
import ssl

import paho.mqtt.client as paho

import parameters as PARAM
import wc_server_manager as handler

logging.basicConfig(level=logging.INFO) #Tiene que ver con los hilos


class MqttObject(object):
    def __init__(self, listener=False, camera_id=None):
        self.connect = False
        self.listener = listener
        self.camera_id = camera_id
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        self.logger.debug("Result of connection: {0}".format(rc))

    def subscribe(self, topic=None):
        if self.listener:
            res = self.mqttc.subscribe(topic, qos=PARAM.MQTT_QOS)
            self.logger.info("Suscribed to: {0}".format(topic))

    def publish(self, topic, payload):
        res = self.mqttc.publish(topic, payload, qos=PARAM.MQTT_QOS)
        if res.rc == 0:
            self.logger.info("Message published: Topic: {0}, Payload:{1}".format(topic, payload))
        else:
            self.logger.error("Message not published: Topic: {0}, Payload:{1}".format(topic, payload))

    def __on_message(self, client, userdata, msg):
        self.logger.info("Topic: {0} Message: {1}".format(msg.topic, msg.payload.decode()))
        self.validate_sub(msg.topic, msg.payload.decode())

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client(self.camera_id)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message
        self.mqttc.on_log = self.__on_log
        if PARAM.MQTT_TLS:
            self.mqttc.tls_set(PARAM.MQTT_CA, certfile=PARAM.MQTT_CERT,
                               keyfile=PARAM.MQTT_KEY, cert_reqs=ssl.CERT_REQUIRED,
                               tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

        result_of_connection = self.mqttc.connect(PARAM.MQTT_HOST, PARAM.MQTT_PORT, keepalive=PARAM.MQTT_KEEPALIVE)
        if result_of_connection == 0:
            self.connect = True
            handler.camera_subscriptions(self)
        return self

    def start(self):
        self.mqttc.loop_start()
        while True:
            if self.connect == True:
                continue
            else:
                self.logger.debug("Attempting to connect.")

    def validate_sub(self, topic, payload):
        topic = topic.split("/")
        if topic[0] == "AI": #identificador alter info
            if topic[1] == "APP": #origen
                if topic[2] == "CAMERA": #destino
                    if topic[3] == self.camera_id: #Id de la camara
                        handler.from_app_to_camera(self, payload) #funcion para comprobar contenido del msj
                elif topic[2] == "SERVER":
                    if topic[3] == self.camera_id:
                        handler.from_app_to_server(self, payload)
                else:
                    self.logger.error("Invalid topic")
            elif topic[1] == "CAMERA":
                if topic[2] == "APP":
                    if topic[3] == self.camera_id:
                        handler.from_camera_to_app(self, payload)
                elif topic[2] == "SERVER":
                    if topic[3] == self.camera_id:
                        handler.from_camera_to_server(self, payload)
                else:
                    self.logger.error("Invalid topic")
            else:
                self.logger.error("Invalid topic")
        else:
            self.logger.error("Invalid topic")

