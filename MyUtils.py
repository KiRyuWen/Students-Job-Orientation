
#data formate will be
#[time, title, url, tag]
def sortDataByDate(data):
    return sorted(data, key=lambda x: x[0], reverse=True)

def searchDataByTitle(data, target):
    return [d for d in data if d[1].lower().find(target) != -1]