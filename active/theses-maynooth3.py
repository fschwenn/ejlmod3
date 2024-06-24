# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest Maynooth University
# JH 2022-11-09

from requests import Session
from json import loads
from time import sleep
from datetime import date
import ejlmod3
import re

publisher = 'NUIM, Maynooth'
years = 2
jnlfilename = 'THESES-maynoothuniversity-%s' % (ejlmod3.stampoftoday())

recs = []

def get_sub_site(url, site_session, years, fc):
    site_resp = site_session.get(url)
    print('Harvesting data -->', url)
    if site_resp.status_code != 200:
        return

    rec = {'tc': 'T', 'jnl': 'BOOK'}
    if fc: rec['fc'] = fc
    data = loads(site_resp.content.decode('utf-8'))

    # Get the authors
    rec['autaff'] = []
    for i in data.get('creators'):
        rec['autaff'].append(['{}, {}'.format(i.get('name').get('family'), i.get('name').get('given')), publisher])

    # Get the keywords
    if data.get('keywords'):
        rec['keyw'] = re.sub('[\n\t\r]', ' ', data.get('keywords')).split('; ')

    # Get the date
    rec['date'] = data.get('datestamp').split(' ')[0]
    current_year = date.today().strftime('%Y')
    valid_years = []
    for year in range(0,years+1):
        valid_years.append(str(int(current_year)-year))
    if rec['date'].split('-')[0] not in valid_years:
        print('Thesis is too old --> Skip')
        return

    # Get the abstract
    try:
        rec['abs'] = re.sub('[\n\t\r]', ' ', data.get('abstract'))
    except:
        print('   no abstract?!')

    # Get the title
    rec['tit'] = re.sub('[\n\t\r]', ' ', data.get('title'))

    # Get the url
    rec['link'] = data.get('uri')

    # Get the pdf link
    rec['hidden'] = data.get('documents')[0].get('uri')

    recs.append(rec)


with Session() as session:
    for (fc, inst) in [('c', 'com'), ('', 'exp'), ('m', 'mtph'), ('m', 'mtst'), ('', 'thphy')]:
        to_curl = 'https://mural.maynoothuniversity.ie/cgi/exportview/divisions/dept=5F' + inst + '/JSON/dept=5F' + inst + '.js'

        index_resp = session.get(to_curl)

        if index_resp.status_code != 200:
            print('Error {}: Can\'t connect to the Server!')
            exit(0)

        articles = loads(index_resp.content.decode('utf-8'))
        for article in articles:
            eprintid = article.get('eprintid')
            new_link = 'https://mural.maynoothuniversity.ie/cgi/export/eprint/{}/JSON/nuimeprn-eprint-{}.js'\
                .format(eprintid, eprintid)

            if article.get('thesis_type') is None or article.get('thesis_type') != 'phd':
                continue

            get_sub_site(new_link, session, years, fc)
            sleep(10)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
