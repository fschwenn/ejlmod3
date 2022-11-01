from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3

recs = []

def get_sub_site(url, session_var):
    print('[%s] --> Harvesting data' % url)
    rec = {'tc': 'T', 'autaff': [], 'license': {}, 'keyw': [], 'link': url, 'jnl': 'BOOK'}

    site_resp = session_var.get(url, verify=False)

    if site_resp.status_code != 200:
        print('[%s] --> Error: Can\'t open page')
        return

    ejlmod3.metatagcheck(rec, BeautifulSoup(site_resp.content.decode('utf-8'), 'lxml'),
		['DC.creator', 'DC.date', 'DCTERMS.abstract', 'DC.subject', 'DC.title', 'citation_date', 'DC.language',
			'DC.rights', 'DC.title', 'citation_keywords', 'citation_pdf_url', 'DC.contributor', 'DC.identifier'])

    recs.append(rec)

    print(rec)


publisher = 'Minho U.'
rpp = 20
pages = 2
for page in range(pages):
    print('==== OPEN PAGE %i/%i' % (page+1, pages))
    to_curl = 'https://repositorium.sdum.uminho.pt/handle/1822/3/browse?type=dateissued&sort_by=2&order=DESC&rpp=%s' \
              '&etal=3&null=&offset=%s' % (rpp, rpp*pages)
    with Session() as session:
        resp = session.get(to_curl, verify=False)

        if resp.status_code != 200:
            print("[%s] --> Error: Can't open page!" % to_curl)
            continue
    v = 0
    for link in BeautifulSoup(resp.content.decode('utf-8'), 'lxml').find_all('a'):
        if v == 10:
            break
        if link.get('href') is not None:
            if link.get('href').find('handle') != -1 and len(link.get('href')) <= 20:
                get_sub_site('https://repositorium.sdum.uminho.pt{}'.format(link.get('href')), session)
                sleep(10)
                v+=1
    sleep(10)
    break

jnlfilename = 'THESES-MINHO-%s' % (ejlmod3.stampoftoday())

ejlmod3.writenewXML(recs, publisher, jnlfilename)
