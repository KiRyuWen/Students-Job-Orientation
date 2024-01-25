from flask import Flask, render_template, request
import MyUtils
import MyDatabase
import json

app = Flask(__name__, static_folder='assets')
#predefined
data_from_database = MyDatabase.getRawDataFromDatabase()
data_from_database = MyUtils.sortDataByDate(data_from_database)

@app.route('/', methods=['GET'])
def index():
    # # get data
    # all_data = MyDatabase.getDataFromDatabase()
    # #args check


    # all_data = MyUtils.sortDataByDate(all_data)



    return render_template("index.html",datas = data_from_database)

@app.route('/data', methods=['GET'])
def getDataRequest():
    # data_list = MyDatabase.getDataFromDatabase()

    ## is search for specific target
    search_target = request.args.get("search")
    if search_target is not None:
        data_specific_target = MyUtils.searchDataByTitle(data_from_database,search_target)
        return json.dumps(data_specific_target)

    ##size
    news_size = request.args.get("news_size")
    if not news_size:
        news_size = 10

    

    all_data_size = len(data_from_database)
    data_list = data_from_database[:min(int(news_size),all_data_size)]


    return json.dumps(data_list)

if __name__ == '__main__':
    app.run(debug=True)