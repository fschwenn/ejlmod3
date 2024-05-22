# -*- coding: utf-8 -*-
#harvest theses from Brussels
#JH: 2021-12-20
#FS: 2023-03-22

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
import re
import unicodedata
import ejlmod3
import os
import undetected_chromedriver as uc


publisher = 'U. Brussels'
jnlfilename = 'THESES-BRUSSELS-%s' % (ejlmod3.stampoftoday())

pages = 6
skipalreadyharvested = True
boring = ["Doctorat en Criminologie", "Doctorat en Histoire, histoire de l'art et archéologie",
          "Doctorat en Philosophie", "Doctorat en Sciences biomédicales et pharmaceutiques (Médecine)",
          "Doctorat en Sciences biomédicales et pharmaceutiques (Pharmacie)", "Doctorat en Sciences juridiques",
          "Doctorat en Sciences politiques et sociales", "Doctorat en Sciences psychologiques et de l'éducation",
          "Doctorat en Art et Sciences de l'Art", "Doctorat en Histoire, art et archéologie",
          "Doctorat en Sciences de la motricité", "Doctorat en Sciences de la santé Publique",
          "Doctorat en Art de bâtir et urbanisme (Polytechnique)",
          "Doctorat en Langues, lettres et traductologie", "Doctorat en Sciences des religions",
          "Doctorat en Sciences agronomiques et ingénierie biologique", "Doctorat en Sciences médicales (Médecine)",
          "Doctorat en Santé Publique", "Doctorat en Sciences économiques et de gestion",
          "Doctorat en Sciences de l'ingénieur et technologie", "Option Biologie des organismes du Doctorat en Sciences",
          "Option Biologie moléculaire du Doctorat en Sciences", "Option Géographie du Doctorat en Sciences",
          "Doctorat en Sciences médicales (Santé Publique)",
          "Option Gestion de l’environnement et d’aménagement du territoire du Doctorat en Sciences",
          "Doctorat en Arts du spectacle et technique de diffusion et de communication",
          "Doctorat en Langues et lettres", "Doctorat en Information et communication",
          "Doctorat en Art de bâtir et urbanisme (Architecture)", "Doctorat en droit",
          "Doctorat en environnement, Orientation gestion de l'environnement",
          "Doctorat en philosophie et lettres, Orientation histoire de l'art et archéologie",
          "Doctorat en philosophie et lettres, Orientation linguistique",
          "Doctorat en sciences agronomiques et ingénierie biologique",
          "Doctorat en sciences économiques, Orientation économie",
          "Doctorat en sciences, Orientation statistique", "Doctorat en sciences pharmaceutiques",
          "Doctorat en sciences politiques", "Doctorat en sciences psychologiques",
          "Doctorat en sciences sociales, Orientation sociologie",
          "Doctorat en sciences, Spécialisation chimie", "Doctorat en sciences, Spécialisation géologie",
          "Doctorat en Sciences dentaires", "Doctorat en sciences médicales",
          "Doctorat en Art de bâtir et urbanisme", "Doctorat en Sciences de la santé publique",
          "Doctorat en Sciences Psychologiques et de l'éducation", "Doctorat en Sciences médicales",
          "Doctorat en Sciences biomédicales et pharmaceutiques", "Doctorat en Sciences de l'ingénieur",
          "Doctorat en sciences sociales, Orientation sciences du travail",
          "Doctorat en philosophie et lettres, Orientation langue et littérature",
          "Doctorat en philosophie et lettres, Orientation histoire"]
boring += ["Sciences sociales", "Télédétection", "Chimie des surfaces et des interfaces",
           "Géologie", "Ecologie", "Géochimie", "Océanographie physique et chimique", "Chimie",
           "Biochimie", "Biologie cellulaire", "Urbanisme et architecture (aspect sociologique)",
           "Informatique mathématique", "Chimie organique", "Biologie", "Biologie moléculaire",
           "Glaciologie", "Géographie urbaine", "Géographie humaine", "Chimie analytique",
           "Biologie théorique", "Immunologie", "Cancérologie", "Architecture et art urbain",
           "Santé publique", "Psychologie", "Sciences de l'ingénieur", "Sciences pharmaceutiques",
           "Disciplines biomédicales diverses", "Médecine pathologie humaine", "Langues et littératures",
           "Sociologie du travail et de la technique", "Urbanisme et architecture [génie civil]",
           "Sciences humaines", "Agronomie générale", "Géographie physique", "Aménagement du territoire",
           'Sciences bio-médicales et agricoles', 'Chimie des polymères de synthèse',
           'Chimie macromoléculaire']

recs = []

# Initialize driver
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)



if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def convert_string(string):
    string_list = list(string)

    for i in range(0,len(string_list)):
        try:
            string_list[i] = str(unicodedata.digit(string_list[i])).encode('utf-8')
        except ValueError:
            pass

    out = ""
    for j in string_list:
        out += j

    return out



def get_sub_side(url):
    keepit = True

    rec = {'keyw' : []}

    rec['supervisor'] = []
    rec['note'] = []
    rec['tc'] = 'T'
    rec['jnl'] = 'BOOK'
    rec['link'] = url

    # Set the fake doi
    rec['doi'] = "20.2000/brussels/" + re.sub('\W', '', url)
    print(" ["+url+"] --> Harvesting data")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # Get the main information table
    record_details = soup.find_all('table', attrs={'id': 'recorddetails'})
    if len(record_details) == 1:
        counter = 0
        for tr in record_details[0].find_all('tr'):
            for caption in tr.find_all('td', attrs={'id': 'caption'}):
                if caption.text.find('Title') != -1:

                    # Get the title of the article
                    title = tr.find_all('td',attrs={'id': 'value'})
                    if len(title) == 1:
                        rec['tit'] = title[0].text
                elif caption.text.find('Author') != -1:

                    # Get the author of the article
                    author = tr.find_all('td', attrs={'id': 'value'})
                    if len(author) == 1:
                        rec['autaff'] = [[author[0].text, publisher]]
                elif caption.text.find('Director') != -1:

                    # Add the director to the comittee members
                    director = tr.find_all('td', attrs={'id': 'value'})
                    if len(director) == 1:
                        for sv in re.split('; ', director[0].text):
                            rec["supervisor"].append([sv])
                elif caption.text.find('Co.Supervisor') != -1:

                    # Add the director to the comittee members
                    codirector = tr.find_all('td', attrs={'id': 'value'})
                    if len(codirector) == 1:
                        for sv in re.split('; ', codirector[0].text):
                            rec["supervisor"].append([sv])
                elif caption.text.find('Committee member') != -1:

                    # Add the committee members
                    committee_members_section = tr.find_all('td', attrs={'id': 'value'})
                    if len(committee_members_section) == 1:
                        committee_members = committee_members_section[0].text.split(';')
                        #Committee Mebmbers do not count as supervisors
                        #for member in committee_members:
                        #    rec['supervisor'].append([convert_string(member)])
                elif caption.text.find('Physical description') != -1:

                    # Add number of pages
                    pages = tr.find_all('td', attrs={'id': 'value'})
                    if len(pages) == 1:
                        pages = pages[0].text
                        if re.search('\d+ p\.', pages):
                            rec['pages'] = re.sub('.*?(\d+) p\..*', r'\1', pages)
                elif caption.text.find('Defense date') != -1:

                    # Get the publication date
                    publication_date = tr.find_all('td', attrs={'id': 'value'})
                    if len(publication_date) == 1:
                        rec['date'] = publication_date[0].text.replace('-', '/')
                elif caption.text.find('CREF') != -1:

                    # Get the CREFs and add it the the note
                    crefs = []
                    crefs.append(tr.find_all('td', attrs={'id': 'value'})[0].text)

                    # Run this loop as long as needed to catch all of the entries under this point
                    i = 1
                    while True:
                        if record_details[0].find_all('tr')[counter+i].find_all('td', attrs={'id': 'caption'})[0].text != "":
                            break

                        crefs.append(record_details[0].find_all('tr')[counter+i].find_all('td', attrs={'id': 'value'})[0].text)

                        i += 1
                    rec['note'] += crefs
                    for cref in crefs:
                        if cref in boring:
                            keepit = False
                        elif cref in ['Astrophysique']:
                            rec['fc'] = 'a'
                        elif cref in ['Cristallographie']:
                            rec['fc'] = 'f'
                        elif cref in ['Informatique générale']:
                            rec['fc'] = 'c'
                        elif cref in ['Mathématiques', 'Statistique mathématique']:
                            rec['fc'] = 'm'
                        else:
                            rec['note'].append(cref)
                elif caption.text.find('Keywords') != -1:

                    # Get the keywords
                    # In case they are in an enumeration split it, otherwise Run a loop till all of them  are caught
                    keywords_section = tr.find_all('td', attrs={'id': 'value'})
                    if keywords_section[0].text.find(',') != -1:
                        keywords = keywords_section[0].text.split(', ')
                        for keyword in keywords:
                            rec['keyw'].append(keyword)
                    else:
                        keywords = []
                        keywords.append(tr.find_all('td', attrs={'id': 'value'})[0].text)
                        i = 1
                        while True:
                            if record_details[0].find_all('tr')[counter+i].find_all('td', attrs={'id': 'caption'})[0].text != "":
                                break

                            keywords.append(record_details[0].find_all('tr')[counter+i].find_all('td', attrs={'id': 'value'})[0].text)

                            i += 1
                        rec['keyw'] = keywords
                elif caption.text.find('Degree') != -1:

                    # Get the degree
                    degree_section = tr.find_all('td', attrs={'id': 'value'})
                    if len(degree_section) == 1:
                        degree = degree_section[0].text
                        if degree in boring:
                            keepit = False
                        else:
                            rec['note'].append(degree)
                elif caption.text.find('Language') != -1:

                    # Get the language of the article
                    language_section = tr.find_all('td', attrs={'id': 'value'})
                    if len(language_section) == 1:
                        if language_section[0].text.find('nglish') == -1:
                            rec['language'] = language_section[0].text
            counter += 1


    # Get the abstract
    abstract_link_section = soup.find_all('a', attrs={'class': 'first'})
    for i in abstract_link_section:
        if i.text == "Content":
            driver.get(i.get('href'))
            break

    soup = BeautifulSoup(driver.page_source, 'lxml')
    abstract_section = soup.find_all('td', attrs={'id': 'abstractvalue'})
    if len(abstract_section) == 1:
        rec['abs'] = ''
        rec['abs'] = abstract_section[0].text
        #rec['abs'] = convert_string(rec['abs'])
    if keepit:
        #Fulltext
        sleep(2)
        holdingsurl = re.sub('Details', 'Holdings', url)
        driver.get(holdingsurl)
        holdingspage = BeautifulSoup(driver.page_source, features="lxml")
        for script in holdingspage.find_all('script', attrs = {'type' : 'text/javascript'}):
            sstring = script.string
            #JSON parsing does not work because of quotation marks mess
            if sstring and re.search('\.pdf', sstring):
                for part in re.split('"File" *:', sstring)[1:]:
                    if re.search('(Full text|uvre compl).*Open access', part):
                        #rec['note'].append(part)
                        access = re.sub('.*(https.*?\.pdf).*', r'\1', part)
                        rec['FFT'] = access
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])
    sleep(10)




for page in range(1, pages):
    ejlmod3.printprogress("=", [[page, pages]])
    index_url = "https://difusion.ulb.ac.be/vufind//Search/Home?lookfor=&sort=pubdate+desc&submitButton=Recherche&type=general&filter[]=genreUlbStr:%22info:ulb-repo/semantics/doctoralThesis%22&page=" + str(page)
    driver.get(index_url)
    sleep(2)

    language_switch = driver.find_elements(By.ID, 'enLang')
    if len(language_switch) == 1:
        language_switch[0].click()
        sleep(5)
        for i in BeautifulSoup(driver.page_source, 'lxml').find_all('div', attrs={'id': 'resultItemLine1'}):
            for link in i.find_all('a'):
                if link.has_attr('href'):
                    final_link = "https://difusion.ulb.ac.be/" + re.sub('Holdings', 'Details', link['href'])
                    # Set the fake doi
                    doi = "20.2000/brussels/" + re.sub('\W', '', final_link)
                    if skipalreadyharvested and doi in alreadyharvested:
                        print(" ["+final_link+"] --> already in backup")
                    elif ejlmod3.checkinterestingDOI(doi):
                        get_sub_side(final_link)
                    else:
                        print(" ["+final_link+"] --> uninteresting")
    sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
