
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
def insertToDatabase(datas):
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

def insertToDatabaseByForLoop(datas):
    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            sql = "INSERT INTO info(date,title,link,tag,school) VALUES (%s,%s,%s,%s,%s)"#command
            try:
                for data in datas:
                    try:
                        cursor.execute(sql, data)#insert
                    except pymysql.err.IntegrityError as dup_key_error: # find error 
                        break
                    except Exception as ex:
                        raise ex

                conn.commit()#save
            except pymysql.err.IntegrityError as dup_key_error:
                print("\nsame key bros",dup_key_error)
                print()
            except Exception as ex:
                print(ex)
            finally:
                conn.close()
    except Exception as ex: # connection error?
        print(ex)


def insertHeaderDateToDatabase(data):
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


def getDataFromDatabase():
    try:
        #https://stackoverflow.com/questions/7483363/python-mysqldb-returns-datetime-date-and-decimal
        #god is good saves me. lol
        #the following is came from stackoverflow
        conv = pymysql.converters.conversions.copy() 
        conv[246] = float
        conv[10] = str

        conn = pymysql.connect(**db_settings,conv = conv)
        
        with conn.cursor() as cursor:
            sql = "SELECT * FROM info"
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as ex:
        pass
    return None

def dropAllDataFromInfoDatabase():
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "DROP TABLE info"
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)

def deleteDataFromSpecificDatabase(database_name):
    try:
        conn = pymysql.connect(**db_settings)
        with conn.cursor() as cursor:
            sql = "DELETE FROM " + database_name
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
