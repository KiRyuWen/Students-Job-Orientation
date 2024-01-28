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
    print(All_Intern_hiring_list)
    my_database = MyDatabase()
    my_database.insertToDatabase(All_Intern_hiring_list)
    driver.close()

def myScrapperNCTUGetAllData():
    pass
def myScrapperNCKUGetAllData():
    pass


import datetime
import time
my_database = MyDatabase()
if __name__ == '__main__':
    
    target_date = datetime.datetime(2024,1,25,18,35,0)

    # myScrapperNTUSTGetAllData()
    # myScrapperNTUGetAllData()
    # myScrapperNTHUGetAllData()


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
