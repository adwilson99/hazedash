#####################################
# fix for bad path, when current dir not included in python path.
import sys
sys.path.append(".")
########### END FIX ################

import requests
import re
import time
import csv

import smtplib
from email.mime.text import MIMEText

#from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Setup virtual display
#display = Display(visible=0, size=(800, 600))
#display.start()

# Constants:
aqiURL="https://apims.doe.gov.my/api_table.html"
pjxpath =  '/html/body/div/section/div[3]/div/div/div[2]/div[2]/table/tbody/tr[19]/td[26]/div'
htmlhead = """
<HTML>
	<BODY>
"""
htmlfoot = """
	</BODY>
</HTML>
"""


options = Options()
options.headless = True
options.binary_location = r'/usr/bin/geckodriver'
print("Starting driver")
driver = webdriver.Firefox(options=options)

print("Driver started, sleeping for 3 seconds")

time.sleep(3)

print("accessing URL")
driver.get(aqiURL)
airIndex = driver.find_element(By.XPATH,pjxpath)
msg="<h3>The Air Quality Index in Petaling Jaya is: " + airIndex.text + "</h3>"

print("found air quality")
print("message")

#convert to integer
number = re.findall(r'\d+', airIndex.text)

if number:
	airIndexNum = int(''.join(number))
else:
	airIndexNum = 0
if (airIndexNum != "N/A") or (airIndexNum !=0) :
	if airIndexNum > 300:
		msg = msg + '''<p><span style="background-color:#ff6363"><b>AIR IS HAZARDOUS!!!</b> RUN FOR THE HILLS!!!</p>'''
	elif airIndexNum > 200:
		msg = msg + '''<p>AIR Polution index is <span style="background-color:#ffcbb5"><b>VERY UNHEALTHY</b></span>,  Stay indoors</p>'''
	elif airIndexNum > 100:
		msg = msg + '''<p>AIR Polution index is <span style="background-color:#ffdda3"><b>UNHEALTHY</b></span>, try to limit outdoor exposure</p>'''
	elif airIndexNum > 50:
		msg = msg + '''<p>It's a little hazey, but the air polution is <span style="background-color:#007BFF"><b>MODERATE</b></span> and poses little risk</p>'''
	elif airIndexNum <=50:
		msg = msg + '''<p><b>ENJOY THE FRESH AIR!!!</b> There is very little polution in the air today and the quality is <span style="background-color:#83D983"><b>GOOD!</b></p>'''
else:
	msg = "Unable to get reading"

driver.close()
#display.stop()

timestamp = time.ctime(time.time())


msg = msg + "<p>Data taken at: " + str(timestamp) + "</p>"
msg = msg + "<p>from: " + aqiURL + "</p>"
print(msg)

csvmsg = msg
print("Data taken at: " + str(timestamp))
print("from: ", aqiURL)

print ("Created messsage")
hours = str(timestamp)[-13:]

mail_subject = "Air Quality in PJ as of: " + str(timestamp) + " is " + str(airIndexNum)
mail_from = "adwilson99@gmail.com"
mail_to = 'alan.wilson@celcomdigi.com'
mail_body = msg
username = "adwilson99"
password = "xmtyxlbbthfxxjoj" 

msg = MIMEText(mail_body, 'html')
msg['Subject'] = mail_subject
msg['From'] = mail_from
msg['To'] = mail_to

data_to_append = [
        [airIndexNum,hours[:2],str(timestamp)[:10],csvmsg]
]

with open('/home/adwilson99/scripts/haze/haze.csv', 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    for row in data_to_append:
        csv_writer.writerow(row)

print("sending message")
#connection.send_message(mimemsg)
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
	smtp_server.login(username, password)
	smtp_server.sendmail(mail_from, mail_to, msg.as_string())

