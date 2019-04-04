import socket
import cv2
import traceback
import threading

server_address = "0.0.0.0"
server_port = 4000
PACKAGE = 1901


#out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 5, (320,240))

def create_server_udp(address, port):
    # Initialize Socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((address, port))
    return s

def index_input(input_data,tag):

    if tag == 1:
        try:
            idx_innit = input_data.index(b'\xff\xd8')
            print("inicio imagen")
        except ValueError:
            print("No se consigue el inicio")
            idx_innit = -1
        return idx_innit
    else:
        try:
            idx_end = input_data.index(b'\xff\xd9')
            print("finaliza imagen")
        except ValueError:
            print("No se consigue el final")
            idx_end = -1
        return idx_end


def receive_array_image():
    # Inilitialize server
    s = create_server_udp(server_address, server_port)
    print("udp up")
    inicio = True
    reception_list = []
    count = 1

    while True:
        input_data, client_address = s.recvfrom(PACKAGE)
        #print(input_data[1900])
        print(len(input_data))

        f = open("imagen" + str(count) + ".jpg", "ab")  # Se abre el archivo en modo 'write binarie'
        f.write(input_data)
        f.close()
        continue

        '''
        if len(input_data) == 4:
            print("UDP Reset")
            count = 1
            inicio =  True
            reception_list.clear()
            continue

        if inicio:
            #print("Receiving from:", client_address[0])
            idx_init = index_input(input_data, 1)                       #Se busca el inicio
            if idx_init < 0:                                            #Si no se encuentra el inicio
                continue
            else:                                                       #Si se encuentra el inicio
                inicio = False                                          #Se sale del bucle 'inicio'
                reception_list.append(input_data[idx_init:])            #Se agrega a la lista desde el inicio hasta el final del paquete
        else:
            idx_end = index_input(input_data, 2)                        #Se busca el final
            if idx_end < 0:                                             #No se encuentra el final
                reception_list.append(input_data)                       #Se agrega el paquete a la lista
            else:                                                       #Se encuentra el final
                reception_list.append(input_data[0: idx_end + 2])       #Se agregan los datos del paqueta hasta el final de la imagen
                if len(reception_list) != 0:                            #Se verifica que la lista no este vacía
                    buffer = b''                                        #Para escribir en un archivo binario
                    for pack in reception_list:                         #Se escriben los paquetes en el archivo
                        buffer = buffer + pack
                        f = open("imagen" + str(count) + ".jpg", "wb")  #Se abre el archivo en modo 'write binarie'
                        f.write(buffer)
                        f.write(pack)
                        f.close()                                       #Se cierra el archivo
                    count += 1                                          #Se incrementa el contador
                    inicio = True                                       #Se reinicia el proceso de busqueda para la siguiente foto
                break
        reception_list = []                                     #Se vacía la lista para comenzar el proceso de nuevo


        '''
        '''   
            if input_data[0] == b'END':                     ##Se recibe 'END' desde el ESP32
                print("Reset socket UDP")
                reception_list.clear
                counter = 1
                inicio = True
                continue
            if input_data[0] == 35 and input_data[1] == 6:
                print("ACK RECEIVED FROM CAMERA")
                continue

            if input_data[0] != 0xFF or input_data[1] != 0xD8:
                continue
            

            print("Init Frame number: " + str(counter))
            inicio = False

        if input_data == b'EOT':

            if len(reception_list) != 0:
                buffer = b''
                ##print(reception_list)
                
                for pack in reception_list:
                    try:
                        idx = pack.index(b'\xff\xd9')
                    except ValueError:
                        idx = -1
                    if(idx < 0):
                        print("hola")
                        buffer = buffer + pack
                    else:
                        print("chao")
                        print(pack)
                        print(pack[0:idx+2])
                        buffer = buffer + pack[0:idx+2]                 ##Se escribe solo hasta FF D9 en la imagen
                    f = open("imagen"+str(counter)+".jpg", "wb")
                    f.write(buffer)                                     ##Se sobreescribe el archivo
                    f.close()                                           ##Se cierra el archivo
                print(len(buffer))
                img = cv2.imread("imagen"+str(counter)+".jpg")
                counter += 1
                inicio = True
                print("End Frame Number: " + str(counter-1))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            reception_list = []
        else:
            reception_list.append(input_data)
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
                inicio = True # Para sobreescribir la imagen.
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
            #s.settimeout(5)
            inicio = False
            counter = 2

        print(len(input_data))
        if input_data == b'END':
            if len(reception_list) != 0:
                buffer = b''
                for pack in reception_list:
                    buffer = buffer + pack

                filename = "imagen"+str(counter)+".jpg"
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
   #receive_image()
main()