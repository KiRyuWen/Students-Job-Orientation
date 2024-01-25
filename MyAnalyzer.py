from MyDatabase import getDataFromDatabase
from MyUtils import sortDataByDate
from MyDepartmentSystem import MyDepartmentSystem


import requests
from html.parser import HTMLParser
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER #ckiptagger
import math


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
        self.llmapi = MyLLMAPI.MyLLMAPI('./api-assets/claude-ai-cookie.txt','./api-assets/claude-ai-uuid.txt')
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
                self.llmapi.getAnswer(prompt_start + "\n" + prompt_departments + "\n" + prompt_keywords + "\n" + prompt_failed + "\n")

            prompt = ""
            print("-------------------")
            if BOOL_SEND_API:
                for content in contents:
                    prompt = prompt_content_constraint + content
                    print(prompt)
                    result = self.llmapi.getAnswer(prompt)
                    if result.find("c)") != -1:
                        departments_list.append('Unknown')
                        keywords.append('Unknown')
                        print('unknown')
                    else:
                        print("success")
                        index_b = result.find("b)")
                        result_str_a = (result[:index_b])[2:]
                        result_str_b = (result[index_b:])[2:].split("\n")

                        result_str_b = [x for x in result_str_b if x != ' ' and x != '']

                        print(result_str_a)
                        print(result_str_b)
                    

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

        TitleFixer = MyLLMAPI.MyTitleFixerLLMAPI('./api-assets/claude-ai-cookie.txt','./api-assets/claude-ai-uuid.txt')

        # TitleFixer.sendORGStartPrompt()
        result_orgs = TitleFixer.fixListIfNoneTitle(result_orgs,titles)

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
        if len(word) > 1:
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

 

    


#step 2 get datas url
#step 2.1 request
#step 2.2 get content
#step 2.2.1 parse data
#step 2.3 tokenization
#step 2.4 frequency table
#step 2.5 TF-IDF
TOP_K = 500
TEST_DATA_LEN = 3
def getAllDataOrgName():

    
    raw_data = sortDataByDate(getDataFromDatabase()[:TEST_DATA_LEN])

    all_title = [data[1] for data in raw_data ] #get all title
    all_url = [data[2] for data in raw_data ] #get all url

    tmp_word_dict = {}
    word_dict = {}
    org_url_dict = {}
    org_name_list = []

    Analyzer = Analyzer051()
    # titles = Analyzer.getOrgNamesByTitles(all_title)
    contents = []
    for i in range(len(all_url)):     
        content = getNTUSTUrlContent(all_url[i])
        contents.append(content)

    Analyzer.inferDepartmentsFromContent(contents)

    

    #loop all url
    # for i in range(len(all_url)):
    #     html_parser.close() #reset
    #     html_parser.reset()
    #     content = getUrlContent(all_url[i])
    #     word_list = getWordSentenceList(content)

    #     _, entity_list_title = getTokenization(all_title[i])#analyze title
    #     org_list = getORGFromContent(entity_list_title)
    #     if org_list != [] and org_url_dict.get(org_list[0]) == None:
    #         # org_url_dict[org_list[0]] = ''
    #         org_url_dict[all_url[i]] = org_list[0]
    #         org_name_list.append(org_list[0])
    #     elif org_list == []:
    #         org_url_dict[all_url[i]] = 'None'
    #         org_name_list.append('None')
    #     #org_list
    #     push2FrequencyTable(word_list,tmp_word_dict) #preprocess
    #     print(content)
    
    # #TF-IDF
    # for word, frequency in tmp_word_dict.items():
    #     if frequency < 2:
    #         pass
    #     else:
    #         word_dict[word] = math.log10(1/(len(all_url)/frequency)) #frequency
    # word_dict_sort_top_k = OrderedDict(sorted(word_dict.items(), key=lambda t: t[1], reverse = True)[:TOP_K]) # inverse importance frequency higher the value is less important
    # #print(word_dict_sort_top_k)

    # #word cloud
    # showWordCloud(word_dict_sort_top_k)

    # MyTitleFixer = MyLLMAPI.MyTitleFixerLLMAPI('./api-assets/claude-ai-cookie.txt','./api-assets/claude-ai-uuid.txt')
    # MyTitleFixer.fixListIfNoneTitle(org_name_list,all_title) # fix org name

    # i = 0
    # for url in org_url_dict.keys():
    #     if type(org_name_list[i]) is tuple:
    #         org_name_list[i] = org_name_list[i][3]
        

    #     org_url_dict[url] = org_name_list[i]
    #     i+=1
    
    # i = 0
    # print('---------------------------')
    # for url, org in org_url_dict.items():
    #     print(f"{org}:\t{url}\t{all_title[i]}")
    #     i+=1

    

    





if __name__ == '__main__':
    html_parser = HTMLCleaner()


    getAllDataOrgName()
