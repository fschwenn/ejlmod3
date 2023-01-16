# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest Rev.Roum.Math.Pures Appl.
# FS 2022-09-26

import os
import ejlmod3
import re
import sys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

publisher = 'Romanian Academy, Publishing House of the Romanian Academy'
vol = sys.argv[1]
iss = sys.argv[2]

jnlfilename = 'rrmpa%s.%s' % (vol, iss)

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

tocurl = 'http://imar.ro/journals/Revue_Mathematique/php/%i/Rrc%s_%s.php' % (1960+int(vol), str(int(vol)-40), re.sub('\-', '_', iss))
print(tocurl)
driver.get(tocurl)
tocpage =  BeautifulSoup(driver.page_source, features="lxml")

recs = []
for center in tocpage.body.find_all('center'):
    for tr in center.find_all('tr'):
        rec = {'jnl' : 'Rev.Roum.Math.Pures Appl.', 'tc' : 'P', 'notes' : ['Vorsicht, kein Abstract!'],
               'vol' : vol, 'issue' : iss}
        rec['year'] = str(1960+int(vol))
        for a in tr.find_all('a'):
            rec['tit'] = a.text.strip()
            rec['FFT'] = a['href']
            rec['p1'] = re.sub('.*\/(.*).pdf', r'\1', a['href'])
        tds = tr.find_all('td')
        authors = re.sub(',? and ', ', ', tds[0].text.strip())
        rec['auts'] = re.split(' *, *', authors)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
driver.quit()
