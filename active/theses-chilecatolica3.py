# -*- coding: UTF-8 -*-
#program to harvest Chile U., Catolica
# JH 2022-10-31

from requests import Session
from json import loads
from time import sleep
import ejlmod3
import re

publisher = 'Chile U., Catolica'
jnlfilename = 'THESES-CHILECATOLICA-%s' % (ejlmod3.stampoftoday())
years = 3

reorcid = re.compile('.*(\d\d\d\d\-\d\d\d\d\-\d\d\d\d\-\d\d\d.).*')
with Session() as session:
    themes = [
        ('https://repositorio.uc.cl/assets/php/discovery.php?filtro=fq=dc.subject.dewey:Astronom%C3%ADa'
         '%20OR%20dc.subject.other:Astronom%C3%ADa%26fq=dc.type'
         ':Tesis%26&valor=Astronom%C3%ADa&start=0&orden=asc&campus=Todos ', (ejlmod3.year()-2016)//2),
        ('https://repositorio.uc.cl/assets/php/discovery.php?filtro=fq=dc.subject.dewey:Matem%C3%A1ticas%20f%C3%ADsica'
         '%20y%20qu%C3%ADmica%20OR%20dc.subject.other:Matem%C3%A1ticas%20f%C3%ADsica%20y%20qu%C3%ADmica%26fq=dc.type'
         ':Tesis%26&valor=Matem%C3%A1ticas%20f%C3%ADsica%20y%20qu%C3%ADmica&start=0&orden=asc&campus=Todos ', (ejlmod3.year()-2009)//2)        
    ]
    recs = []
    rpp = 20
    for (url, pages) in themes:
        print("---- START NEW THEME ----")
        for page in range(0, pages*rpp, rpp):
            print("#### OPEN PAGE %i/%i  ####" % (page/rpp+1, pages))
            resp = session.get(url.replace('start=0', 'start='+str(page)))

            if resp.status_code != 200:
                print('[%s] --> Error: Can\'t open page!' % url.replace('start=0', 'start='+str(page)))
                continue

            articles = loads(resp.content.decode('utf-8')).get('response').get('docs')
            for article in articles:
                keepit = True
                if ejlmod3.checkinterestingDOI(article.get('handle')):
                    sub_link = 'https://repositorio.uc.cl/assets/php/ficha.php?handle=' + article.get('handle')
                else:
                    continue
                sleep(5)

                data_resp = session.get(sub_link)

                if data_resp.status_code != 200:
                    print('[{}] --> Error: Can\'t open page!'.format(sub_link))
                    continue
                print('[{}] --> Harvesting data'.format(sub_link))
                article_data = loads(data_resp.content.decode('utf-8')).get('response').get('docs')[0]

                rec = {'autaff': [], 'tc': 'T', 'jnl': 'BOOK', 'keyw': [], 'hdl': article_data.get('handle'), 'supervisor': [], 'note' : []}

                # Get the supervisor
                for supervisor in article_data.get('dc.contributor.advisor'):
                    rec['supervisor'].append([supervisor])

                # Get author
                for author in article_data.get('author'):
                    rec['autaff'].append([author])

                # Get the issued date
                rec['date'] = article_data.get('dateIssued')[0]
                if int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
                       keepit = False

                # Get the link
                rec['link'] = article_data.get('dc.identifier.uri')[0]

                # Get the pages
                if article_data.get('dc.format.extent'):
                    for_mat = article_data.get('dc.format.extent')[0]
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', for_mat)

                # Get the language
                if article_data.get('language'):
                    rec['lang'] = article_data.get('language')[0]

                # Get the keywords
                try:
                    for keyword in article_data.get('dc.subject.other'):
                        rec['keyw'].append(keyword)
                except:
                    print('    no dc.subject.other')

                # Get the title
                rec['tit'] = article_data.get('title')[0]

                # Get the pdf file
                rec['hidden'] = 'https://repositorio.uc.cl/xmlui/bitstream/handle/' + rec['hdl'] + '/' + article_data.get('archivos')[0].get('archivo')

                # Get the abstract if exits
                if article_data.get('dc.description.abstract') is not None:
                    rec['abs'] = article_data.get('dc.description.abstract')[0]

                #type?
                if article_data.get("dc.description"):
                    for description in article_data.get("dc.description"):
                        if re.search('(Msc|MSc|Master of Science|Mater in|Mag.ster|Master.s|Master) (degree|in|en|of) ', description):
                            keepit = False
                        elif  not  re.search('(Doctor|PHD|PhD|Ph\.D\.|Docteur|Dissertation) (en|in|of) ', description):
                            rec['note'].append(description)
                #ORCID?
                if article_data.get('dc.information.autoruc'):
                    for autoruc in article_data.get('dc.information.autoruc'):
                        if reorcid.search(autoruc):
                            if re.search(rec['autaff'][0][0], autoruc):
                                rec['autaff'][0].append(reorcid.sub(r'ORCID:\1', autoruc))
                            elif rec['supervisor']:
                                for sv in rec['supervisor']:
                                    if re.search(sv[0], autoruc):
                                        sv.append(reorcid.sub(r'ORCID:\1', autoruc))
                rec['autaff'][0].append(publisher)
                if keepit:
                    recs.append(rec)
                else:
                    ejlmod3.adduninterestingDOI(rec['hdl'])
            sleep(5)
        sleep(5)




ejlmod3.writenewXML(recs, publisher, jnlfilename)
