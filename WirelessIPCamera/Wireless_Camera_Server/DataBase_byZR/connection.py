import psycopg2
import pprint
import sys

def main():
    ##Variable de conexion
    stringConnect = "host='localhost' dbname='wc_databse' user='postgres' password='alterinfo'"
    print("String connect\n ->", (stringConnect))
    #CREANDO CONEXION CON LA BASE DE DATOS

    obj = psycopg2.connect(stringConnect)
    #Creamos cursor para ejecutar consultas a la BD

    objCursor = obj.cursor()




    # Insertar en la base de datos

    objCursor.execute("INSERT INTO tbtest(num,data) VALUES(%s, %s)", (26, 'Juan Aguirre'))

    # Para guardar de forma permanente
    obj.commit()

    objCursor.execute("SELECT *FROM tbtest;")
    #LEYENDO REGISTROS
    registros = objCursor.fetchall()
    #Imprimir registros

    pprint.pprint(registros)

    # CERRAR FUNCIONES Y CONEXION EXTABLECIDA
    objCursor.close()
    obj.close()

main()