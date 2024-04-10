from MyDatabase import getRawDataFromDatabase, getHeaderDateFromDatabase, MyDatabase
from MyUtils import sortDataByDate
from MyDepartmentSystem import MyDepartmentSystem


import requests
from html.parser import HTMLParser
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER #ckiptagger
import math
from datetime import datetime,timedelta

from collections import OrderedDict


# wordcloud
import numpy as np
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt


import MyLLMAPI #send http request to ai model

# process html file
class HTMLCleaner(HTMLParser):
    def __init__(self,*args,**kwargs):
        super(HTMLCleaner,self).__init__(*args,**kwargs)
        self.content = []
    def handle_data(self, data: str):
        self.content.append(data)
    def reset(self) -> None:
        super().reset()
        self.content = []


class Analyzer051:
    def __init__(self):
        self.ws = WS("./data")
        self.pos = POS("./data")
        self.ner = NER("./data")
        self.department_system = MyDepartmentSystem()
        self.llmapi = MyLLMAPI.MyLLMAPI('./api-assets/')
    def __del__(self):
        del self.ws
        del self.pos
        del self.ner

    def getWordSentenceList(self,text:str) -> list:
        data_sentence_list = [text]
        # 使用 WS 來對句子列表進行斷詞，並存入 word_sentence_list
        word_sentence_list = self.ws(data_sentence_list)
        return word_sentence_list[0]
    def getPosSentenceList(self,word_sentence_list:list)->list:
        # 使用 POS 來對斷詞後的句子列表進行詞性標註，並存入 pos_sentence_list
        return self.pos(word_sentence_list)
    def getEntitySentenceList(self,word_sentence_list:list, pos_sentence_list:list)->list:
        # 使用 NER 來對斷詞後的句子列表進行命名實體識別，並存入 entity_sentence_list
        return self.ner(word_sentence_list, pos_sentence_list)[0]

    def textToTokenization(self, text:str):
        word_sentence_list = self.getWordSentenceList([text])
        pos_sentence_list = self.getPosSentenceList(word_sentence_list)
        entity_sentence_list = self.getEntitySentenceList(word_sentence_list, pos_sentence_list)

        return word_sentence_list,entity_sentence_list
    def resolveHTML(self, text:str):
        self.html_cleaner.feed(text)
        return self.html_cleaner.content
    def replaceStringWithSpace(self, text:str):
        return text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ').replace(u"\xa0", " ")
    
    def showWordCloud(self, content_dict:OrderedDict) -> None:
        cloud_mask = np.array(Image.open("leaf.png"))
        font_path = "./fonts/msjh.ttc"
        wordcloud = WordCloud(background_color="white", mask=cloud_mask, contour_width=3, contour_color='steelblue', font_path= font_path).generate_from_frequencies(content_dict)
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

    def makeTFIDF(self, word_sentence_list:list, entity_sentence_list:list):
        pass

    def sendStartPrompt(self, prompt_start) -> str:
        return self.llmapi.getAnswer(prompt_start)
    def inferDepartmentsFromContent(self, contents:list,keyword_allow_number = 10) -> list:
        if contents is None or len(contents) == 0:
            raise Exception('contents is empty')
            return []

        departments_list = []
        keywords =  []
        prompt_start = "你接下來一系列的任務都是"

        prompt_departments = "a)推測給予的內容屬於學校哪個科系，可以多個科系同時出現，回答格式只要回答數字即可 學校科系有"

        for i in range(len(self.department_system.getDepartmentLists())):
            prompt_departments += str(i) + ". " + self.department_system.getDepartmentLists()[i] + " "
        

        prompt_keywords = "b)另外回答根據甚麼關鍵字，至多{keyword_allow_number}個關鍵字。只要回答關鍵字內容即可。回答範例為 1.資安, 2.威脅"
        prompt_failed = "c) 如果a,b都無法得出，請回答 Unknown"

        prompt_content_constraint = "內容如下;let\'s think step by step;不要廢話;不必解釋為何是Unknown\n"

        BOOL_SEND_API = True
        if True:

            if BOOL_SEND_API:
                self.llmapi.getAnswer(prompt_start + "\n" + prompt_departments + "\n" + prompt_keywords + "\n" + prompt_failed + "\n",'9c64549d-4f71-45eb-a27e-c1887f040dc2')

            prompt = ""

            if BOOL_SEND_API:
                for content in contents:
                    prompt = prompt_content_constraint + content

                    result = self.llmapi.getAnswer(prompt)
                    if result.find("c)") != -1:
                        departments_list.append('Unknown')
                        keywords.append('Unknown')

                    else:

                        index_b = result.find("b)")
                        result_str_a = (result[:index_b])[2:]
                        result_str_b = (result[index_b:])[2:].split("\n")

                        result_str_b = [x for x in result_str_b if x != ' ' and x != '']

                        departments_list.append(result_str_a)
                        keywords.append(result_str_b)

                    

        return departments_list,keywords

    def getOrgNamesByTitles(self, titles:list):
        result_orgs = []

        for i in range(len(titles)):
            _, entity_list_title = self.textToTokenization(titles[i]) #entity is list of tuple
            org_list = [word for word in entity_list_title if word[2] == 'ORG']
            #only push first one
            if len(org_list) > 0 and org_list[0] not in result_orgs:
                result_orgs.append(org_list[0][3]) #[3] is org name
            elif len(org_list) == 0:
                result_orgs.append('None')

        TitleFixer = MyLLMAPI.MyTitleFixerLLMAPI('./api-assets/')

        # TitleFixer.sendORGStartPrompt()
        result_orgs = TitleFixer.fixListIfNoneTitle(result_orgs,titles)
        print("After fix: ",result_orgs)
        return result_orgs


# 定義一個印出斷詞和詞性標註結果的函數
def print_word_pos_sentence(word_sentence, pos_sentence):
    assert len(word_sentence) == len(pos_sentence)
    for word, pos in zip(word_sentence, pos_sentence):
        print(f"{word}({pos})", end="\u3000")
    print()
    return

# 迴圈印出每個句子的處理結果，包括斷詞、詞性標註以及命名實體識別的結果

def getWordSentenceList(text):
    data_sentence_list = [text]
    # 使用 WS 來對句子列表進行斷詞，並存入 word_sentence_list
    word_sentence_list = ws(data_sentence_list)
    return word_sentence_list[0]

def getPosSentenceList(word_sentence_list):
    # 使用 POS 來對斷詞後的句子列表進行詞性標註，並存入 pos_sentence_list
    pos_sentence_list = pos(word_sentence_list)
    return pos_sentence_list
def getEntitySentenceList(word_sentence_list, pos_sentence_list):
    # 使用 NER 來對斷詞、詞性標註後的句子進行命名實體識別，並存入 entity_sentence_list
    entity_sentence_list = ner(word_sentence_list, pos_sentence_list)
    return entity_sentence_list

#step 1 tokenization
def getTokenization(text):
    data_sentence_list = [text]

    # 使用 WS 來對句子列表進行斷詞，並存入 word_sentence_list
    word_sentence_list = ws(data_sentence_list)

    # 使用 POS 來對斷詞後的句子列表進行詞性標註，並存入 pos_sentence_list
    pos_sentence_list = pos(word_sentence_list)

    # 使用 NER 來對斷詞、詞性標註後的句子進行命名實體識別，並存入 entity_sentence_list
    entity_sentence_list = ner(word_sentence_list, pos_sentence_list)

    entity_sentence_list = sorted(entity_sentence_list[0])



    # for i, sentence in enumerate(data_sentence_list):
    #     print()
    #     print(f"'{sentence}'")
    #     print_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i])
    #     for entity in sorted(entity_sentence_list[i]):
    #         print(entity)

    return word_sentence_list,entity_sentence_list


    



# request then get content data
def requestHeaderDataByURL(url):
    response = requests.get(url) # to specific get result
    return  response


def parseHTMLContent(content):
    html_parser.feed(content)
    return html_parser.content

def getNTUSTUrlContent(url):
    html_parser.reset()
    html_parser.close()

    url = url.replace("#","api")
    json_file = requestHeaderDataByURL(url).json()

    data_content = json_file['data']['content']
    #parse  content
    data_content_parse = parseHTMLContent(data_content)

    #weird data
    for i in range(len(data_content_parse)):
        data_content_parse[i] = data_content_parse[i].replace(u"\xa0"," ").replace("\r","").replace("\n","").replace("\t","")

    result = ''.join(data_content_parse)
    # content.replace(u"\xa0"," ").replace("\r","").replace("\n","").replace("\t","")

    return result


#step 3 TF-IDF preprocess
def push2FrequencyTable(content,target_dict):
    for word in content:
        if target_dict.get(word) == None:
            target_dict[word] = 0
    
        target_dict[word] += 1

def getORGFromContent(content):
    return [word for word in content if word[2] == 'ORG']


def showWordCloud(content_dict:OrderedDict) -> None:

    cloud_mask = np.array(Image.open("leaf.png"))
    font_path = "./fonts/msjh.ttc"

    wordcloud = WordCloud(background_color="white", mask=cloud_mask, contour_width=3, contour_color='steelblue', font_path= font_path).generate_from_frequencies(content_dict)
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

def fixTitle(raw_title):
    pass

 
def getTFIDFByDepartmentAndKeyWord(Analyzer:Analyzer051,ds,ks):

    department_dict_count = {}
    keyword_dict_count = {}

    for department in Analyzer.department_system.department_list:
        department_dict_count[department] = 0
    
    for departments in ds:
        for department in departments:
            dep_str = Analyzer.department_system.department_list[department]
            department_dict_count[dep_str] += 1

    #get all info
    #tf idf
    for keywords in ks:
        for keyword in keywords:
            if keyword_dict_count.get(keyword) == None:
                keyword_dict_count[keyword] = 0
            keyword_dict_count[keyword] += 1
    
    for word in keyword_dict_count.keys():
        keyword_dict_count[word] = keyword_dict_count[word]/len(ks)
    
    for department in department_dict_count.keys():
        department_dict_count[department] = department_dict_count[department]/len(ds)
    
    #make wordcloud
    keyword_OD = OrderedDict(sorted(keyword_dict_count.items(), key=lambda x: x[1], reverse=True))# from big to small
    department_OD = OrderedDict(sorted(department_dict_count.items(), key=lambda x: x[1], reverse=True))# from big to small
    showWordCloud(keyword_OD)
    showWordCloud(department_OD)
    return department_OD,keyword_OD

    


#step 2 get datas url
#step 2.1 request
#step 2.2 get content
#step 2.2.1 parse data
#step 2.3 tokenization
#step 2.4 frequency table
#step 2.5 TF-IDF
TOP_K = 500
TEST_DATA_LEN = 10
def backendDataflow():
    # pass
    # assume spyder get data at midnight and school always updated before midnight at same day.
    # impossible 2/14 update a 2/13 data and 2/13 data etc
    
    # raw_data = sortDataByDate(getRawDataFromDatabase())[0:TEST_DATA_LEN] # get data
    header_date = getHeaderDateFromDatabase()
    last_two_time_database_update = (datetime.today() - timedelta(days=1)).date()
    last_time_database_update = datetime.today().date()

    if len(header_date)>0:
        last_time_database_update = header_date[0][0]
        if len(header_date)>1:
            last_two_time_database_update = header_date[1][0]
            last_two_time_database_update = datetime.strptime(last_two_time_database_update,"%Y-%m-%d").date()
        last_time_database_update = datetime.strptime(last_time_database_update, "%Y-%m-%d").date()
    
    if last_two_time_database_update > last_time_database_update:
        last_two_time_database_update = last_time_database_update

    my_database = MyDatabase()
    new_data = my_database.getDataFromDatabase(database_name="info",rule="date > %s",additional_data=(last_two_time_database_update.strftime("%Y-%m-%d")))
    
    # print(len(new_data))
    
    if new_data == []:
        return
    
    # print(new_data)

    
    newest_date = last_time_database_update.strftime("%Y-%m-%d")
    
    if True:



        #after title analysis
        all_title = [data[1] for data in new_data ] #get all title
        all_url = [data[2] for data in new_data ] #get all url




        # get llm helper
        Analyzer = Analyzer051()

        #fix title
        titles = Analyzer.getOrgNamesByTitles(all_title)
        
        #unique test
        #get data from unique database
        #compare org with date
        actual_new_data_title = []
        actual_new_data_url = []
        a_month_ago = (datetime.strptime(newest_date,"%Y-%m-%d").date() - timedelta(days=30)).strftime("%Y-%m-%d")
        print("processing time:",a_month_ago," after.")
        print("The title count is:",len(titles))
        for title in titles:
            # find the title and check the date a month ago is exist or not
            # if not, add it
            # if exists, don't
            unique_datas = my_database.getDataFromDatabase(database_name="organizations",rule="org = %s AND date > %s",additional_data=(title,a_month_ago)) 
            if len(unique_datas) == 0:
                title_index = titles.index(title)
                actual_new_data_title.append(all_title[title_index])
                actual_new_data_url.append(all_url[title_index])
            # else:
            #     unique_datas = sorted(unique_datas, key=lambda x: x[0], reverse=True)
            #     newest_data = unique_datas[0]
            #     last_date_date = datetime.strptime(newest_data[0],"%Y-%m-%d").date()

            #     if newest_date > last_date_date:
            #         title_index = titles.index(title)
            #         actual_new_data_title.append(all_title[title_index])
            #         actual_new_data_url.append(all_url[title_index])
        



        
        #(date,org,department)
        #depend on (date,org) within 2 month or not
        #to find out data is new
        #ex. yahoo earliest data i s Jan, 2022
        #ex. yahoo is hiring at Feb, 2022 => not new
        #ex. yahoo is hiring at Apr, 2022 => new
        

        # prepare content
        contents = []
        for i in range(len(actual_new_data_title)):     
            content = getNTUSTUrlContent(actual_new_data_url[i])
            contents.append(content)
        #get departments and keywords
        ds,ks = Analyzer.inferDepartmentsFromContent(contents)
        ds_dict, ks_dict = getTFIDFByDepartmentAndKeyWord(Analyzer,ds,ks)
        #save to database

        insert_data = []

        for i in range(len(actual_new_data_title)):
            d_str = ds[i]

            if d_str == 'Unknown':
                d_str = MyDepartmentSystem().department_list[-1]
            else:
                d_all_number = d_str.split(",")
                d_str_list = [MyDepartmentSystem().department_list[int(d_num)] for d_num in d_all_number]
                d_str = ",".join(d_str_list)
            insert_data.append((newest_date,actual_new_data_title[i],d_str))

        #insert to unique database
        my_database.insertToDatabase(insert_data,database=my_database.ORGANIZATION_DATABASE_STR,commit=True,close=True)


    

    





if __name__ == '__main__':
    html_parser = HTMLCleaner()


    backendDataflow()
