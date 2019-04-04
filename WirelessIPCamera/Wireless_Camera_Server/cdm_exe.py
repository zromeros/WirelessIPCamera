import subprocess

def cmd(comando):
    subprocess.run(comando, shell=True)
def init():
    comando = "C:\Program Files\mosquitto\mosquitto.exe"
    cmd(comando)
init()
