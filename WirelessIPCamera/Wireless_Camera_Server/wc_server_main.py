import threading
import subprocess
import wc_mqtt_main as mqtt
#from sock import wc_server_udp_rx as udp

def cmd():
    print("me conecto")
    comando = "C:\Program Files\mosquitto\mosquitto.exe"
    subprocess.run(comando, shell=True)

if __name__ == '__main__':
    cmd_thread = threading.Thread(target=cmd)
    cmd_thread.start()
    mqtt_thread = threading.Thread(target=mqtt.init)
    mqtt_thread.start()
    print("listo")
    #udp_thread = threading.Thread(target=udp.init)
    #udp_thread.start()
    #udp.main()