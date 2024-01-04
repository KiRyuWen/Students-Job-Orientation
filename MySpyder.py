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
def MyScrapper_NTUST():
    
    target_url = 'https://career.ntust.edu.tw/#/news'
    try:
        request_header_date(target_url)
    except Exception as ex:
        print(ex)
        return 
    
    #open firefox
    driver = webdriver.Firefox()

    #to target url
    driver.get(target_url)
    #wait until element loaded
    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/ul/li[1]/a/div[4]")))
    #locate the value
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
        NTUST_Intern.append((date_text,title_text,link_text,tag_text,school_text))
   
    driver.close()




import requests # to get header
from MyDatabase import *
import datetime
def request_header_date(url):
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
    try:
        Insert_header_date(header_date)
    except:
        raise Exception("data is not updated yet")


MyScrapper_NTUST()