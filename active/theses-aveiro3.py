from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import re
import ejlmod3

recs = []

jnlfilename = 'THESES-AVEIRO-%s' % (ejlmod3.stampoftoday())

def extract_links(content: str, prafix: str):
    soup = BeautifulSoup(content, 'lxml')
    article_links = soup.find_all('a', {'href': re.compile('/handle/\d{0,}/\d{0,}')})
    filtered = filter(lambda article: False if article.parent.get('class') is None
                        else True if 'evenRowOddCol' in article.parent.get('class') or 'oddRowOddCol' in article.parent.get('class')
                        else False, article_links)

    return list(filtered)


def get_sub_site(url, sess):
	print("[{}] --> Harvesting data".format(url))

	resp = sess.get(url)

	if resp.status_code != 200:
		print("[{}] --> Error: Can't open this page! Skipping...".format(url))
		return

	soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')

	rec = {'tc': 'T', 'jnl': 'BOOK'}
	ejlmod3.metatagcheck(rec, soup, ['DC.creator', 'DCTERMS.issued', 'DC.identifier', 'DC.rights', 'DC.subject', 'citation_title', 'citation_pdf_url', 
					'DCTERMS.abstract'])

	recs.append(rec)

publisher = 'Aveiro U.'
pages = 2
rpp = 20
with Session() as session:
	for page in range(pages):
		tocurl = 'https://ria.ua.pt/browse?type=type&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&value=doctoralThesis&offset=' + str(rpp*page)
		print(tocurl)
		index_resp = session.get(tocurl)

		if index_resp.status_code != 200:
			print("[{}] --> Error: Can't open this page! Skipping page...".format(tocurl))
			continue
#		print(ejlmod3.getdspacerecs(BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml'), 'https://ria.ua.pt'))
		for article in extract_links(index_resp.content.decode('utf-8'), 'https://ria.ua.pt'):
			get_sub_site('https://ria.ua.pt' + article.get('href'), session)
			sleep(10)
		sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
