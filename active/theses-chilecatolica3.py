# -*- coding: UTF-8 -*-
#program to harvest Chile U., Catolica
# JH 2022-10-31

from requests import Session
from json import loads
from time import sleep
import ejlmod3


with Session() as session:
    themes = [
        ('https://repositorio.uc.cl/assets/php/discovery.php?filtro=fq=dc.subject.dewey:Matem%C3%A1ticas%20f%C3%ADsica'
        '%20y%20qu%C3%ADmica%20OR%20dc.subject.other:Matem%C3%A1ticas%20f%C3%ADsica%20y%20qu%C3%ADmica%26fq=dc.type'
        ':Tesis%26&valor=Matem%C3%A1ticas%20f%C3%ADsica%20y%20qu%C3%ADmica&start=0&orden=asc&campus=Todos ', 2)
    ]

    recs = []
    for theme in themes:
        print("---- START NEW THEME ----")
        for page in range(0, theme[1]*20, 20):
            print("#### OPEN PAGE %i/%i  ####" % (page/20+1, theme[1]))
            resp = session.get(theme[0].replace('start=0', 'start='+str(page)))

            if resp.status_code != 200:
                print('[%s] --> Error: Can\'t open page!' % theme[0].replace('start=0', 'start='+str(page)))
                continue

            articles = loads(resp.content.decode('utf-8')).get('response').get('docs')
            for article in articles:
                sub_link = 'https://repositorio.uc.cl/assets/php/ficha.php?handle=' + article.get('handle')
                sleep(5)

                data_resp = session.get(sub_link)

                if data_resp.status_code != 200:
                    print('[{}] --> Error: Can\'t open page!'.format(sub_link))
                    continue
                print('[{}] --> Harvesting data'.format(sub_link))
                article_data = loads(data_resp.content.decode('utf-8')).get('response').get('docs')[0]

                rec = {'autaff': [], 'tc': 'T', 'jnl': 'BOOK', 'keyw': [], 'hdl': article_data.get('handle'), 'supervisor': []}

                # Get the supervisor
                for supervisor in article_data.get('dc.contributor.advisor'):
                    rec['supervisor'].append([supervisor])

                # Get author
                for author in article_data.get('author'):
                    rec['autaff'].append([author])

                # Get the issued date
                rec['date'] = article_data.get('dateIssued')[0]

                # Get the link
                rec['link'] = article_data.get('dc.identifier.uri')[0]

                # Get the pages
                for_mat = article_data.get('dc.format.extent')[0]
                pages = for_mat.split(' ')[1]
                rec['pages'] = pages

                # Get the language
                rec['lang'] = article_data.get('language')[0]

                # Get the keywords
                for keyword in article_data.get('dc.subject.other'):
                    rec['keyw'].append(keyword)

                # Get the title
                rec['tit'] = article_data.get('title')[0]

                # Get the pdf file
                rec['hidden'] = 'https://repositorio.uc.cl/xmlui/bitstream/handle/' + rec['hdl'] + '/' + article_data.get('archivos')[0].get('archivo')

                # Get the abstract if exits
                if article_data.get('dc.description.abstract') is not None:
                    rec['abs'] = article_data.get('dc.description.abstract')[0]

                recs.append(rec)
            sleep(5)
        sleep(5)


publisher = 'Chile U., Catolica'
jnlfilename = 'THESES-CHILECATOLICA-%s' % (ejlmod3.stampoftoday())


ejlmod3.writenewXML(recs, publisher, jnlfilename)
