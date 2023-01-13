import re
import os
from requests import Session
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3

jnlfilename = 'THESES-ILLINOIS-%s' % (ejlmod3.stampoftoday())
recs = []

skipalreadyharvested = True
pages = 1

boring = ['M.S.', 'M.A.', 'MS', 'MA']

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

def get_sub_site(url, fc, sess, aff):
    if ejlmod3.checkinterestingDOI(url):
        print('[{}] --> Harvesting Data'.format(url))
    else:
        print('[{}]'.format(url))
        return
    rec = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}
    keepit = True

    if fc: rec['fc'] = fc

    sleep(4)
    resp = sess.get(url)

    # Check if site correctly loaded
    if resp.status_code != 200:
        print("Can't reach this page:", url)
        return

    artpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['dc.contributor.advisor', 'dc.description.abstract', 
                                        'dc.identifier.uri', 'dc.rights', 'citation_title', 'citation_author',
                                        'citation_keywords', 'citation_pdf_url', 'citation_public_url',
                                        'thesis.degree.name', 'citation_publication_date'])
    if 'thesis.degree.name' in rec:
        for degree in rec['thesis.degree.name']:
            if degree in boring:
                keepit = False
                print('\n~~~ skip %s ~~~\n' % (degree))
            elif not degree in ['PhD', 'PHD', 'Ph.D.']:
                rec['note'].append(degree)
    # Add the aff
    if not 'autaff' in rec or not rec['autaff']:
        for h4 in artpage.find_all('h4', attrs = {'class' : 'creators'}):
            rec['autaff'] = [[ re.sub('"', '', h4.text.strip()) ]]
    for author in range(0,len(rec['autaff'])):
        rec['autaff'][author].append(aff)
    # Title
    if not 'tit' in rec:
        for title in artpage.find_all('title'):
            rec['tit'] = re.sub('\|.*', '', title.text)

#    rec['hidden'] = rec['pdf_url']
#    rec.pop('pdf_url')
    rec['link'] = url
    if rec['hdl'] in alreadyharvested:
        print('   %s already in backup' % (rec['hdl']))
        if not keepit:
            ejlmod3.adduninterestingDOI(url)            
    elif keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(url)


publisher = 'Illinois U., Urbana (main)'
departments = [('Dept.+of+Physics', 'Illinois U., Urbana', ''),
               ('Dept.+of+Computer+Science', 'Illinois U., Urbana (main)', 'c'),
               ('Dept.+of+Mathematics', 'Illinois U., Urbana, Math. Dept.', 'm'),
               ('Dept.+of+Astronomy', 'Illinois U., Urbana, Astron. Dept.', 'a')]
rpp = 25

with Session() as session:
    for (dep, aff, fc) in departments:
        for page in range(pages):
            tocurl = 'https://www.ideals.illinois.edu/items?direction=desc&fq%5B%5D=k_unit_titles%3A' + dep + '&fq%5B%5D=k_unit_titles%3AGraduate+Dissertations+and+Theses+at+Illinois&fq%5B%5D=metadata_dc_type.keyword%3AThesis&q=&sort=metadata_dc_date_issued.sort&start=' + str(rpp*page)
            tocurl = 'https://www.ideals.illinois.edu/items?direction=desc&fq%5B%5D=k_unit_titles%3AGraduate+Dissertations+and+Theses+at+Illinois&sort=d_element_dc_date_issued&fq%5B%5D=k_unit_titles%3A' + dep + '&start=' + str(rpp*page)
            ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
            index_resp = session.get(tocurl)

            if index_resp.status_code != 200:
                print("Can't reach this page:", tocurl)
                continue

            link_box = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('div', attrs={'class': 'media-body'})
            #tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
            #print(tocpage.text)
            #link_box = tocpage.find_all('div', attrs={'class': 'media-body'})
            for box in link_box:
                link = box.find_all('a')
                if len(link) == 1:
                    get_sub_site("https://www.ideals.illinois.edu" + link[0].get('href'), fc, session, aff)
            sleep(4)
        sleep(4)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
