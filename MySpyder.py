# first, get 'desired text from element'
# second, how much information we want
        # date, title_text, link(/#/news/number), simple_tags
# third, insert into database
# fourth, get information from database
# fifth, process information to add tags(major, What grade at least, etc.)
# sixth, display on website
from selenium import webdriver
import time





from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as E_C
from selenium.webdriver.common.by import By


NTUST_Intern = [] 
def NTUST_Target_Element(driver,target_list):
    intern_elements = driver.find_elements(By.CLASS_NAME,"news_item")
    

    school_text = "NTUST"
    for link in intern_elements: #foreach news item
        #link is now DOM element I think
        try:
            child_tag = link.find_element(By.CLASS_NAME,"pink") # NTUST tags
            child_title = link.find_element(By.CLASS_NAME,"content")
            child_link = link.find_element(By.CLASS_NAME,"clearfix")
            child_date = link.find_element(By.CLASS_NAME,"date")
            #found
            tag_text = "實習" 
            date_text = child_date.get_attribute("innerText")
            title_text = child_title.get_attribute("innerText")
            link_text = child_link.get_attribute("href")

        except:
            try:
                child = link.find_element(By.CLASS_NAME,"yellow")
                child_title = link.find_element(By.CLASS_NAME,"content")            
                child_link = link.find_element(By.CLASS_NAME,"clearfix")
                child_date = link.find_element(By.CLASS_NAME,"date")
                #found
                tag_text ="徵才"
                date_text = child_date.get_attribute("innerText")
                title_text = child_title.get_attribute("innerText")
                link_text = child_link.get_attribute("href")

            except:
                #We don't want
                continue
        #we want it
        target_list.append((date_text,title_text,link_text,tag_text,school_text))

    

def myScrapper_NTUST():
    
    target_url = 'https://career.ntust.edu.tw/#/news'
    
    #open firefox
    driver = webdriver.Firefox()

    #to target url
    driver.get(target_url)
    #wait until element loaded
    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/ul/li[1]/a/div[4]")))


    NTUST_Target_Element(driver,NTUST_Intern) # find element & add into intern list
   
    driver.close()




import requests # to get header
from MyDatabase import *
import datetime
def requstHeaderDataByURL(url):
    response = requests.get(url) # to specific get result
    header_date = response.headers["Date"] # date value will be "Thu, 04 Jan 2024 13:02:12 GMT"
    # however, we need to convert it to "2024-01-04 13:02:12" for database
    header_date = header_date[:len(header_date)-4] # drop GMT value
    #stripe the time to following format
    # %a : day of week abbreviation
    # %d : day of month
    # %b : month abbreviation
    # %Y : year
    # %H : hour
    # %M : minute
    # %S : second
    # then convert to "2024-01-04 13:02:12"
    # %Y-%m-%d %H:%M:%S = 2024-01-04 13:02:12 

    # str parse to time 
    # str format time 
    header_date = datetime.datetime.strptime(header_date, "%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") # convert the format
    


def myScrapperNTUSTGetAllData():
    All_intern = []

    # loop all pages to get all intern info
    # 1. get first page
    # 2. get all elements
    # 3. go to next page if has
    # 4. do until all pages is done => find element is disabled
    target_url = 'https://career.ntust.edu.tw/#/news'

    
    #open firefox
    driver = webdriver.Firefox()

    #to target url
    driver.get(target_url)
    #wait until element loaded
    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/ul/li[1]/a/div[4]")))


    # get value from pages first
    NTUST_Target_Element(driver,All_intern) # find element & add into intern list

    #click to second page
    page_items = driver.find_elements(By.CLASS_NAME,"page-item")
    page_items[2].click()

    keep_click = True
    while keep_click: # loop all pages except first and last pages
        time.sleep(1)
        NTUST_Target_Element(driver,All_intern) # find element & add into intern list
        time.sleep(1)
        page_items = driver.find_elements(By.CLASS_NAME,"page-item")
        page_items[3].click()

        #is end?
        specific_classes = page_items[4].get_attribute("class")
        for in_str in specific_classes.split(" "):
            if in_str == "disabled":
                keep_click = False
    # last page
    time.sleep(1)
    NTUST_Target_Element(driver,All_intern)

    
    


    driver.close()
    All_intern = list(set(All_intern))
    All_intern = sorted(All_intern, key=lambda x: x[0], reverse=True)
    my_database.insertToDatabase(All_intern,bool_executemany=False)

from bs4 import BeautifulSoup
def myScrapperNTUGetAllData():
    All_Intern_hiring_list = []
    target_url = "https://career.ntu.edu.tw/board/index/tab/0/page/"
    num = 1


    school_text = "NTU"
    while True:
        url = target_url + str(num)
        web_response = requests.get(url)
        soup = BeautifulSoup(web_response.text, 'html.parser')
        page_contents = soup.find_all("li",class_="announcement-item")

        if len(page_contents) == 0:
            break

        for content in page_contents:
            intern_or_hiring_text = content.find('a',class_=["tags_custom_2","tags_custom_4"])
            if intern_or_hiring_text != None:
                tags_title = content.find_all('a')

                tag_text = tags_title[0].text
                title_text = tags_title[1].text
                link_text = tags_title[1].get('href')
                title_text = title_text.replace("\n","").replace("\t","").replace("\r","").replace(" ","").replace(u"\u5553","").replace(u"\u7881","").replace(u"\u5cef","")
                date_text = content.find('span').text.replace("\n","").replace("\t","").replace("\r","").replace(" ","")
                All_Intern_hiring_list.append((date_text,title_text,link_text,tag_text,school_text))
        num+=1
    my_database = MyDatabase()
    my_database.insertToDatabase(All_Intern_hiring_list)


def myScrapperNTHUGetAllData():
    All_Intern_hiring_list = []
    # loop all pages to get all intern info
    # 1. get first page
    # 2. get all elements
    # 3. go to next page if has
    # 4. do until all pages is done => find element is disabled
    target_url = 'https://goodjob-nthu.conf.asia/sys_news.aspx?nt=all'

   
    
    #open firefox
    driver = webdriver.Firefox()

    #to target url
    driver.get(target_url)
    #wait until element loaded
    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/form/div[3]/div/div[2]/div/ul")))


    school_text = "NTHU"
    do_again = True
    while do_again:
        do_again = False

        ul_content = driver.find_element(By.XPATH,"/html/body/form/div[3]/div/div[2]/div/ul")
        li_content = ul_content.find_elements(By.TAG_NAME,"li")
        NTHU_WEB_SITE_NUMBER_OF_PAGE = 4

        for li in li_content:

            bool_is_end = False
            try:
                div_label_span_1 = li.find_element(By.CLASS_NAME,"label")
                activity_text = div_label_span_1.get_attribute("innerText")
            except Exception as ex:
                inputs = li.find_elements(By.TAG_NAME,"input")
                if(len(inputs) == NTHU_WEB_SITE_NUMBER_OF_PAGE):
                    bool_is_end = True
                elif len(inputs) != 0:
                    print('-----------')
                    print("the nthu had changed the page size please check")
                    print('-----------')
                else:
                    continue

            if activity_text == "實習" or activity_text == "徵才":
                date_text_day = li.find_element(By.CLASS_NAME,"g-color-primary").get_attribute("innerText")
                date_text_month_year = li.find_elements(By.CLASS_NAME,"d-block")
                date_text_month = date_text_month_year[0].get_attribute("innerText").split("月")[0]
                date_text_year = date_text_month_year[1].get_attribute("innerText")
                if len(date_text_month) == 1:
                    date_text_month = "0" + date_text_month
                date_text = date_text_year + "/" + date_text_month + "/" + date_text_day
                link_text = li.find_element(By.TAG_NAME,"a").get_attribute("href") #get link
                title_text = li.find_element(By.TAG_NAME,"h3").get_attribute("innerText").replace("\n","").replace("\t","").replace("\r","").replace(" ","").replace(u"\u5553","").replace(u"\u7881","").replace(u"\u5cef","") #get title
                title_text = title_text.encode('big5','ignore').decode('big5','ignore')
                tag_text = activity_text
                # print((date_text,title_text,link_text,tag_text,school_text))
                All_Intern_hiring_list.append((date_text,title_text,link_text,tag_text,school_text))
            
            if bool_is_end:
                #next page
                all_inputs = li.find_elements(By.TAG_NAME,"input")
                current_num = 1
                for num in range(len(all_inputs)):
                    try:
                        if all_inputs[num].get_attribute("class") == "pager_on":
                            current_num = num
                            if current_num + 1 <= NTHU_WEB_SITE_NUMBER_OF_PAGE - 2:#remove head and tail
                                all_inputs[num+1].click()
                                do_again = True
                                time.sleep(1)
                    except:
                        continue

                

    All_Intern_hiring_list = list(set(All_Intern_hiring_list))
    All_Intern_hiring_list = sorted(All_Intern_hiring_list,key=lambda x: x[0], reverse=True)
    my_database = MyDatabase()
    my_database.insertToDatabase(All_Intern_hiring_list)
    driver.close()

from math import ceil
from selenium.webdriver.common.action_chains import ActionChains
def myScrapperNCTUGetAllData():
    #request is too slow!!!!! takes at lease 1 sec by website
    All_intern_hiring_list = []



    # loop all pages to get all intern info
    # 1. get first page
    # 2. get all elements
    # 3. go to next page if has
    # 4. do until all pages is done => find element is disabled
    target_url = 'https://osa.nycu.edu.tw/osa/ch/app/data/list?module=nycu0106&id=3604'

   
    
    #open firefox
    driver = webdriver.Firefox()

    #to target url
    driver.get(target_url)
    #wait until element loaded
    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div[2]/div/form/div/div[2]")))

    school_text = "NCTU"
    number_of_page = driver.find_element(By.CLASS_NAME,"text-danger").get_attribute("innerText")
    number_of_page = ceil(int(number_of_page)/15.0)
    now_page = 0
    while now_page < number_of_page:
        ul_content = driver.find_element(By.XPATH,"/html/body/div[2]/div/form/div/div[2]/ul")
        lis = ul_content.find_elements(By.TAG_NAME,"li")
        for li in lis:
            try:
                link_text = li.find_element(By.TAG_NAME,"a").get_attribute("href")
                paragraphs = li.find_elements(By.TAG_NAME,"p")

                date_text = paragraphs[0].get_attribute("innerText")
                date_text = date_text[date_text.find("：")+1:]
                date_texts = date_text.split("-")
                date_text = str(int(date_texts[0])+1911) + "-" +date_texts[1]+"-"+date_texts[2]

                title_text = paragraphs[2].get_attribute("innerText")
                title_text = title_text.replace("\n","").replace("\t","").replace("\r","").replace(" ","").replace(u"\u5553","").replace(u"\u7881","").replace(u"\u5cef","")
                title_text = title_text.encode('big5','ignore').decode('big5','ignore')
                tag_text = "徵才"

                if "實習" in title_text or "intern" in title_text.lower() or "工讀" in title_text:
                    tag_text = "實習"
                All_intern_hiring_list.append((date_text,title_text,link_text,tag_text,school_text))
            except Exception as e:
                continue
        # WebDriverWait(driver,30).until(E_C.element_to_be_clickable((By.XPATH,"/html/body/div[2]/div/form/div/div[3]/div/ul/li[3]"))).click()
            
        element = driver.find_element(By.XPATH ,"/html/body/div[2]/div/form/div/div[3]/div/ul/li[3]")
        driver.execute_script("arguments[0].scrollIntoView(false)", element)
        time.sleep(1)
        element.click()
        # driver.find_element(By.XPATH,"/html/body/div[2]/div/form/div/div[3]/div/ul/li[3]").click()
        time.sleep(1)#sleep at at least 1 sec
        # print(All_intern_hiring_list)   
        now_page = now_page + 1
    All_intern_hiring_list = list(set(All_intern_hiring_list))
    All_intern_hiring_list = sorted(All_intern_hiring_list,key=lambda x: x[0], reverse=True)
    my_database = MyDatabase()
    my_database.insertToDatabase(All_intern_hiring_list,bool_executemany=False)

    driver.close()
        
    
def myScrapperNCKUGetAllData():
    All_intern_hiring_list = []
    current_time = datetime.date.today()#date
    #seriously lack date info
    target_url = "https://grad-osa.ncku.edu.tw/p/403-1054-96-1.php?Lang=zh-tw"
    web_response = requests.get(target_url)
    soup = BeautifulSoup(web_response.text, 'html.parser')
    items = soup.find_all("div",class_ ="listBS")
    school_text = "NCKU"
    last_year = "2024"
    #finish first page
    for item in items:
        inner_text = item.find('a').text
        tag_text = ""
        link_text = item.find('a').get('href')
        date_text = ""

        if inner_text.find("企業徵才") != -1:
            tag_text = "徵才"
        elif inner_text.find("職場體驗") != -1:
            tag_text = "實習"
        else:
            continue # ignore
        
        #date time filler
        if inner_text.find("2023") != -1 or inner_text.find("112") != -1:
            date_text = "2023"
        elif inner_text.find("2024") != -1 or inner_text.find("113") != -1:
            date_text = "2024"
        elif inner_text.find("2025") != -1 or inner_text.find("114") != -1:
            raise ValueError("The system need to modify in ncku")
        else:
            date_text = last_year
        last_year = date_text#update last year
        
        
        if inner_text.find("暑") !=-1: #lack of date info we fill it
            date_text = date_text + "-01-01"
        else:
            date_text = date_text + "-11-01"

        date_type = datetime.datetime.strptime(date_text,"%Y-%m-%d").date()
        if date_type>current_time:
            date_text = datetime.datetime.strftime(current_time,"%Y-%m-%d")

        title_text = inner_text.replace("\n", '').replace("\t", '').replace("\r", '').replace(u"\xa0", "")
        title_text = title_text.encode('big5','ignore').decode('big5','ignore')
        All_intern_hiring_list.append((date_text,title_text,link_text,tag_text,school_text))
    #second pages need to post method
    num = 2
    while True:
        data = {"Rcg":96,"Op":"getpartlist","Page":num}
        web_response = requests.post("https://grad-osa.ncku.edu.tw/app/index.php?Action=mobilercglist",data=data)
        web_response = web_response.json()
        if web_response["stat"] == "over":
            break
        html_content = web_response["content"]
        soup = BeautifulSoup(html_content, 'html.parser')

        items = soup.find_all("div",class_ ="listBS")

        for item in items:
            inner_text = item.find('a').text
            tag_text = ""
            link_text = item.find('a').get('href')
            date_text = ""

            if inner_text.find("企業徵才") != -1:
                tag_text = "徵才"
            elif inner_text.find("職場體驗") != -1:
                tag_text = "實習"
            else:
                continue # ignore
            
            #date time filler
            if inner_text.find("2023") != -1 or inner_text.find("112") != -1:
                date_text = "2023"
            elif inner_text.find("2024") != -1 or inner_text.find("113") != -1:
                date_text = "2024"
            elif inner_text.find("2025") != -1 or inner_text.find("114") != -1:
                raise ValueError("The system need to modify in ncku")
            else:
                date_text = last_year
            last_year = date_text#update last year
            
            
            if inner_text.find("暑") !=-1: #lack of date info we fill it
                date_text = date_text + "-01-01"
            else:
                date_text = date_text + "-11-01"

            date_type = datetime.datetime.strptime(date_text,"%Y-%m-%d").date()
            if date_type>current_time:
                date_text = datetime.datetime.strftime(current_time,"%Y-%m-%d")

            title_text = inner_text.replace("\n", '').replace("\t", '').replace("\r", '').replace(u"\xa0", "")
            title_text = title_text.encode('big5','ignore').decode('big5','ignore')
            All_intern_hiring_list.append((date_text,title_text,link_text,tag_text,school_text))
        num+=1
    All_intern_hiring_list = list(set(All_intern_hiring_list))
    All_intern_hiring_list = sorted(All_intern_hiring_list, key=lambda x: x[0],reverse=True)
    my_database = MyDatabase()
    my_database.insertToDatabase(All_intern_hiring_list)
    # print(All_intern_hiring_list)


import datetime
import time
my_database = MyDatabase()
if __name__ == '__main__':
    
    target_date = datetime.datetime(2024,1,25,18,35,0)

    # myScrapperNTUSTGetAllData()
    # myScrapperNTUGetAllData()
    # myScrapperNTHUGetAllData()
    myScrapperNCTUGetAllData()
    # test_str = "\n\t\t\t\t\n\t\t\t\t【職場體驗】文化部文化資產局1916工坊「112學年第2學期以工換技實習徵選報名簡章」\n\t\t\t"
    # print(test_str.replace("\n", '').replace("\t", '').replace("\r", '').replace(u"\xa0", ""))
    # myScrapperNCKUGetAllData()
    # print("HELLO")
    #do it every day
    #url
    #1. ntust
    #2. ntu
    #3. nthu
    #4. nctu
    #5. ncku

    # while True:
    #     current_time = datetime.datetime.now()
    #     if current_time >= target_date:
    #         target_date = target_date + datetime.timedelta(days=1)
    #     else:
    #         delta_time = target_date - current_time
    #         time.sleep(delta_time.total_seconds())
