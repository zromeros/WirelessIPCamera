import socket
import cv2
import os

import traceback
import numpy

server_address = "0.0.0.0"
server_port = 4000
PACKAGE = 1500

image_folder = "C:\\Users\\-\\ProyectosESP32\\Repositorio\\WirelessIPCamera\\Wireless_Camera_Server\\sock"
format = 'XVID'

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



def stream(file_stream):
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
            data = data[idxe + 2:]
            idx = idx + 1
    except:
        print("No image")

def receive_array_image():
    # Inilitialize server
    s = create_server_udp(server_address, server_port)

    count_packs = 0
    count_stream = 0
    while True:
        input_data, client_address = s.recvfrom(PACKAGE)
        print(len(input_data))
        file_stream = "stream" + str(count_stream) + ".log"
        f = open(file_stream, "ab")  # Se abre el archivo en modo 'write binarie'
        f.write(input_data)
        f.close()

        if count_packs == 75: #cinco frames
            video_name = 'stream' + str(count_stream) + '.avi'
            fourcc = cv2.VideoWriter_fourcc(*format)
            stream(file_stream)
            count_packs = 0
            count_stream += 1
            images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
            frame = cv2.imread(os.path.join(image_folder, images[0]))
            height, width, layers = frame.shape
            video = cv2.VideoWriter(video_name, fourcc, 5, (width, height))
            for image in images:
                video.write(cv2.imread(os.path.join(image_folder, image)))
            video.release()


        else:
            count_packs += 1
        continue



        #frame, idx, data = index_order(input_data)  # SE SEPARA EL INDICE Y LA DATA POR PAQUETE
        #reception_list.insert(idx, data)  # SE INSERTAN LOS PAQUETES EN LA LISTA AUXILIAR SEGUN EL INDICE QUE SE INDICA
        #print(frame)

        '''
        if len(reception_list) == 256:
            for j in range(len(reception_list)):
                buffer = b''
                aux = reception_list[j]
                #print(j)
                for package in aux:
                    buffer = buffer + package
                    f = open("imagen.jpg", "ab")
                    f.write(buffer)
                    f.close()
            reception_list = []
        continue
        '''

        '''
        if (len(input_data)) == 3:
            if input_data == b'EOT':
                #print(reception_list)
                val = create_image(reception_list, i)
                if val != 0:
                    #print(str(val))
                    continue
                #reception_list = []
                i += 1
                continue
            elif input_data == b'END':
                i = 0
                reception_list = []
                continue
            else:
                idx, data = index_order(input_data)  # SE SEPARA EL INDICE Y LA DATA POR PAQUETE
                reception_list.insert(idx, data)  # SE INSERTAN LOS PAQUETES EN LA LISTA AUXILIAR SEGUN EL INDICE QUE SE INDICA
                continue
        else:
            idx, data = index_order(input_data)  # SE SEPARA EL INDICE Y LA DATA POR PAQUETE
            reception_list.insert(idx, data)  # SE INSERTAN LOS PAQUETES EN LA LISTA AUXILIAR SEGUN EL INDICE QUE SE INDICA
        '''



def receive_image():
    # Inilitialize server
    s = create_server_udp(server_address, server_port)
    print("udp up")
    inicio = True
    reception_list = []

    while True:
        input_data, client_address = s.recvfrom(PACKAGE)
        if inicio:
            print("Receiving from:", client_address[0])
            if input_data[0] == 35 and input_data[1] == 6:
                print("ACK RECEIVED FROM CAMERA")
                continue
            if input_data[0] != 0xFF or input_data[1] != 0xD8:
                continue
            inicio = False

        print(len(input_data))
        if input_data == b'EOT':
            if len(reception_list) != 0:
                buffer = b''
                for pack in reception_list:
                    buffer = buffer + pack

                    f = open("imagen.jpg", "wb")
                    f.write(buffer)
                    f.close()

                img = cv2.imread("imagen.jpg")
                inicio = True  # Para sobreescribir la imagen.
                ##if img is not None:
                ##   cv2.imshow('frame', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            reception_list = []
        else:
            reception_list.append(input_data)
def receive_video():
    # Inilitialize server
    s = create_server_udp(server_address, server_port)
    print("socket up")
    inicio = True
    reception_list = []

    while True:
        input_data, client_address = s.recvfrom(PACKAGE)

        if inicio:
            print("Receiving from:", client_address[0])
            # s.settimeout(5)
            inicio = False
            counter = 2

        print(len(input_data))
        if input_data == b'END':
            if len(reception_list) != 0:
                buffer = b''
                for pack in reception_list:
                    buffer = buffer + pack

                filename = "imagen" + str(counter) + ".jpg"
                f = open(filename, "wb")
                f.write(buffer)
                f.close()
                # array = np.frombuffer(buffer, dtype=np.dtype('uint8'))
                # img = cv2.imdecode(array, 1)
                #
                #
                counter += 1
                #
                # if img is not None:
                #     out.write(img)

            reception_list = []

        else:
            reception_list.append(input_data)
    out.release()
    s.close()
def main():
    receive_array_image()
    # receive_image()
main()

