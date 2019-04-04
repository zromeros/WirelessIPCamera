import psycopg2
from db.configDB import config

def connect():
    # read connection parameters
    params = config()
    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    return psycopg2.connect(**params)

#no funciona
def save_camera_id(camera_id):
    sql = "INSERT INTO cameras(camera_id) VALUES(%s)"

    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        # create table one by one
        cur.execute(sql, (camera_id,))
        # commit the changes
        conn.commit()
        # close communication with the PostgreSQL database server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def execute_command(command):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        # create table one by one
        cur.execute(command)
        # commit the changes
        conn.commit()
        # close communication with the PostgreSQL database server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    insert_camera_id("5233")

