import paho.mqtt.client as paho
import ssl
import logging
import threading
import parameters as PARAM
import wc_mqtt_object as Mqtt


logging.basicConfig(level=logging.INFO)  #Tiene que ver con los hilos

def create_mqtt_thread(payload):
    Mqtt.MqttObject(listener=True, camera_id=payload).bootstrap_mqtt().start() #Hilo MQTT (Se inicia)


class MqttMain(object):
    def __init__(self, listener=False, cameras_id=[]):
        self.connect = False
        self.listener = listener
        self.cameras_id = cameras_id
        self.logger = logging.getLogger(repr(self))

    def __on_connect(self, client, userdata, flags, rc):
        self.connect = True
        if self.listener:
            self.mqttc.subscribe(PARAM.MQTT_SUB_ID, qos=PARAM.MQTT_QOS)
            self.logger.info("Suscribed to: {0}".format(PARAM.MQTT_SUB_ID))

        # inicar threads para cada camara ya registrada en la base de datos
        #new_thread = threading.Thread(target=create_mqtt_thread, args=(payload,))
        #new_thread.start()
        self.logger.debug("Result of connection: {0}".format(rc))

    def __on_message(self, client, userdata, msg):
        self.logger.info("Topic: {0} Message: {1}".format(msg.topic, msg.payload.decode()))
        self.validate_sub(msg.topic, msg.payload.decode())

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def bootstrap_mqtt(self):
        self.mqttc = paho.Client("Server")
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message
        self.mqttc.on_log = self.__on_log

        #Habilitar cuando se quiera introducir TLS
        if PARAM.MQTT_TLS:
            self.mqttc.tls_set(PARAM.MQTT_CA, certfile=PARAM.MQTT_CERT,
                               keyfile=PARAM.MQTT_KEY, cert_reqs=ssl.CERT_REQUIRED,
                               tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

        result_of_connection = self.mqttc.connect(PARAM.MQTT_HOST, PARAM.MQTT_PORT, keepalive=PARAM.MQTT_KEEPALIVE)
        if result_of_connection == 0:
            self.connect = True
        return self

    def start(self):
        self.mqttc.loop_start()
        while True:
            if self.connect == True:
                continue
            else:
                self.logger.debug("Attempting to connect.")

    def validate_sub(self, topic, payload):
        topic = topic.split("/")  #ELIMINA ESTE CARACTER DE LA LISTA
        if topic[0] == "AI":
            if topic[1] == "ID":
                # Verifica unicidad de id de la camara
                if payload not in self.cameras_id:
                    self.cameras_id.append(payload)
                    #  guardar en base de datos la nueva camara
                    # Iniciar una thread para cada cada conexion mqtt
                    new_thread = threading.Thread(target=create_mqtt_thread, args=(payload,))
                    new_thread.start()
                    # Guardar id en base de datos
                else:
                    self.logger.error("Camera ID already exist in database")
            else:
                self.logger.error("Invalid topic")
        else:
            self.logger.error("Invalid topic")


def init():
    # obtener la lista de las id de las camaras en la base de datos
    cameras_id = []
    MqttMain(listener=True, cameras_id=cameras_id).bootstrap_mqtt().start()

#opcional
