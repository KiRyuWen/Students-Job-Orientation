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
# wait until see elements

# scrapper

NTUST_Intern = [] 
def MyScrapper_NTUST():
    driver = webdriver.Firefox()
    
    target_url = 'https://career.ntust.edu.tw/#/news'

    driver.get(target_url)

    WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/ul/li[1]/a/div[4]")))
    intern_elements = driver.find_elements(By.CLASS_NAME,"news_item")

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
                continue
            #We don't want
        NTUST_Intern.append((date_text,title_text,link_text,tag_text))

    driver.close()




