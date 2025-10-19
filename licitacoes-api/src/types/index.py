from typing import TypedDict

class LicitacaoType(TypedDict):
    id: int
    titulo: str
    descricao: str
    natureza: str