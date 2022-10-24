# -*- coding: utf-8 -*-
#harvest theses from UNSW
#JH: 2022-10-16

from requests import Session
from time import sleep
from json import loads
from bs4 import BeautifulSoup
import ejlmod3

publisher = 'New South Wales U.'
rpp = 40
pages = 3

boring = ['School of Biological, Earth & Environmental Sciences',
          '470102 Communication technology and digital media studies',
          "School of Aviation", "School of Biomedical Engineering",
          "School of Biotechnology & Biomolecular Sciences", "School of Built Environment",
          "School of Chemical Engineering", "School of Optometry & Vision Science",
          "School of Civil and Environmental Engineering", "School of Clinical Medicine",
          "School of Economics", "School of Medical Sciences", "Climate Change Research Centre",
          "School of Psychology", "School of Women's & Children's Health",
          "3103 Ecology", "3701 Atmospheric sciences", "3707 Hydrology", "400302 Biomaterials",
          "400303 Biomechanical engineering", "Evolution & Ecology Research Centre",
          "401102 Environmentally sustainable engineering", "401602 Composite and hybrid materials",
          "401605 Functional materials", "401606 Glass", "310801 Phycology (incl. marine grasses)",
          "4016 Materials engineering", "420701 Biomechanics", "4003 Biomedical engineering",
          "ARC Centre of Excellence for Climate Extremes", "401607 Metals and alloy materials",
          "Centre for Sustainable Materials Research & Technology", "School of Chemistry",
          "310112 Structural biology (incl. macromolecular modelling)", 
          "401804 Nanoelectronics", "41 ENVIRONMENTAL SCIENCES", "400311 Tissue engineering",
          "Centre for Marine Science and Innovation", "School of Risk & Safety Science"]

jnlfilename = 'THESES-UNSW-%sE' % (ejlmod3.stampoftoday())

recs = []

def normal_get_sub_site(url, sess):
    if not ejlmod3.ckeckinterestingDOI(url):
        return
    print('[%s] --> Harvesting data' % url)
    data_resp = sess.get(url)

    rec = {'tc': 'T', 'jnl': 'BOOK', 'autaff': [], 'supervisor': [],
           'keyw': [], 'license': {}, 'note': [], 'link': url}

    if data_resp.status_code != 200:
        print('[%s] --> Can\'t open this page' % url)
        print('try again after 120s')
        sleep(120)
        data_resp = sess.get(url)
    else:
        sleep(5)


    # Get the rows
    rows = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml').find_all('tr', attrs={'class': 'ng-star-inserted'})

    # Go through rows and harvest data
    for row in rows:
        cols = row.find_all('td')

        descriptor = cols[0].text
        data = cols[1].text

        # Check if it is really a PhD
        if descriptor == 'unsw.thesis.degreetype':
            if data.find('PhD') == -1:
                continue

        # Add supervisor
        elif descriptor == 'dc.contributor.advisor':
            rec['supervisor'].append([data])

        # Add the author
        elif descriptor == 'dc.contributor.author':
            rec['autaff'].append([data])

        # Add the date
        elif descriptor == 'dc.date.issued':
            rec['date'] = data

        # Add Abstract
        elif descriptor == 'dc.description.abstract':
            rec['abs'] = data

        # Add the handle
        elif descriptor == 'dc.identifier.uri':
            handle = data.split('/')
            rec['hdl'] = handle[-2] + '/' + handle[-1]

        # Add license statement
        elif descriptor == 'dc.rights':
            rec['license']['statement'] = data.replace(' ', '-')

        # Add license url
        elif descriptor == 'dc.rights.uri':
            rec['license']['link'] = data

        # Add keywords
        elif descriptor == 'dc.subject.other':
            rec['keyw'].append(data)

        # Add title
        elif descriptor == 'dc.title':
            rec['tit'] = data

        # Get the DOI
        elif descriptor == 'unsw.identifier.doi':
            doi = data.split('/')
            rec['doi'] = '%s/%s/%s' % (doi[-3], doi[-2], doi[-1])

        # Add the notes
        elif descriptor in ['unsw.relation.school', 'unsw.subject.fieldofresearchcode']:
            if data in boring:
                #print('  skip', data)
                ejlmod3.adduninterestingDOI(url)
                return
            else:
                if data in ['510103 Cosmology and extragalactic astronomy',
                            '5101 Astronomical sciences',
                            '510104 Galactic astronomy',
                            '510109 Stellar astronomy and planetary systems']:
                    rec['fc'] = 'a'
                elif data in ['510803 Quantum information, computation and communication',
                              '5108 Quantum physics']:
                    rec['fc'] = 'k'
                elif data in ['4903 Numerical and computational mathematics',
                              '490404 Combinatorics and discrete mathematics (excl. physical combinatorics)',
                              '490406 Lie groups, harmonic and Fourier analysis'
                              '490510 Stochastic analysis and modelling']:
                    rec['fc'] = 'm'
                elif data in ['510404 Electronic and magnetic properties of condensed matter; superconductivity']:
                    rec['fc'] = 'f'
                else:
                    rec['note'].append(data)
            

        

    # Get the pdf file
    pdf_links = BeautifulSoup(data_resp.content.decode('utf-8'), 'lxml').find_all('a')
    for pdf_link in pdf_links:
        if pdf_link.get('href') is None:
            continue
        if pdf_link.get('href').find('bitstreams') != -1 and pdf_link.get('href').find('download') != -1:
            if rec['license'] != {}:
                rec['FFT'] = 'https://unsworks.unsw.edu.au' + pdf_link.get('href')
            else:
                rec['hidden'] = 'https://unsworks.unsw.edu.au' + pdf_link.get('href')

    recs.append(rec)


with Session() as session:
    # Go through the pages
    for page in range(0, pages):
        print('---- PAGE %i of %i ----' % (page+1, pages))
        index_url = 'https://unsworks.unsw.edu.au/server/api/discover/search/objects?savedList=list_37f7cdd3-9221' \
                    '-42cd-91f8-f5552f370c2f&projection=SavedItemLists&sort=dc.date.issued,DESC&page={}' \
                    '&size=40&configuration=publication&f.isAffiliatedOrgUnitOfPublication=bf742dbd-94b8-4d67-9b9a' \
                    '-2ac5ff5afc42,equals&f.resourceType=PhD%20Doctorate,equals&embed=thumbnail'.format(page)

        index_resp = session.get(index_url)

        if index_resp.status_code != 200:
            print('Error: Can\'t open the index page', page)
            continue

        pubs = loads(index_resp.content.decode('utf-8')).get('_embedded').get('searchResult')\
            .get('_embedded').get('objects')

        for pub in pubs:
            normal_get_sub_site('https://unsworks.unsw.edu.au/entities/publication/%s/full'
                                % pub.get('_embedded').get('indexableObject').get('id'), session)
        print('\n  %4i records so far\n' % (len(recs)))
        sleep(2)


ejlmod3.writenewXML(recs, publisher, jnlfilename)

