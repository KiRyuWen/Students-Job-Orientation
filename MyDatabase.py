
import pymysql


class MyDatabase: #WenYi_SQL80
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

        self.INFO_DATABASE_STR = "info(date,title,link,tag,school)"
        self.DATE_TIME_DATABASE_STR = "date_time(date)"
        self.ORGANIZATION_DATABASE_STR = "organizations(date,org,departments)"

    def insertToDatabase(self, datas, commit=True, close=True,bool_executemany = True ,database = "info(date,title,link,tag,school)"):
        try:
            conn = pymysql.connect(**self.database_settings)

            comma_count = database.count(',')
            values_str = " VALUES ("
            for i in range(comma_count):
                values_str += "%s,"
            values_str+="%s)"

            with conn.cursor() as cursor:
                sql = "INSERT INTO " + database + values_str#command
                try:
                    if bool_executemany:
                        cursor.executemany(sql, datas)#insert
                    else:
                        for data in datas:
                            cursor.execute(sql, data)
                            conn.commit()
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
    def getDataFromDatabase(self,database_name:str,rule = "",additional_data:tuple = ()):
        try:
            conn = pymysql.connect(**self.database_settings,conv = self.conn_rule)

            with conn.cursor() as cursor:
                sql = "SELECT * FROM " + database_name
                if rule != "":
                    sql += " WHERE " + rule
                    cursor.execute(sql,additional_data)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
            conn.close()
            return list(result)
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
            sql = "DELETE FROM "+ database_name
            cursor.execute(sql)
            conn.commit()
        conn.close()
    except Exception as ex:
        print(ex)
def getHeaderDateFromDatabase():
    try:
        conv = pymysql.converters.conversions.copy() 
        conv[246] = float
        conv[10] = str

        conn = pymysql.connect(**db_settings,conv = conv)
        with conn.cursor() as cursor:
            sql = "SELECT * FROM date_time"
            cursor.execute(sql)
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as ex:
        pass
    return None

from MyDepartmentSystem import MyDepartmentSystem
if __name__ == '__main__':
    my_database = MyDatabase()
    # deleteDataFromSpecificDatabase("organizations")
    # my_database
    # my_database.insertToDatabase([
    #     ("2022-01-01","yahoo","資訊工程系,電機工程系"),
    #     ("2022-04-01","yahoo","資訊工程系,電機工程系"),
    #     ("2022-01-01","google","資訊工程系,電機工程系"),
    #     ("2022-01-01","amazon","資訊工程系,電機工程系"),
    #     ("2022-01-01","netflix","資訊工程系,電機工程系"),
    #     ("2022-01-01","meta","資訊工程系,電機工程系")
    # ],database=my_database.ORGANIZATION_DATABASE_STR
    # )
    # newest_date = "2022-03-01"
    # orgs = ["a","b","c","d","e","f"]
    # deps = ["1,2,3","0,1,2","9","4,5,6,7","8","Unknown"]

    # final_result = []
    # for i in range(len(orgs)):
    #     d_str = deps[i]

    #     if d_str == 'Unknown':
    #         d_str = MyDepartmentSystem().department_list[-1]
    #     else:
    #         d_all_number = d_str.split(",")
    #         d_str_list = [MyDepartmentSystem().department_list[int(d_num)] for d_num in d_all_number]
    #         d_str = ",".join(d_str_list)

    #     final_result.append((newest_date,orgs[i],d_str))
    # print(final_result)
        
    # input()
    # my_database.insertToDatabase(final_result,database=my_database.ORGANIZATION_DATABASE_STR,commit=True,close=True)
    
    data_yahoo = my_database.getDataFromDatabase(database_name="organizations",rule = "date > %s",additional_data=("2022-01-01 00:00:00",))
    print(data_yahoo)