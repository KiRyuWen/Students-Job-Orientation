
import pymysql
# database setting
with open("password.txt") as f:
    _password = f.read()

db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": _password,
    "db": "myspyder_info",
    "charset": "big5"
}
def Insert_2_database_from_scrapper(datas):
    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            sql = "INSERT INTO info(date,title,link,tag,school) VALUES (%s,%s,%s,%s,%s)"#command
            try:
                cursor.executemany(sql, datas)#insert
                conn.commit()#save
            except pymysql.err.IntegrityError as dup_key_error:
                print("\nsame key bros",dup_key_error)
                print()
            except Exception as ex:
                print(ex)
            finally:
                conn.close()
    except Exception as ex:
        print(ex)

def Insert_header_date(data):
    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            sql = "INSERT INTO date_time(date) VALUES (%s)"#command
            try:
                cursor.execute(sql, data)#insert
                conn.commit()#save
            except pymysql.err.IntegrityError as dup_key_error:
                raise dup_key_error
            except Exception as ex:
                raise ex
            finally:
                conn.close()
    except Exception as ex:
        raise ex


def Get_data_from_database():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT * FROM info"
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as ex:
        pass
    return None

def Display_data_from_database():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "SELECT * FROM info"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(len(result))
            print(result)
        conn.close()
    except Exception as ex:
        print(ex)

def Drop_all_database():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "DROP TABLE info"
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)

def Delete_data_from_info_database():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "DELETE FROM info"
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)

def Delete_data_date_time_database():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "DELETE FROM date_time"
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
