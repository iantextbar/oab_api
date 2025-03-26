from typing import Any, Dict, Union
import requests
import bs4
import re
import numpy as np
import pytesseract
from pytesseract import Output
from PIL import Image
import io

from oab_api.request_scraper import RequestScraper

HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en,en-GB;q=0.9,en-US;q=0.8,pt;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "__RequestVerificationToken=hKr8cwUFIDRuAIS_nqH9oXB1Xe4kazzl4erJ3yd8NR5_ElX5gDfOoS4vcAQrdXB3VCbikbgdwhhftT4llVBm4NCmHwqI4DALAvnttj0_dLo1; __utma=82693700.650500242.1739371243.1739371243.1739371243.1; __utmc=82693700; __utmz=82693700.1739371243.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __RequestVerificationToken=SHHGTC0oItWwZ4Fz44Rh1Zplu6tGOe1jDK4RtVn2EPJ-EjQysHAG5BUSi5mv4zVFUFIWUZbmbpcqxwgr2NyNnJLEIu_fsumOI3KUjDuci8g1",
    "Origin": "https://cna.oab.org.br",
    "Referer": "https://cna.oab.org.br/",
    "RequestVerificationToken": "OB_GrKphn4cRe9jn_6_ip3c7uoQeKqxMdgDPUyOsHPVYFmPub26s0M1T_MYK1FQUUWsiPfWpJz1TEtu1cIKXnaE_UAwwp3THKFkiFSdXhSg1:7p9Uqf5HcP9au8-jNhecK6RP6EKMOGOL5Dza_Q-1mECxQ0tiofb5ywuNNW9nYGAUfT0kRMwtVif3jur5Tk0sFKZe7eXWz68IER1A52xtpYU1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

class OABRequestScraper(RequestScraper):

    def __init__(
            self, id: str = "oab_request_scraper", method: str = 'POST'
    ) -> None:
        super().__init__(id=id, default_method=method.upper())
        self.default_method = method.upper()
        self.base_url = "https://cna.oab.org.br/"
        self.search_url = self.base_url + '/Home/Search'

    def text_extraction(
            self, text: str
    ) -> Dict[str, Any]:
        
        """
        Dado um texto com as informações relevantes de um profissional
        retorna um Dict com tais informações organizadas conforme esperado.

        Parâmetros:
            text (str): texto com informações de um advogado

        Retorna:
            Dict: Contendo as informações do advogado, caso sejam encontradas.
        """

        def nao_informado(text):
            if 'Não informado' in text:
                return 'NA'
            return text
        
        dados = {}
        text_list = [i for i in text.split("\n") if i not in ['', ' ']]

        # extraindo informações relevantes
        name = text_list[0]
        dados['nome'] = name
        pattern_insc = r"Subseção\s*(.*?)\s*Endereço"
        dados_insc_match = re.search(pattern_insc, text, re.DOTALL)

        if dados_insc_match:
            result = dados_insc_match.group(1).strip().split('\n')
            dados_insc = result[0].split(' ', 2)

            # verificando se os dados contém inscrição, seccional e subseção
            assert len(dados_insc) == 3
            insc = dados_insc[0]
            seccional = dados_insc[1].upper()
            subsec = dados_insc[-1]

            dados['insc'] = nao_informado(insc)
            dados['seccional'] = nao_informado(seccional)
            dados['subsecao'] = nao_informado(subsec)

        else:
            print('Não foi possível extrair os dados da inscrição do profissional')
            dados['insc'] = 'NA'
            dados['seccional'] = 'NA'
            dados['subsecao'] = 'NA'

        pattern_end = r"Profissional\s*(.*?)\s*Telefone"
        dados_end_match = re.search(pattern_end, text, re.DOTALL)

        if dados_end_match:
            end = re.sub("\s+", " ", re.sub("\n", " ", dados_end_match.group(1).strip()))
            dados['endereco'] = nao_informado(end)
        else:
            print('Não foi possível extrair os dados do endereço do profissional')
            dados['endereco'] = 'NA'

        pattern_tel = r"Telefone Profissional\s*(.*?)\s*SITUAÇÃO"
        dados_tel_match = re.search(pattern_tel, text, re.DOTALL)

        if dados_tel_match:
            tel = re.sub('\s+', ' ', re.sub("\n", " ", dados_tel_match.group(1).strip()))
            dados['telefone'] = nao_informado(tel)
        else:
            print('Não foi possível extrair os dados de telefone do profissional')
            dados['telefone'] = 'NA'
        
        sit = text_list[-2]
        dados['situacao'] = nao_informado(sit)

        return dados


    def fetch_adv(
            self, nome: str, insc: str
    ) -> Union[Dict[str, Any], None]:
        
        """
        Extrai Dict de informações para um advogado específico.

        Parâmetros:
            nome (str): Nome do advogado.
            insc (str): Código de inscrição do advogado.

        Retorna:
            Dict: Contendo as informações do advogado, caso sejam encontradas.
            None: Se não houver caderno para a data ou ocorrer algum erro.
        """

        # pegando verification token do BASE URL
        response = requests.get(self.base_url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        token_sec = soup.find('input', {"name": "__RequestVerificationToken"})

        try:
            token = token_sec.get('value')
        except:
            print('Não foi possível pegar o token de verificação da página')
            return None
        
        # declarando payloads e headers
        DATA = {'__RequestVerificationToken':token,
                "NomeAdvo": nome,
                "Insc": insc}
        
        # realizando a primeira extracao de dados
        params1 = {'url': self.search_url,
                  'payload': DATA,
                  'headers': HEADERS,
                  'method': self.default_method}
        try:
            response = self.fetch_data(params=params1)
        except:
            print('Erro na primeira extração')
            return None
        
        # realizando a segunda extracao
        detail_url = self.base_url + response['Data'][0]['DetailUrl']
        params2 = {'url':detail_url,
                  'method':'GET'}
        
        try:
            response2 = self.fetch_data(params=params2)
        except:
            print('Erro na segunda extração')
            return None
        
        # realizando a terceira extracao
        detail_url2 = self.base_url + response2['Data']['DetailUrl']
        params3 = {'url':detail_url2,
                   'method':'GET'}
        
        try:
            img_data = requests.get(detail_url2).content
        except:
            print('Não foi possível pegar os dados da imagem na terceira extração')
            return None
        
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image, lang='por')

        dados = self.text_extraction(text)

        return dados
        
