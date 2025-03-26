from abc import ABC, abstractmethod
from typing import Any, Dict, Union


class DataSource(ABC):
    """
    Interface para todos os conectores de dados.
    Possui atributos para identificação e categorização e define o contrato
    do método fetch_data, que pode retornar JSON (dict) ou conteúdo binário
    (bytes).
    """

    def __init__(self, id: str, category: str, method: str) -> None:
        self.id = id  # Identificador único
        self.category = category  # Ex: "requests", "selenium", "db"
        self.method = method  # Ex: "GET", "POST", "read"

    @abstractmethod
    def fetch_data(
        self, params: Dict[str, Any]
    ) -> Union[Dict[str, Any], bytes, None]:
        """
        Método obrigatório para todos os conectores.
        Pode retornar um dicionário (para JSON) ou bytes (para arquivos).
        """
        pass
