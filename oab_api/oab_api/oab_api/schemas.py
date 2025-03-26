from pydantic import BaseModel


class Message(BaseModel):
    message: str

class AdvogadoSchema(BaseModel):
    nome: str
    insc: str

class AdvogadoResponse(BaseModel):
    nome: str
    insc: str
    seccional: str
    subsecao: str
    endereco: str
    telefone: str
    situacao: str
