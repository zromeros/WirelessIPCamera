import crc8
import parameters as PARAM

def camera_subscriptions(mqtt):
    topics = [PARAM.MQTT_SUB_APP_CAMERA % mqtt.camera_id,
              PARAM.MQTT_SUB_APP_SERVER % mqtt.camera_id,
              PARAM.MQTT_SUB_CAMERA_APP % mqtt.camera_id,
              PARAM.MQTT_SUB_CAMERA_SERVER % mqtt.camera_id]
    for topic in topics:
        mqtt.subscribe(topic)


def from_app_to_camera(mqtt, payload):
    topic = PARAM.MQTT_PUB_TO_CAMERA % mqtt.camera_id
    payload = create_verification_crc8(payload)
    mqtt.publish(topic, payload)


def from_app_to_server(mqtt, payload):
    mqtt.logger.info("Message from App to Server. Camera_ID: {0}, Payload:{1}".format(mqtt.camera_id, payload))


def from_camera_to_app(mqtt, payload):
    topic = PARAM.MQTT_PUB_TO_APP % mqtt.camera_id
    mqtt.publish(topic, payload)


def from_camera_to_server(mqtt, payload):
    mqtt.logger.info("Message from Camera to Server. Camera_ID: {0}, Payload:{1}".format(mqtt.camera_id, payload))
    # para pedir informacion como status, tiempo etc


def create_verification_crc8(payload):
    hash = crc8.crc8()
    hash.update(payload.encode())
    return (payload + hash.hexdigest()).upper()