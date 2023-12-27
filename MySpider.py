from selenium import webdriver
import time
driver = webdriver.Firefox()

target_url = 'https://career.ntust.edu.tw/#/news'

driver.get(target_url)



from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as E_C
from selenium.webdriver.common.by import By
# wait until see elements
WebDriverWait(driver,20).until(E_C.visibility_of_element_located((By.XPATH,"/html/body/div/main/div/div[2]/div/div/div[2]/div/div/div[2]/div/ul/li[1]/a/div[4]")))
intern_elements = driver.find_elements(By.CLASS_NAME,"news_item")

NTUST_Intern = []
for link in intern_elements:
    #link is now DOM element I think
    try:
        child = link.find_element(By.CLASS_NAME,"pink") # NTUST tags
        print(child.get_attribute("innerText")) #so use innertText to get information
        NTUST_Intern.append(child)
    except:
        try:
            child = link.find_element(By.CLASS_NAME,"yellow")
            print(child.get_attribute("innerText")) #so use innertText to get information
            NTUST_Intern.append(child)
        except:
            continue
        #We don't want
for e in NTUST_Intern:
    print(e)



driver.close()