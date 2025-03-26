from typing import Any, Dict, Union

import requests

from oab_api.base import DataSource


class RequestScraper(DataSource):
    """
    Scraper utilizando requests de forma abstrata, permitindo métodos GET e
    POST.
    Aceita parâmetros dinâmicos, como payload, headers e timeout.
    """

    def __init__(
        self, id: str = 'request_scraper', default_method: str = 'GET'
    ) -> None:
        super().__init__(id=id, category='requests', method=default_method)
        self.default_method = default_method.upper()

    def fetch_data(
        self, params: Dict[str, Any]
    ) -> Union[Dict[str, any], bytes, None]:
        """
        Executa uma requisição HTTP de forma genérica.

        Parâmetros esperados em `params`:
            - url (str): URL a ser acessada (obrigatório)
            - method (str): 'GET' ou 'POST'. Se não informado, utiliza o método
                            padrão.
            - payload (dict, opcional): Dados a serem enviados (query params
                                        para GET ou dados para POST).
            - headers (dict, opcional): Cabeçalhos customizados.
            - timeout (int, opcional): Tempo de espera em segundos (padrão: 5).

        Retorna:
            - dict, se o Content-Type indicar JSON;
            - bytes, para outros tipos de conteúdo;
            - None em caso de erro.
        """
        url = params.get('url')
        if not url:
            raise ValueError('A URL deve ser informada em params["url"]')

        method = params.get('method', self.default_method).upper()
        payload = params.get('payload', None)
        headers = params.get('headers', {'User-Agent': 'Mozilla/5.0'})
        timeout = params.get('timeout', 5)

        try:
            if method == 'GET':
                response = requests.get(
                    url, params=payload, headers=headers, timeout=timeout
                )
            elif method == 'POST':
                response = requests.post(
                    url, data=payload, headers=headers, timeout=timeout
                )
            else:
                raise ValueError(f'Método HTTP "{method}" não suportado')
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                return response.content
        except requests.RequestException as e:
            print(f'Erro na requisição: {e}')
            return None
