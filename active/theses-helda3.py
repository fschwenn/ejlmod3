# -*- coding: utf-8 -*-
#harvest theses from HELDA
#FS: 2019-10-25
#FS: 2023-11-30

from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os
#import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

Scheiss JavaScript


publisher = 'Helsinki U.'
jnlfilename = 'THESES-HELSINKI-%s' % (ejlmod3.stampoftoday())
rpp = 40
pages = 3
skipalreadyharvested = True

boring = ['116 Chemical sciences', '116 Kemia', '116 Kemi', '1171 Geosciences',
          '1171 Geotieteet', '1171 Geovetenskaper', '1172 Environmental sciences',
          '1172 Miljövetenskap', '1172 Ympäristötiede',
          '1181 Ecology, evolutionary biology', '1181 Ekologia, evoluutiobiologia',
          '1181 Ekologi, evolutionsbiologi', '1182 Biochemistry, cell and molecular biology',
          '1182 Biokemia, solu- ja molekyylibiologia', '1182 Biokemi, cell- och molekylärbiologi',
          '11832 Microbiology and virology', '11832 Mikrobiologia ja virologia',
          '11832 Mikrobiologi och virologi', '1184 Genetics, developmental biology, physiology',
          '1184 Genetiikka, kehitysbiologia, fysiologia',
          '1184 Genetik, utvecklingsbiologi, fysiologi', '215 Chemical engineering',
          '215 Teknillinen kemia, kemian prosessitekniikka', '215 Teknisk kemi, kemisk processteknik',
          '217 Lääketieteen tekniikka', '217 Medical engineering', '217 Medicinsk teknik',
          '218 Environmental engineering', '218 Miljöteknik', '218 Ympäristötekniikka',
          '219 Environmental biotechnology', '219 Miljöbioteknologi', '219 Ympäristön bioteknologia',
          '3122 Cancersjukdomar', '3122 Cancers', '3122 Syöpätaudit', '313 Dentistry',
          '313 Hammaslääketieteet', '313 Odontologi', '3142 Folkhälsovetenskap, miljö och arbetshälsa',
          '3142 Kansanterveystiede, ympäristö ja työterveys',
          '3142 Public health care science, environmental and occupational health',
          '318 Lääketieteen bioteknologia', '318 Medical biotechnology', '318 Medicinsk bioteknologi',
          '4112 Forestry', '4112 Metsätiede', '4112 Skogsvetenskap', '516 Educational sciences',
          '516 Kasvatustieteet', '516 Pedagogik', '5171 Political Science', '5171 Statslära',
          '5171 Valtio-oppi', '519 Social and economic geography',
          '519 Socialgeografi och ekonomisk geografi', '519 Yhteiskuntamaantiede, talousmaantiede',
          '5200 Muut yhteiskuntatieteet', '5200 Other social sciences',
          '5200 Övriga samhällsvetenskaper']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


#options = uc.ChromeOptions()
#options.binary_location='/usr/bin/chromium'
#chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#driver = uc.Chrome(version_main=chromeversion, options=options)

options = Options()
#options.add_argument("--headless")
options.add_argument("--enable-javascript")
options.add_argument("--incognito")
options.add_argument("--nogpu")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1200,1980")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)


baseurl = 'https://helda.helsinki.fi'
driver.get(baseurl)
time.sleep(10)    

recs = []
for page in range(pages):
    tocurl = 'https://helda.helsinki.fi/collections/b9c99799-fd50-4802-a8dd-f1d833b10794?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, baseurl, [], boring=boring, alreadyharvested=alreadyharvested)
        1/len(prerecs)
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, baseurl, [], boring=boring, alreadyharvested=alreadyharvested)

    #print(tocpage)
    for rec in prerecs:
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)



















#        if note in ['111 Matematiikka', '111 Matematik', '111 Mathematics']:
#            rec['fc'] = 'm'
#        elif note in ['113 Computer and information sciences', '113 Data- och informationsvetenskap',
#                      '113 Tietojenkäsittely- ja informaatiotieteet']:
#            rec['fc'] = 'c'
#        elif note in ['115 Astronomy, Space science', '115 Avaruustieteet ja tähtitiede',
#                      '115 Rymdvetenskap och astronomi']:
#            rec['fc'] = 'a'
#        elif note in ['112 Statistics and probability', '112 Statistik', '112 Tilastotiede']:
#            rec['fc'] = 's'
