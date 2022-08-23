import re
import os
from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3

jnlfilename = 'THESES-ILLINOIS-%s' % (ejlmod3.stampoftoday())
recs = []

def get_sub_site(url, fc, sess, aff):
    print('[{}] --> Harvesting Data'.format(url))
    rec = {'tc': 'T', 'jnl': 'BOOK'}

    if fc: rec['fc'] = fc

    resp = sess.get(url)

    # Check if site correctly loaded
    if resp.status_code != 200:
        print("Can't reach this page:", url)
        return

    artpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['dc.contributor.advisor', 'dc.description.abstract', 'dc.date.submitted', 'dc.identifier.uri', 'dc.rights', 'citation_title', 'citation_author', 'citation_keywords', 'citation_pdf_url', 'citation_public_url'])

    # Add the aff
    if not 'autaff' in rec or not rec['autaff']:
        for h4 in artpage.find_all('h4', attrs = {'class' : 'creators'}):
            rec['autaff'] = [[ re.sub('"', '', h4.text.strip()) ]]
    for author in range(0,len(rec['autaff'])):
        rec['autaff'][author].append(aff)
    # Title
    if not 'tit' in rec:
        for title in artpage.find_all('title'}:
            rec['tit'] = re.sub('\|.*', '', title.text)

#    rec['hidden'] = rec['pdf_url']
#    rec.pop('pdf_url')
    rec['link'] = url

    recs.append(rec)
    ejlmod3.printrecsummary(rec)


publisher = 'Illinois U., Urbana (main)'
departments = [('Dept.+of+Physics', 'Illinois U., Urbana', ''),
               ('Dept.+of+Computer+Science', 'Illinois U., Urbana (main)', 'c'),
               ('Dept.+of+Mathematics', 'Illinois U., Urbana, Math. Dept.', 'm'),
               ('Dept.+of+Astronomy', 'Illinois U., Urbana, Astron. Dept.', 'a')]
pages = 1
rpp = 25

with Session() as session:
    for (dep, aff, fc) in departments:
        for page in range(pages):
            tocurl = 'https://www.ideals.illinois.edu/items?direction=desc&fq%5B%5D=k_unit_titles%3A' + dep + '&fq%5B%5D=k_unit_titles%3AGraduate+Dissertations+and+Theses+at+Illinois&fq%5B%5D=metadata_dc_type.keyword%3AThesis&q=&sort=metadata_dc_date_issued.sort&start=' + str(rpp*page)
            index_resp = session.get(tocurl)

            if index_resp.status_code != 200:
                print("Can't reach this page:", tocurl)
                continue

            link_box = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('div', attrs={'class': 'media-body'})
            for box in link_box:
                link = box.find_all('a')
                if len(link) == 1:
                    get_sub_site("https://www.ideals.illinois.edu" + link[0].get('href'), fc, session, aff)
                sleep(4)
            sleep(4)
        sleep(4)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
