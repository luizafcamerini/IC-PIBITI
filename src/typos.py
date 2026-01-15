from pydantic import BaseModel

class CypherRelacionamentoInput(BaseModel):
    '''Formato de entrada para a criacao de queries de relacionamentos em Cypher.
    
    Args:
        entidades [Opcional]: lista de strings com os nomes das entidades (labels) dos nodes.
        relacionamentos: lista de strings com os nomes dos relacionamentos entre os nodes.
        filtro [Opcional]: string opcional com condicoes adicionais para a query.
    '''
    entidades: list[str] | None = None
    relacionamentos: list[str]
    filtro: str | None = None
    
class CypherNodeInput(BaseModel):
    '''Formato de entrada para a criacao de queries de nodes em Cypher.
    
    Args:
        entidade: string com o nome da entidade (label) do (um) node.
        filtro [Opcional]: string opcional com condicoes adicionais para a query.
    '''
    entidade: str
    filtro: str | None = None
    
class CypherVetorialInput(BaseModel):
    '''Formato de entrada para a criacao de queries vetoriais em Cypher.
    
    Args:
        atributos: lista de strings com os nomes dos atributos a serem usados na busca vetorial.
    '''
    atributos: list[str]
