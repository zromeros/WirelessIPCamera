import socket
import threading as th
import cv2
import os

server_address = "0.0.0.0"
server_port = 4000
PACKAGE = 1500
showFrame = False
imIdx = 0
image_folder = "C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock\\img_"

def create_server_udp(address, port):
    # Initialize Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((address, port))
    return s

def streamVideo():
    global showFrame
    index = 0
    while True:

        img = cv2.imread('img_{:08}.jpg'.format(index), 1)
        index += 1
        try:
            cv2.imshow("video", img)
            os.remove(image_folder + "{:08}.jpg".format(index - 1))
            cv2.waitKey(86)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        except:
            continue


def receiveData():
    # Inilitialize server
    global showFrame
    global imIdx
    s = create_server_udp(server_address, server_port)
    imIdx = 0
    noData = True
    endImage = False


    while True:

        if (imIdx == 10) & (endImage == True):
            strVideo = th.Thread(target=streamVideo)
            strVideo.start()

        input_data, client_address = s.recvfrom(PACKAGE)
        f = open("package.log", "ab")
        f.write(input_data)
        print(len(input_data))

        # Buscar ambos indices por separado
        try:
            # Indice de inicio
            idx0 =  input_data.index(b'\xff\xd8\xff')
            beginImage = True

        except:
            beginImage = False
        try:
            # Indice de final
            idx1 = input_data.index(b'\xff\xd9')
            endImage = True
        except:
            endImage = False

        # Consigue solo el inicio
        if (beginImage == True) & (endImage == False):
            # Escribir a partir del indice de inicio
            showFrame = False
            noData = False
            with open('img_{:08}.jpg'.format(imIdx), 'ab') as file:
                file.write(input_data[idx0:])


        # Consigue solo el final
        elif (beginImage == False) & (endImage == True):
            # Escribir hasta el indice del final + 2
            with open('img_{:08}.jpg'.format(imIdx), 'ab') as file:
                file.write(input_data[:idx1+2])
                file.close()
            showFrame = True
            imIdx += 1


        # Consigue inicio y final
        elif (beginImage == True) & (endImage == True):
            # Escribir hasta el indice del final, incrementar el indice de la imagen
            noData = False
            with open('img_{:08}.jpg'.format(imIdx), 'ab') as file:
                file.write(input_data[:idx1 + 2])
            showFrame = True
            imIdx += 1
            with open('img_{:08}.jpg'.format(imIdx), 'ab') as file:
                file.write(input_data[idx0:])

        # No consigue ningun indice
        elif (beginImage == False) & (endImage == False):
            showFrame = False

            # Verificar si es informacion basura o es informacion de la imagen
            if noData == False:
                with open('img_{:08}.jpg'.format(imIdx), 'ab') as file:
                    file.write(input_data)
            else:
                continue

receiveData()