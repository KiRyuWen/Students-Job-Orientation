
import pymysql


class MyDatabase:
    def __init__(self):
        self.password = None
        self.database_settings = None

        with open("./password.txt") as f:
            self.password = f.read()
        self.database_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": _password,
            "db": "myspyder_info",
            "charset": "big5"
        }
        self.conn_rule = pymysql.converters.conversions.copy()
        self.conn_rule[10] = str
        self.conn_rule[246] = float

        self.info_database_str = "info(date,title,link,tag,school)"
        self.date_time_database_str = "date_time(date)"
        self.organization_database_str = "organization(date,org,departments)"


    def insertToDatabase(self, datas, commit=True, close=True,bool_executemany = True ,database = "info(date,title,link,tag,school)"):
        try:
            conn = pymysql.connect(**self.database_settings)

            with conn.cursor() as cursor:
                sql = "INSERT INTO " + database + " VALUES (%s,%s,%s,%s,%s)"#command

                try:
                    if bool_executemany:
                        cursor.executemany(sql, datas)#insert
                    else:
                        for data in datas:
                            cursor.execute(sql, data)
                    #finish
                    if commit:
                        conn.commit()#save
                except pymysql.err.IntegrityError as dup_key_error:
                    print("\nsame key bros",dup_key_error)
                    print()
                except Exception as ex:
                    print(ex)
                finally:
                    if close:
                        conn.close()
        except Exception as ex:
            print(ex)

# database setting
with open("./password.txt") as f:
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


def getRawDataFromDatabase():
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
