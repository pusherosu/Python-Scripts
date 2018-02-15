#imports

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

URL='Public url of the survey'

#functions
def do_survey ( firstname , lastname ):
	Form = driver.find_element_by_name('element name for the form itself') #The form
	ln = driver.find_element_by_name('element name for voter last name') #voter last name element is a text field
	fn = driver.find_element_by_name('element name for voter first name') #voter first name element is a text field
	Country = Select(driver.find_element_by_name('element name for country')) #Country element is a dropdown
	Site = Select(driver.find_element_by_name('element name for site')) #Site element is a dropdown
	Lastname = driver.find_element_by_name('element name for traget last name') #Lastname is a text field
	Firstname = driver.find_element_by_name('element name for target first name') #Firstname is a text field
	Email = driver.find_element_by_name('element name for email address') #Email address is a text field
	
	Lastname.clear()
	Lastname.send_keys(lastname);
	time.sleep(1)
	
	Firstname.clear()
	Firstname.send_keys(firstname);
	time.sleep(1)

	ln.clear()
	ln.send_keys('Capt. Chas');
	time.sleep(1)
	fn.clear()
	fn.send_keys('Rathing');
	time.sleep(1)
	Country.select_by_value('element name for selected country')
	time.sleep(1)
	Site.select_by_value('element name for selected site')
	time.sleep(1)
	Email.clear()
	Email.send_keys('captchasrathing@notarealemail.com');
	time.sleep(1)
	
	Form.submit()
	time.sleep(2)
	driver.execute_script("window.history.go(-1)")

def load_names():
	with open('first.csv') as f:
		firstnames = f.read().splitlines()
	firstnames = [x.strip() for x in firstnames] 

	with open('last.csv') as l:
		lastnames = l.read().splitlines()
	lastnames = [x.strip() for x in lastnames] 
	
if __name__ == '__main__':

	driver = webdriver.Chrome('chromedriver.exe')
	driver.get(URL)
	time.sleep(1) 

	load_names()

	for firstname in firstnames:
		for lastname in lastnames:
			print firstname + lastname
			do_survey ( firstname , lastname )

	driver.quit()
