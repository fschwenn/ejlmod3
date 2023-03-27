# -*- coding: utf-8 -*-
# Harvest theses from Barcelona Polytechnic U.
#JH: 2022-23-05
#FS: 2023-03-26



from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import getopt
import sys
import os
import ejlmod3
import re
import undetected_chromedriver as uc


pages = 6
rpp = 50
skipalreadyharvested = True

publisher = 'Barcelona Polytechnic U.'
jnlfilename = 'THESES-BARCELONAPOLYTECH-%s' % (ejlmod3.stampoftoday())


# Initialize Webdriver
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

boring = ["Universitat Politècnica de Catalunya. Departament d'Urbanisme i Ordenació del Territori",
          "Universitat Politècnica de Catalunya. Departament de Projectes Arquitectònics",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria de la Construcció",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria de Projectes i de la Construcció",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Minera, Industrial i TIC",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Química",
          "Universitat Politècnica de Catalunya. Departament d'Òptica i Optometria",
          "Universitat Politècnica de Catalunya. Departament d'Organització d'Empreses",
          "Universitat Politècnica de Catalunya. Departament de Ciència dels Materials i Enginyeria Metal·lúrgica",
          "Universitat Politècnica de Catalunya. Departament de Composició Arquitectònica",
          "Universitat Politècnica de Catalunya. Departament de Projectes d'Enginyeria",
          "Universitat Politècnica de Catalunya. Departament de Resistència de Materials i Estructures a l'Enginyeria",
          "Universitat Politècnica de Catalunya. Departament de Tecnologia de l'Arquitectura",
          "Universitat Politècnica de Catalunya. Departament d'Arquitectura de Computadors",
          "Universitat Politècnica de Catalunya. Departament de Representació Arquitectònica",
          "Escola Tècnica Superior d'Enginyers de Camins, Canals i Ports de Barcelona",
          "Universitat Politècnica de Catalunya. Centre de Cooperació per al Desenvolupament",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Agroalimentària i Biotecnologia",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Civil i Ambiental",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria de Sistemes, Automàtica i Informàtica Industrial",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Elèctrica",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Electrònica",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Mecànica",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Telemàtica",
          "Universitat Politècnica de Catalunya. Departament d'Enginyeria Tèxtil i Paperera",
          "Universitat Politècnica de Catalunya. Departament d'Estadística i Investigació Operativa",
          "Universitat Politècnica de Catalunya. Departament d'Expressió Gràfica a l'Enginyeria",
          "Universitat Politècnica de Catalunya. Departament d'Expressió Gràfica Arquitectònica I",
          "Universitat Politècnica de Catalunya. Departament d'Infraestructura del Transport i del Territori",
          "Universitat Politècnica de Catalunya. Departament de Ciència i Enginyeria Nàutiques",
          "Universitat Politècnica de Catalunya. Departament de Ciències de la Computació",
          "Universitat Politècnica de Catalunya. Departament de Construccions Arquitectòniques I",
          "Universitat Politècnica de Catalunya. Departament de Màquines i Motors Tèrmics",
          "Universitat Politècnica de Catalunya. Departament de Mecànica de Fluids",
          "Universitat Politècnica de Catalunya. Departament de Teoria del Senyal i Comunicacions",
          "Universitat Politècnica de Catalunya. Departament de Teoria i Història de l'Arquitectura i Tècniques de Comunicació",
          "Universitat Politècnica de Catalunya. Institut d'Investigació Tèxtil i Cooperació Industrial de Terrassa",
          "Universitat Politècnica de Catalunya. Institut d'Organització i Control de Sistemes Industrials",
          "Universitat Politècnica de Catalunya. Institut de Tècniques Energètiques",
          "Universitat Politècnica de Catalunya. Institut Universitari de Recerca en Ciència i Tecnologies de la Sostenibilitat"]

def update_record(rec, name, data, non_nested=False):
    if name in list(rec.keys()):
        if non_nested:
            rec[name].append(data)
        else:
            rec[name].append([data])
    else:
        if non_nested:
            rec[name] = [data]
        else:
            rec[name] = [[data]]

    return rec


recs = []
regorcid = re.compile('.*orcid:(\d\d\d\d\-\d\d\d\d\-\d\d\d\d\-\d\d\d.).*')
def get_sub_site(url):
    if not ejlmod3.checkinterestingDOI(url):
        return
    else:
        if skipalreadyharvested and re.sub('.*handle\/', '', url) in alreadyharvested:            
            print('[%s] --> already in backup' % url)
            return
        else:
            print('[%s] --> Harvesting data' % url)
    rec = {'tc': 'T', 'jnl': 'BOOK', 'link' : url, 'note' : []}
    keepit = True


    driver.get(url+'?show=full')
    fullpage = BeautifulSoup(driver.page_source, 'lxml')
    rows = fullpage.find_all('tr', attrs={'class': 'ds-table-row'})
    sleep(4)
    for row in rows:
        columns = row.find_all('td')
        title = columns[0].text
        data = columns[1].text

        # Get the author
        if title == 'dc.contributor.author':
            rec['autaff'] = [[ data, publisher ]]

        # Get the supervisor
        if title == 'dc.contributor':
            rec = update_record(rec, 'supervisor', data)

        # Get the date
        if title == 'dc.date.issued':
            rec['date'] = data

        # Get the handle
        if title == 'dc.identifier.uri':
            rec['hdl'] = re.sub('.*handle.net\/', '', data)

        # Get the abstract in english
        if title == 'dc.description.abstract':
            if data.find('the') != -1:
                rec['abs'] = data

        # Get the pages
        if title == 'dc.format.extent':
            rec['pages'] = data.replace(' p.', '')

        # Get the language
        if title == 'dc.language.iso':
            if data == 'spa':
                rec['language'] = 'Spanish'

        # Get the license link
        if title == 'dc.rights.uri':
            rec['license'] = {
                'url': data
            }
            splitted_url = data.split('/')
            statement = splitted_url[-3] + '-' + splitted_url[-2]
            rec['license']['statement'] = statement.upper()

        # Get the keywords
        if title.find('dc.subject') != -1:
            rec = update_record(rec, 'keyw', data, True)

        # Get the title
        if title == 'dc.title':
            rec['tit'] = data

        #department
        elif title == 'dc.contributor.other':
            if data in boring:
                keepit = False
            else:
                rec['note'].append(data)
                

    # Get the pdf link
    pdf_section = fullpage.find_all('a', attrs={'class': 'image-link'})
    if len(pdf_section) == 1:
        rec['hidden'] = "https://upcommons.upc.edu%s" % pdf_section[0].get('href')
    if keepit:
        if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(url)

    #check for ORCIDs
    sleep(5)
    driver.get(url)
    page = BeautifulSoup(driver.page_source, 'lxml')
    #author
    for div in page.find_all('div', attrs={'class': 'simple-item-view-authors'}):
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('browse.authority', a['href']):
                rec['autaff'] = [[ a.text.strip() ]]
                if regorcid.search(a['href']):
                    rec['autaff'][-1].append(regorcid.sub(r'ORCID:\1', a['href']))
                rec['autaff'][-1].append(publisher)
    #supervisor        
    for div in page.find_all('div', attrs={'class': 'simple-item-view-description'}):
        for span in div.find_all('span'):
            if re.search('Tutor', span.text):
                rec['supervisor'] = []
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('browse.authority', a['href']):
                        rec['supervisor'].append([ a.text.strip() ])
                        if regorcid.search(a['href']):
                            rec['supervisor'][-1].append(regorcid.sub(r'ORCID:\1', a['href']))
                        rec['supervisor'][-1].append(publisher)

                        
for page in range(pages):
    print(('OPENING PAGE %i OF %i' % (page+1, pages)))
    tocurl = 'https://upcommons.upc.edu/discover?rpp=' +str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Doctoral+thesis&sort_by=dc.date.issued_dt&order=desc'
    driver.get(tocurl)
    for article in BeautifulSoup(driver.page_source, 'lxml').find_all('h4', attrs={'class': 'artifact-title'}):
        article_link = article.find_all('a')
        if len(article_link) == 1:
            article_link = article_link[0].get('href')
            get_sub_site('https://upcommons.upc.edu%s' % article_link)
    sleep(10)

#closing of files and printing


ejlmod3.writenewXML(recs, publisher, jnlfilename)
