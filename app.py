from flask import Flask, render_template
import MyDatabase

app = Flask(__name__, static_folder='/assets')
@app.route('/')
def index():
    all_data = MyDatabase.Get_data_from_database()
    return render_template("index.html",datas = all_data)


if __name__ == '__main__':
    app.run(debug=True)