from langchain_huggingface import HuggingFaceEmbeddings
from typing import Any, Optional
import neo4j, cohere, os, dotenv, json
MODEL = "paraphrase-multilingual-mpnet-base-v2"

class AgenteRetrieval():
    '''Classe que representa um agente responsavel por realizar buscas
    vetoriais e simples em um banco de dados Neo4j, utilizando embeddings.'''
    def __init__(self, driver: neo4j.Driver, vector_terms:dict[str,str], simple_terms: dict[str,dict],
                 index_name: str, context:str = None, embedder: Optional[str] = MODEL) -> None:
        '''Construtor do AgenteRetrieval.
        
        Recebe:
            driver: neo4j.Driver; Driver de conexao com o Neo4j.
            vector_terms: dict[str,str]; Dicionario de atributos e 
            termos para a busca vetorial.
            simple_terms: dict[str,dict]; Dicionario de atributos e 
            termos para a busca simples.
            index_name: str; Nome do indice vetorial.
            embedder: (Optional) str; Nome do modelo de embed.
        '''
        dotenv.load_dotenv()
        self.driver = driver
        self.vector_terms = vector_terms
        self.simple_terms = simple_terms
        self.index_name = index_name
        self.context = context
        self.embedder = HuggingFaceEmbeddings(model_name=embedder)
        self.client = cohere.ClientV2(api_key=os.getenv('COHERE_API_KEY'))

    def get_search_results(self, query_vector: Optional[list[float]] = None, 
                           query_text: Optional[str] = None, top_k: int = 1000) -> neo4j.Result:
        '''
        Busca vetorial apenas sobre os nós filtrados pela query Cypher.

        Retorna:
            neo4j.Result: Objeto de resultado retornado pela consulta Neo4j.
        '''
        cypher_simples = self._gera_query_cypher_simples(self.simple_terms)
        cypher_vetorial = """
        CALL db.index.vector.queryNodes($index, $top_k, $queryVector)
        YIELD node, score
        WHERE node = node_obj
        RETURN node, score
        ORDER BY score DESCENDING
        """
        cypher_final = cypher_simples + cypher_vetorial
        results,_,_ = self.driver.execute_query(
            query_=cypher_final,
            parameters_={
                'index': self.index_name,
                'queryVector': query_vector or self.embedder.embed_query(self.vector_terms['embedding'][0]),
                'top_k': top_k
            }
        )
        return results

    def _gera_query_cypher_simples(self, simple_terms: dict[str,dict]) -> str:
        '''Funcao que gera uma query simples em cypher se baseando no contexto e
        nos diferentes termos de busca simples.
        
        Recebe:
            simple_terms: dict[str,dict]; Dicionario de termos para busca simples.'''
        funcao = """
        Você é um assistente que converte um dicionário em uma query Cypher.
        Instruções:
        A entrada é um JSON com entidades, atributos e valores.
        Gere um filtro Cypher usando esse JSON.
        O Cypher deve:
        Conter MATCH com todos os nós e relacionamentos correspondentes ao dicionário.
        Usar os atributos e valores corretamente com WHERE.
        Estar no formato de string, sem qualquer tipo de formatação.
        Não responder nada além da query Cypher SEM O RETURN.
        A entidade node_obj não deve ter classe imposta, deve ser genérica, apenas como (node_obj).
        Exemplo:
        Entrada JSON:
        {"node_obj": {"nome": "Fulano da Silva", "lattes": 123}, 
        "Departamento": {"nome": "Artes e Design"}, 
        "Producao": {"ano": 2021}}
        Saída Cypher:
        MATCH (p:Producao)<-[:PRODUZ]-(node_obj)-[:PERTENCE_A]->(d:Departamento)
        WHERE p.ano = 2021
        AND node_obj.nome = 'Fulano da Silva'
        AND node_obj.lattes = 123
        AND d.nome = 'Artes e Design'
        
        Exemplo:
        Entrada JSON:
        {'node_obj': {'tipo': 'Article'},
        'Professor': {'nome': 'Marcos Vianna Villas'}}
        Saída Cypher:
        MATCH (node_obj)<-[:PRODUZ]-(p:Professor)
        WHERE p.nome = 'Marcos Vianna Villas'
        AND node_obj.tipo = 'Article'
        """
        resposta = self.client.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": self.context + funcao}],
            documents=[
                {"data": json.dumps(simple_terms)}
            ]
        )
        return resposta.message.content[0].text