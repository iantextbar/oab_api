from http import HTTPStatus

from fastapi import FastAPI

from oab_api.oab_request_scraper import OABRequestScraper

from oab_api.schemas import Message, AdvogadoSchema, AdvogadoResponse

app = FastAPI()

@app.post('/oab_fetch/', status_code=HTTPStatus.CREATED, response_model=AdvogadoResponse)
def fetch_adv(adv: AdvogadoSchema):
    
    nome = adv.nome
    insc = adv.insc

    scraper = OABRequestScraper()

    dados = scraper.fetch_adv(nome, insc)

    return dados
