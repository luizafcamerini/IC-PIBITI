from pydantic import BaseModel

class CypherRelacionamentoInput(BaseModel):
    entidades: list[str] | None = None
    relacionamentos: list[str] | None = None
    filtro: str | None = None
    
class CypherNodeInput(BaseModel):
    entidades: list[str] | None = None
    filtro: str | None = None
    
class CypherVetorialInput(BaseModel):
    atributos: list[str]
    filtro: str | None = None