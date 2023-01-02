from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
from time import sleep
import re
import ejlmod3
from requests import Session

publisher = 'Aveiro U.'
pages = 4
rpp = 50

jnlfilename = 'THESES-AVEIRO-%s' % (ejlmod3.stampoftoday())

boring = ['Programa Doutoral em Materiais e Processamento Avançados',
          'Programa Doutoral em Engenharia da Refinação, Petroquímica e Química',
          'Programa Doutoral em Ciência e Tecnologia Alimentar e Nutrição',
          'Apoio financeiro do INAGBE no quadro relação contratual no sector público', 
          'Programa Doutoral em Biologia e Ecologia das Alterações Globais',
          'Programa Doutoral em Biologia', 'Programa Doutoral em Biomedicina',
          'Programa Doutoral em Bioquímica', 'Programa Doutoral em Design',
          'Programa Doutoral em Educação', 'Programa Doutoral em Engenharia Química',
          'Programa Doutoral em História das Ciências e Educação Científica',
          'Programa Doutoral em Marketing e Estratégia', 'Programa Doutoral em Música',
          'Programa Doutoral em Políticas Públicas', 'Programa Doutoral em Química',
          'Programa Doutoral em Telecomunicações', 'Programa Doutoral em Tradução e Terminologia',
          'Programa Doutoral em Turismo', 'Programa Doutoral em Ciência Política',
          'Programa Doutoral em Ciências Económicas e Empresariais',
          'Programa Doutoral em Ciências e Engenharia do Ambiente',
          'Programa Doutoral em Ciência, Tecnologia e Gestão do Mar',
          'Programa Doutoral em Engenharia e Gestão Industrial',
          'Programa Doutoral em Estudos Culturais',
          'Programa Doutoral em Gerontologia e Geriatria',
          'Programa Doutoral em Multimédia em Educação',
          'Programa Doutoral em Psicologia', 'Doutoramento em Linguística',   
          'Programa Doutoral em Território, Riscos e Políticas Públicas',
          'Doutoramento em Biologia', 'Doutoramento em Ciências e Engenharia do Ambiente',
          'Doutoramento em Engenharia Mecânica', 'Doutoramento em Marketing e Estratégia',
          'Doutoramento em Música', 'Doutoramento em Psicologia',
          'Programa Doutoral em Ciências da Reabilitação',
          'Programa Doutoral em Ciências do Mar (Mares)',
          'Programa Doutoral em Contabilidade', 'Doutoramento em Ciências Sociais',
          'Programa Doutoral em Didática e Formação',
          'Programa Doutoral em Engenharia Civil',
          'Programa Doutoral em E-Planeamento',
          'Programa Doutoral em Estudos Literários',
          'Programa Doutoral em Geociências',
          'Programa Doutoral em Química Sustentável',
          'Programa Doutoral em Sistemas Energéticos e Alterações Climáticas',
          'Ddoutoramento em Biologia e Ecologia das Alterações Globais',
          'Departamento em Química',
          'Desenvolvimento de um sistema de tomografia computorizada de contagem de fotão único usando MPGDs',
          'Design', 'Doutoramento Biologia',
          'Doutoramento em Biologia Aplicada - Ecologia, Biodiversidade e Gestão de Ecossistemas',
          'Doutoramento em Biologia - Biologia Marinha',
          'Doutoramento em Biologia e Ecologia das Alterações Globais (Especialização em Ecologia e Biologia Tropical)',
          'Doutoramento em Biologia e Ecologia das Alterações Globais – ramo Biologia e Ecologia Marinha',
          'Doutoramento em Biologia e Ecologia das Alterações Globais',
          'Doutoramento em Biologia Marinha', 'Doutoramento em Biomedicina',
          'Doutoramento em Bioquímica', 'Doutoramento em Ciências Biomédicas',
          'Doutoramento em Ciências da Educação', 'Doutoramento em Ciências do Mar e do Ambiente',
          'Doutoramento em Ciências do Mar', 'Doutoramento em Ciências e engenharia do ambiente',
          'Doutoramento em Ciências e Tecnologias da Saúde - Decisão Clínica',
          'Doutoramento em Ciências e Tecnologias da Saúde',
          'Doutoramento em Ciências Políticas', 'Doutoramento em Ciências Sociais',
          'Doutoramento em Contabilidade', 'Doutoramento em Cultura Portuguesa',
          'Doutoramento em Design',
          'Doutoramento em Didáctica e Desenvolvimento Curricular',
          'Doutoramento em Didáctica e Formação - Avaliação',
          'Doutoramento em Didáctica e Formação - Didáctica e Desenvolvimento Curricular',
          'Doutoramento em Didáctica e Formação - Didática e Desenvolvimento Curricular',
          'Doutoramento em Didáctica e Formação',
          'Doutoramento em Didáctica e Formação - Supervisão',
          'Doutoramento em Didática e Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação - Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação - Didáctica e Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação Didáctica e Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação - Didática e Desenvolviemto Curricular',
          'Doutoramento em Didática e Formação - Didatica e Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação - Didática e Desenvolvimento Curricular',
          'Doutoramento em Didática e Formação (ramo de Avaliação),',
          'Doutoramento em Didática e Formação',
          'Doutoramento em Didática e Formação - Supervisão',
          'Doutoramento em Ecologia Aplicada',
          'Doutoramento em Economia',
          'Doutoramento em Educação - Administração e Políticas Educacionais',
          'Doutoramento em Educação - Didática e Desenvolvimento Curricular',
          'Doutoramento em Educação - Psicologia da Educação',
          'Doutoramento em Educação – Ramo Supervisão e Avaliação',
          'Doutoramento em Educação',
          'Doutoramento em Educação - Supervisão e Avaliação',
          'Doutoramento em Engenharia Biomédica',
          'Doutoramento em Engenharia Civil', 'Doutoramento em Engenharia Civil,',
          'Doutoramento em Engenharia da Refinação, Petroquímica e Química',
          'Doutoramento em Engenharia e Gestão Industrial',
          'Doutoramento em Engenharia Química - Bioengenharia',
          'Doutoramento em Engenharia Química - Especialização em Engenharia de Materiais e Produtos Macromoleculares',
          'Doutoramento em Engenharia Química', 'Doutoramento em Estudos Culturais',
          'Doutoramento em Estudos de Arte', 'Doutoramento em Estudos em Ensino Superior',
          'Doutoramento em etnomusicologia', 'Doutoramento em Geotecnologias',
          'Doutoramento em Gerontologia e Geriatria - Geriatria',
          'Doutoramento em Gerontologia e Geriatria - Gerontologia',
          'Doutoramento em Gerontologia e Geriatria',
          'Doutoramento em Gestão Industrial', 'Doutoramento em Gestão',
          'Doutoramento em Linguística', 'Doutoramento em Literatura',
          'Doutoramento em Multimédia em Educação',
          'Doutoramento em Música - Ensino Instrumento/Canto',
          'Doutoramento em Música - Estudos em Performance',
          'Doutoramento em Música - Etnomusicologia',
          'Doutoramento em Música (Performance/ Guitarra Clássica)',
          'Doutoramento em Música - Performance Jazz',
          'Doutoramento em Música - Performance',
          'Doutoramento em Música – Performance',
          'Doutoramento em Música', 'Doutoramento em Políticas Públicas',
          'Doutoramento em Química',
          'Doutoramento em Química Sustentável',
          'Doutoramento em Secção Autónoma de Ciências da Saúde da Universidade de Aveiro',
          'Doutoramento em Sistemas Energéticos e Alterações Climáticas',
          'Doutoramento em Tradução', 'Doutoramento em Turismo',
          'Doutoramento emTurismo', 'Doutoramento Engenharia Civil',
          'Doutoramento Música']
recs = []

def extract_links(content: str, prafix: str):
    soup = BeautifulSoup(content, 'lxml')
    article_links = soup.find_all('a', {'href': re.compile('/handle/\d{0,}/\d{0,}')})
    filtered = filter(lambda article: False if article.parent.get('class') is None
                        else True if 'evenRowOddCol' in article.parent.get('class') or 'oddRowOddCol' in article.parent.get('class')
                        else False, article_links)

    return list(filtered)


hdr = {'User-Agent' : 'Magic Browser'}
def get_sub_site(url, sess):
    print("[{}] --> Harvesting data".format(url))
    if ejlmod3.ckeckinterestingDOI(url):
        keepit = True
        req = urllib.request.Request(url, headers=hdr)
        soup = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

        rec = {'tc': 'T', 'jnl': 'BOOK', 'note' : []}
        ejlmod3.metatagcheck(rec, soup, ['DC.creator', 'DCTERMS.issued', 'DC.identifier', 'DC.rights', 'DC.subject', 'citation_title', 'citation_pdf_url', 
                                         'DCTERMS.abstract', 'citation_language'])
        rec['autaff'][-1].append(publisher)
        for meta in soup.head.find_all('meta', attrs = {'name' : 'DC.description'}):
            prog = meta['content']
            if prog in boring:
                keepit = False
            elif prog in ['Programa Doutoral em Informática',
                          'Programa Doutoral em Informação e Comunicação em Plataformas Digitais', 'doutoramento Ciências da Computação',
                          'Doutoramento Ciências da Computação', 'Doutoramento em Ciências da Computação',
                          'Doutoramento conjunto em Informação e Comunicação em Plataformas Digitais',
                          'Doutoramento conjunto, em Informação e Comunicação em Plataformas Digitais',
                          'Doutoramento conjunto em Informática', 'Doutoramento em Informação e Comunicação em Plataformas Digitais',
                          'Doutoramento em Informática (MAP-i)', 'Doutoramento em Informática (MAP-I)',
                          'Doutoramento em Informática', 'Doutoramento conjunto em Matemática - Matemática e Aplicações (PDMA)',
                          'Doutoramento conjunto MAPi em Ciências da Computação', 'Doutoramento conjunto MAP-i em Informática',
                          'Doutoramento conjunto MAPi em Informática', 'Doutoramento conjunto MAP-i']:
                rec['fc'] = 'c'
            elif prog in ['Programa Doutoral em Matemática Aplicada', 'Programa Doutoral em Matemática',
                          'Doutoramento em Matemática e Aplicações (PDMA)', 'Doutoramento em Matemática e Aplicações',
                          'Doutoramento em Matemática', 'Programa Doutoral em Matemática e Aplicações']:
                rec['fc'] = 'm'
            else:
                rec['note'].append(prog)
        if keepit:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(url)
        sleep(10)
            
    

with Session() as session:
    for page in range(pages):
        tocurl = 'https://ria.ua.pt/browse?type=type&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&value=doctoralThesis&offset=' + str(rpp*page)
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        index_resp = session.get(tocurl)

        if index_resp.status_code != 200:
            print("[{}] --> Error: Can't open this page! Skipping page...".format(tocurl))
            continue
#        print(ejlmod3.getdspacerecs(BeautifulSoup(index_resp.content.decode('utf-8'), 'lxml'), 'https://ria.ua.pt'))
        for article in extract_links(index_resp.content.decode('utf-8'), 'https://ria.ua.pt'):
            get_sub_site('https://ria.ua.pt' + article.get('href'), session)
        sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
