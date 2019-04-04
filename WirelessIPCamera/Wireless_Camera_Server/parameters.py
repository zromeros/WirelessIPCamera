import json

mqtt_cfg_json = json.loads(open("mqtt/mqtt_cfg.json").read())

""" SOCKET CONFIGURATION """
SOCKET_SERVER_ADDRESS = "0.0.0.0"
SOCKET_UDP_PORT = 4000
SOCKET_UDP_PACKAGE = 1500

""" MQTT CONFIGURATION """
MQTT_HOST = mqtt_cfg_json['host']
MQTT_PORT = mqtt_cfg_json['port']
MQTT_TLS = mqtt_cfg_json['enable_tls']
MQTT_CA = mqtt_cfg_json['ca_path']
MQTT_CERT = mqtt_cfg_json['cert_path']
MQTT_KEY = mqtt_cfg_json['key_path']
MQTT_KEEPALIVE = mqtt_cfg_json['keep_alive']
MQTT_QOS = mqtt_cfg_json['qos']

""" MQTT SUBSCRIPTION TOPICS """
#ruta madre para suscripcion
MQTT_SUB_ID = "AI/ID"

MQTT_SUB_APP_CAMERA = "AI/APP/CAMERA/%s"
MQTT_SUB_APP_SERVER = "AI/APP/SERVER/%s"
MQTT_SUB_CAMERA_APP = "AI/CAMERA/APP/%s"
MQTT_SUB_CAMERA_SERVER = "AI/CAMERA/SERVER/%s"

""" MQTT PUBLISH TOPICS """
MQTT_PUB_TO_CAMERA = "AI/CAMERA/%s"
MQTT_PUB_TO_APP = "AI/APP/%s"

""" MQTT COMMON MESSAGES """
MQTT_UDP_ACK = "AI.UD.OK"