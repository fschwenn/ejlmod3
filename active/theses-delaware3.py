# -*- coding: utf-8 -*-
#harvest theses from Delaware
#JH: 2019-09-11

from requests import Session
from time import sleep
from bs4 import BeautifulSoup
import ejlmod3

publisher = 'U. Delaware, Newark'
jnlfilename = 'THESES-DELAWARE-%s' % (ejlmod3.stampoftoday())
rpp = 100
pages = 1
boringdeps = ["University of Delaware, School of Education",
              "University of Delaware, Department of Plant and Soil Sciences",
              "University of Delaware, Department of Political Science and International Relations",
              "Universith of Delaware, Department of Kinesiology and Applied Physiology",
              "University of Delaware, Biomechanics and Movement Science Program",
              "University of Delaware, Biomechanics and Movement Science",
              "University of Delaware, Biomedical Engineering Department",
              "University of Delaware. ǂb Program in Biomechanics and Movement Science",
              "University of Delaware, Center for Bioinformatics and Computational Biology",
              "University of Delaware, Department of Animal and Food Sciences",
              "University of Delaware, Department of Applied Physiology",
              "University of Delaware, Department of Art Conservation",
              "University of Delaware, Department of Art History",
              "University of Delaware, Department of Behavioral Health and Nutrition",
              "University of Delaware, Department of Biological Sciences",
              "University of Delaware, Department of Biomedical Engineering",
              "University of Delaware, Department of Chemical &amp; Biomolecular Engineering",
              "University of Delaware, Department of Chemical and Biomolecular Engineering",
              "University of Delaware, Department of Chemistry and Biochemistry",
              "University of Delaware, Department of Civil and Environmental Engineering",
              "University of Delaware. Department of Civil and Environmental Engineering",
              "University of Delaware, Department of Earth Sciences",
              "University of Delaware, Department of Economics",
              "University of Delaware, Department of English",
              "University of Delaware, Department of Entomology and Wildlife Ecology",
              "University of Delaware, Department of Entomology and Wildlife Ecology.",
              "University of Delaware, Department of Geography and Spatial Sciences",
              "University of Delaware, Department of Geography",
              "University of Delaware, Department of Geological Sciences",
              "University of Delaware, Department of History",
              "University of Delaware, Department of Human Development and Family Sciences",
              "University of Delaware, Department of Kinesiology and Applied Physiology",
              "University of Delaware, Department of Kinesiology and Applied Physiology.",
              "University of Delaware, Department of Linguistics and Cognitive Science",
              "University of Delaware, Department of Medical and Molecular Sciences",
              "University of Delaware, Department of Medical Laboratory Sciences",
              "University of Delaware, Department of Psychological and Brain Sciences",
              "University of Delaware, Department of Sociology and Criminal Justice",
              "University of Delaware, Department Sociology and Criminal Justice",
              "University of Delaware, Disaster Science and Management Program",
              "University of Delaware, Energy and Environmental Policy Program",
              "University of Delaware, Institute for Financial Services Analytics",
              "University of Delaware, School of Marine Science and Policy",
              "University of Delaware, School of Nursing",
              "University of Delaware, School of Public Policy and Administration",
              "University of Delaware, Water Science and Policy Program",
              "University of Delaware, Center for Bioinformatics and Computational BiologyUniversity of Delaware, Department of Animal and Food Sciences",
              "University of Delaware, Center for Energy & Environmental Policy",
              "University of Delaware, Center for Energy and Environmental Policy",
              "University of Delaware, Department of Chemical & Biomolecular Engineering",
              "University of Delaware, Department of Chemical and Biochemical Engineering",
              "University of Delaware,Department of Chemical and Biomolecular Engineering",
              "University of Delaware, Department of Chemical Engineering",
              "University of Delaware, Department of Civil & Environmental Engineering",
              "University of Delaware, Department of Department",
              "University of Delaware, Department of Dept. of Political Science and International Relations",
              "University of Delaware, Department of Entomology & Wildlife Ecology",
              "University of Delaware, Department of Geology",
              "University of Delaware, Department of History",
              "University of Delaware, Department of Human Development & Family Studies",
              "University of Delaware, Department of Human Development and Family",
              "University of Delaware, Department of Human Development and Family Studies",
              "University of Delaware, Department of Human Development and Family Studies.",
              "University of Delaware, Department of Kinesiology & Applied Physiology",
              "University of Delaware, Department of Kinesiology and Applied Physiology",
              "University of Delaware, Department of Linguistics & Cognitive Sciences",
              "University of Delaware, Department of Linguistics & Cognitive Science",
              "University of Delaware, Department of Linguistics & Cognitive Science.",
              "University of Delaware, Department of Linguistics and Cognitive Sciences",
              "University of Delaware, Department of Physical Therapy.",
              "University of Delaware, Department of Plant & Soil Sciences",
              "University of Delaware, Department of Political Science & International Relations",
              "University of Delaware, Department of Psychological & Brain Sciences",
              "University of Delaware, Department of Psychology",
              "University of Delaware, Department of School of Marine Science and Policy",
              "University of Delaware, Department of Sociology & Criminal Justice",
              "University of Delaware, Department of Sociology and Criminal Justice.",
              "University of Delaware, Department of Sociology",
              "University of Delaware, Materials Science and Engineering",
              "University of Delaware, School of Marine Science & Policy",
              "University of Delaware, School of Marine Sciences & Policy",
              "University of Delaware, School of Public Policy & Administration"]

recs = []


def get_sub_site(url, sess):
    keepit = True
    if not ejlmod3.ckeckinterestingDOI(url):
        print('                   ', url)
        return
    rec = {'tc': 'T', 'jnl': 'BOOK', 'supervisor': [], 'note' : [], 'link' : url}
    print('Harvesting data -->', url)
    resp = sess.get(url)
    artpage = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')

    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.date', 'DCTERMS.abstract', 'DC.subject', 'DC.title', 'citation_date'])
    rec['autaff'][-1].append(publisher)

    # Get the rest of the data
    for row in artpage.find_all('tr'):
        if len(row.find_all('th')) > 0 and len(row.find_all('td')):
            title = row.find_all('th')[0].text
            data = row.find_all('td')[0].text

            # Get the advisor
            if title == 'Advisor':
                rec['supervisor'].append([data])
            # Department
            elif title == 'Department':
                dep = data.strip()
                if dep == 'University of Delaware, Department of Computer and Information Sciences':
                    rec['fc'] = 'c'
                elif dep in ['University of Delaware, Department of Mathematical Sciences',
                             'University of Delaware, Department of Mathematics']:
                    rec['fc'] = 'm'
                elif dep in boringdeps:
                    keepit = False
                else:
                    rec['note'].append(dep)
        # Get the pdf file
        if row.get('title') is not None:
            if row.get('title').find('.pdf') != -1:
                pdf_link = row.find_all('a')
                if len(pdf_link) == 1:
                    rec['hidden'] = 'https://udspace.udel.edu' + pdf_link[0].get('href')
    if keepit:
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
    sleep(5)
    return


with Session() as session:
    for page in range(pages):
        to_curl = 'https://udspace.udel.edu/handle/19716/12883/browse?rpp=' + str(
            rpp) + '&sort_by=2&type=dateissued&offset=' + str(page * rpp) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[page+1, pages], [to_curl]])
        index_resp = session.get(to_curl)

        if index_resp.status_code != 200:
            print('[ERROR] Can\'t reach the website!')
            continue

        for link_box in BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml').find_all('div', attrs={'class': 'artifact-title'}):
            link = link_box.find_all('a')

            if len(link) != 1:
                continue
            get_sub_site('https://udspace.udel.edu{}?show=full'.format(link[0].get('href')), session)
        print('   %s records so far' % (len(recs)))
        sleep(20)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
