import socket
import cv2
import os
import subprocess as subp
import traceback
import numpy

server_address = "0.0.0.0"
server_port = 4000
PACKAGE = 1500

image_folder = "C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock"
path_file="C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock\\package.log"
pathStream ="C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock\\stream1.avi"
pathList ="C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock\\list.txt"
format = 'XVID'
video_name = 'stream.avi'
# out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 5, (320,240))




def create_server_udp(address, port):
    # Initialize Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((address, port))
    return s
def index_input(input_data, tag):
    if tag == 1:                                         #1 para buscar el inicio
        try:
            #print(input_data)
            idx_innit = input_data.index(b'\xff\xd8\xff')    #Se busca el indice de ff d8 en la lista
        except ValueError:
            idx_innit = -1                               #Si no se consigue, se guarda -1
        return idx_innit                                 #Se retorna el valor del indice del inicio o -1 en caso de no conseguirlo
    else:                                                #Cualquier valor >0 exceptuando 1 para buscar el final
        try:
            idx_end = input_data.index(b'\xff\xd9')      #Se busca el indice de ff d9 en la lista
        except ValueError:
            idx_end = -1                                 #Si no se consigue, se guarda -1
        return idx_end                                   #Se retorna el valor del indice del final o -1 en caso de no conseguirlo
def index_order(a):                                                                                #   SE RECIBE LA LISTA
    b = []
    i = a[len(a)-1]                                                                                #   SE GUARDA EL ULTIMO ELEMENTO
    frame = a[len(a)-2]
    b.append(a[0:len(a)-2])                                                                             #   SE ELIMINA EL ULTIMO ELEMENTO DE LA LISTA
    return frame, i, b                                                                                    #   SE RETORNA EL INDICE Y LA DATA DE LA LISTA POR SEPARADO
# create_image: Se recibe la lista ordenada donde se encuentra la imagen y el numero de la imagen recibida
def create_image(list, img_num):
    # Inicializacion en error (-1) de las variable que son indices de la lista
    begin_array = -1    # indice del arreglo donde esta el inicio de la imagen
    end_array = -1      # indice del arreglo donde esta el final de la imagen
    begin_img = -1      # indice del inicio de la imagen
    end_img = -1        # indice del final de la imagen

    # Contadores
    i = 0
    j = 0

    # Rutina para la busqueda de inicio y final de la imagen
    for pack in list:
        # Se  busca el indice del inicio de la imagen en cada uno de los arreglos que conforman la lista
        while begin_img < 0:
            begin_img = index_input(pack, 1)    # Funcion de busqueda
            break

        # Se  busca el indice del final de la imagen en cada uno de los arreglos que conforman la lista
        while end_img < 0:
            end_img = index_input(pack, 2)      # Funcion de busqueda
            break

        # En caso de que el valor de begin_img cambie, quiere decir que el inicio de la imagen fue encontrado
        if begin_img >= 0:
            begin_array = i     # Se guarda el indice del arreglo que contiene el inicio

        # En caso de que begin_img mantenga su valor (-1), se incrementa el contador de busqueda del inicio
        else:
            i += 1

        # En caso de que el valor de begin_img cambie, quiere decir que el final de la imagen fue encontrado
        if end_img >= 0:
            end_array = j       # Se guarda el indice del arreglo que contiene el final

        # En caso de que begin_img mantenga su valor (-1), se incrementa el contador de busqueda del final
        else:
            j += 1

#######################################################################################################################
    # En caso de que se no se consiga el inicio o el final, o no se consiga ninguno, se retorna error (-1)
    if begin_array < 0 | end_array < 0:
        return -1

    # En caso de que se consiga inicio y final, se crea la imagen y se retorna 0 para indicar que fue creada
    else:
 ##     # PRIMERA IMAGEN    ##  ##  ##  ##
        if img_num == 0:
            ## Se escribe el primer arreglo de la imagen
            buffer = b''
            aux = list[begin_array]
            for pack1 in aux:
                buffer = buffer + pack1
                f = open("imagen.jpg", "wb")
                f.write(buffer)
                f.close()

            for count in range(begin_array + 1, end_array):
                aux = list[count]
                for pack3 in aux:
                    buffer = buffer + pack3
                    f = open("imagen.jpg", "wb")
                    f.write(buffer)
                    f.close()
            print("image: ", img_num)

##      # SIGUIENTES IMAGENES   ##  ##  ##  ##
        else:
            buffer = b''
            aux = list[begin_array]
            for pack1 in aux:
                buffer = buffer + pack1
                f = open("imagen" + str(img_num) + ".jpg", "wb")
                f.write(buffer)
                f.close()

            for count in range(begin_array + 1, end_array):
                aux = list[count]
                for pack3 in aux:
                    buffer = buffer + pack3
                    f = open("imagen" + str(img_num) + ".jpg", "wb")
                    f.write(buffer)
                    f.close()
            print("image: ", img_num)

        return 0
def create_img(list,frame):
    buffer = b''
    for pack in list:
        buffer = buffer + pack
        f = open("imagen.jpg", "wb")
        f.write(buffer)
        f.close()
def createArrayImg(file_stream):
    with open(file_stream, 'rb') as file:
        data = file.read()
        print('file size = {}'.format(len(data)))
    try:
        idx0 = data.index(b'\xff\xd8\xff')
        idx1 = data.index(b'\xff\xd9')
        if idx1 < idx0:
            print("Limpiando imagen. idx = {}, {}".format(idx0, idx1))
            data = data[idx0:]

        idx = 0
        while True:
            try:
                idxb = data.index(b'\xff\xd8\xff')
                print("Image {}: idxb = {}".format(idx, idxb))

            except:
                print("End of buffer: 0")
                break

            try:
                idxe = data.index(b'\xff\xd9')
                print("Image {}: idxe = {}".format(idx, idxe))
            except:
                print("End of buffer: 1")
                break

            with open('img_{:08}.jpg'.format(idx), 'wb') as file:
                file.write(data[idxb:idxe + 2])
                #video.write(cv2.imread('img_{:08}.jpg'.format(idx)))
            data = data[idxe + 2:]
            idx = idx + 1
    except:
        print("No image")
def delateImg():
    for fileName in os.listdir(image_folder):
        if fileName.endswith(".jpg"):
            os.remove(fileName)


def receive_array_image():
    # Inilitialize server
    s = create_server_udp(server_address, server_port)
    beginStream = True
    seqContinue = False
    count_packs = 0                             # Contador de paquetes
    while True:

        input_data, client_address = s.recvfrom(PACKAGE)
        print(len(input_data))
        file_stream = "package.log"
        f = open(file_stream, "ab")  # Se abre el archivo en modo 'append binarie'
        f.write(input_data)
        f.close()
        countVideos = 1
        if count_packs == 90:
            createArrayImg(file_stream)             #Se crean imagenes enumeradas
            if beginStream == True:
                ffmpegComand = 'ffmpeg -f image2 -i img_%08d.jpg -r 5 -s 320x240 stream.mp4'
                beginStream = False
            else:
                ffmpegComand = 'ffmpeg -f image2 -i img_%08d.jpg -r 1 -s 320x240 stream{}.avi'.format(countVideos)

                #seqContinue = True

            subp.call(ffmpegComand, shell=True)     ##Ejecuta ffmpeg por la consola
            os.remove(path_file)                    #Se elimina el log
            delateImg()                             # Elimina las imagene# s
            count_packs = 0
            countVideos += 1
            '''
            if seqContinue == True:

                createList = "(echo file 'stream.avi' & echo file 'stream.avi' )>list.txt"
                subp.run(image_folder + '&' + createList, shell=True)
                os.remove(pathStream)
                ffmpegComand2 = "ffmpeg -safe 0 -f concat -i list.txt -c copy stream.avi"
                subp.call(ffmpegComand2, shell=True)
                subp.call('y', shell=True)
                os.remove(pathList)
            count_packs = 0
            '''
        else:
            count_packs += 1
        continue


#comando para crear el video inicial: ffmpeg -framerate 5 -start_number 1 -t 1 -i "f%d.png" -c:v libx264 -pix_fmt yuv420p -r 5 -bf 0 initial.mp4

def main():
    #receive_array_image()
main()

