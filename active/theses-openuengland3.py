# -*- coding: utf-8 -*-
#harvest thesis from Open U., England
#JH: 2023-02-26

from requests import Session
from bs4 import BeautifulSoup
from time import sleep
from json import loads
import re
import ejlmod3


publisher = 'Open U., England'
startyear = ejlmod3.year(backwards=2)
endyear = ejlmod3.year(backwards=0)
skipalreadyharvested = True

boring = ['IRCCS', 'AASA', 'HRWL', 'IRCCSICH', 'MRCHI', 'SZAD', 'FIRCCS',
          'MRCMGU', 'OUCRUV', 'IRCCSIRFMN', 'TIGM', 'BAS', 'FCIMHL',
          'ICGEB', 'MORU', 'SIMR', 'TRI', 'TRL']
boring += ['wels', 'wels-hwsc', 'fass-ssgs-devl', 'fass-ssgs', 'fass',
           'fbl-bus-daf', 'fbl-bus-dpo', 'fbl-bus-dsm', 'fbl-bus-plse',
           'fbl-bus', 'fbl-law', 'fbl', 'iet', 'stem-eee', 'stem-enin',
           'stem-kmi', 'stem-lhcs', 'fass-acem-hist', 'fass-acem-encw',
           'fass-psco', 'fass-ssgs-rels', 'wels-hwsc-hsc', 'ass-acem-musi',
           'fass-acem', 'fass-acem-clst', 'wels-lal', 'wels-lal-elal',
           'fass-arth', 'fass-ssgs-geog', 'fass-ssgs-phil', 'fass-ssgs-poli',
           'fass-ssgs-reli', 'fass-ssgs-soci', 'fass-acem-arth',
           'fass-acem-musi', 'fass-ssgs-spcr', 'wels-ecys-educ', 'wels-ecys']

jnlfilename = 'THESES-OPEN-U-ENGLAND-%sB9' % (ejlmod3.stampoftoday())

recs: list = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def get_sub_site(url, sess):
    #print('[%s] --> Harvesting data' % url)
    rec = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}

    data_resp = sess.get(url)

    if data_resp.status_code != 200:
        print("Error: Can't open page (%s)!" % url)
        return

    data = loads(data_resp.content.decode('utf-8'))

    rec['date'] = str(data.get('date'))

    # Get the pdf file and license
    if data.get('documents'):
        for document in data.get('documents'):
            if document.get('version') in ["version_of_record", "redacted_vor"]:
                rec['FFT'] = document.get('uri')
                license = document.get('license')
                #print('  - ', license)
                if license is None:
                    continue
                if not license[:5] == 'cc_by':
                    continue
                final_link = license.split('_')
                end = float(final_link[-1])
                final = ""
                for i in final_link[0:-1]:
                    final += i + "-"

                final = final[0:-1] + '/' + str(end) + "/"

                rec['license'] = {
                    'statement': final.split('/')[0].upper() + '-' + final.split('/')[-2],
                    'url': 'https://creativecommons.org/licenses/' + final
                }

    # Get the keywords
    if data.get('keywords') is not None:
        rec['keyw'] = data.get('keywords').split('; ')

    # Get the doi
    if data.get('doi') is not None:        
        rec['doi'] = data.get('doi')
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('   already in backup')
            return False

    # Get the url
    if data.get('uri') is not None:
        rec['link'] = data.get('uri')

    # Get the author
    rec['autaff'] = []
    if data.get('creators') is not None:
        try:
            for author in data.get('creators'):            
                name = author.get('name')
                rec['autaff'].append(['%s, %s' % (name.get('family'), name.get('given'))])
                rec['autaff'][-1].append(publisher)
        except:
            rec['autaff'] = [[ 'Doe, John' ]] 
    # Get the abstract
    if data.get('abstract') is not None:
        rec['abs'] = data.get('abstract')

    # Get the title
    if data.get('title') is not None:
        rec['tit'] = data.get('title')

    # Get the pages
    if data.get('pages') is not None:
        rec['pages'] = data.get('pages')

    #research centre
    if data.get('asc_research_centre'):
        rc = data.get('asc_research_centre')
        if rc in boring:
            ejlmod3.adduninterestingDOI(url)
            print('   skip %s' % (rc))
            return False
        elif not rc in ['KEMRI']:
            rec['note'].append(rc)
    #faculty/department
    if data.get('faculty_dept'):
        for dep in data.get('faculty_dept'):
            if dep in 'stem-coco':
                rec['fc'] = 'c'
            elif dep in 'stem-mast':
                rec['fc'] = 'm'
            elif dep in boring:
                ejlmod3.adduninterestingDOI(url)
                print('   skip %s' % (dep))
                return False
            elif not dep in ['stem-ps', 'zgen-othe']:
                rec['note'].append(dep)
        
    recs.append(rec)
    return True




# Create the year searching pattern
pattern = "("
for i in range(startyear, endyear + 1):
    pattern += "\({}\)|".format(i)
pattern = pattern[0:-1] + ')'


with Session() as session:
    index_url = "http://oro.open.ac.uk/view/thesis/phd.html"

    index_resp = session.get(index_url)

    links = []
    if index_resp.status_code != 200:
        print("Error: Can't reach the index page!")
        exit(0)

    articles = BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('p', attrs={'class': 'item_citation'})

    for article in articles:
        r = re.search(pattern, article.text, re.MULTILINE)
        if r is None:
            continue

        # Get the link
        link = article.find_all('a', attrs={'href': re.compile('http\:\/\/oro\.open\.ac\.uk\/[0123456789]')})
        if len(link) == 1:
            i_d = link[0].get('href').split('/')[-2]
            links.append("http://oro.open.ac.uk/cgi/export/eprint/{}/JSON/oro-eprint-{}.js".format(i_d, i_d))

    for (i, link) in enumerate(links):
        ejlmod3.printprogress('-', [[i+1, len(links)], [link], [len(recs)]])
        if ejlmod3.checkinterestingDOI(link):
            if get_sub_site(link, session):
                ejlmod3.printrecsummary(recs[-1])
            sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
