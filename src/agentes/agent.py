from langchain.tools import tool
from langchain.agents import create_tool_calling_agent
from cohere import ClientV2
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from ..typos import *
from .Database import *
import os, json, neo4j
load_dotenv()

class Agente():
    '''Agente de IA que utiliza tools para buscar e responder questoes sobre o banco de dados.'''
    def __init__(self, index_name:str, driver:GraphDatabase.driver):
        self.model = os.getenv('CHAT_MODEL')
        self.agent = create_tool_calling_agent(self.model,
                                                tools = [self.cria_query_vetorial,
                                                        self.recolhe_dados,
                                                        self.cria_query_relacionamentos,
                                                        self.cria_query_nodes])
        self.missing_slots = set()
        self.done_slots = set()
        self.index = index_name
        self.driver = driver
    
    @tool
    def check_resposta_completa(self, resposta:str):
        '''Verifica se a resposta da LLM está completa para responder a pergunta.'''
        if len(self.missing_slots) == 0:
            if len(self.done_slots) > 0:
                return True
        return False
    
    @tool
    def recolhe_dados(self, query:str, parameters:dict) -> neo4j.Result:
        '''Recolhe dados do banco de dados a partir de uma query em Cypher dada.'''
        pass
    
    @tool
    def cria_query_relacionamentos(self, C: CypherRelacionamentoInput) -> str:
        '''Cria uma query um Cypher focada apenas em relacionamentos entre nodes
        do banco de dados.'''
        cypher = "MATCH "
        for i in range(len(C.entidades)):
            cypher += f"(n{i}:{C.entidades[i]})"
            if i < len(C.relacionamentos):
                cypher += f"-[:{C.relacionamentos[i]}]->"
        if C.filtro:
            cypher += f"WHERE {C.filtro}"
        return cypher

    @tool
    def cria_query_vetorial(self, C: CypherVetorialInput) -> str:
        '''Cria uma query um Cypher focada apenas em busca vetorial do banco de dados.'''
        cypher_vetorial = ""
        embedding_list = [self.cria_embedding(at for at in C.atributos)]
        for embedding in embedding_list:
            cypher_vetorial += f"""
                CALL db.index.vector.queryNodes({self.db.indice}, 10, {embedding})
                YIELD node, score
                WHERE node = node_obj
                RETURN node, score
                ORDER BY score DESCENDING;
            """
        return cypher_vetorial.strip()
    
    @tool
    def cria_query_nodes(self, C: CypherNodeInput) -> str:
        '''Cria uma query um Cypher focada apenas em nodes e seus atributos do banco de dados.'''
        if C.filtro:
            query = f"""
            MATCH (n:{C.entidade})
            WHERE {C.filtro}
            RETURN n;
            """
        else:
            query = f"""
            MATCH (n:{C.entidade})
            RETURN n;
            """
        return query.strip()
    
    @tool
    def junta_resultados_vetorial_query_relacionamentos(self, resultados: neo4j.Result,
                                                        C: CypherRelacionamentoInput) -> str:
        '''Junta os nodes resultados de uma query vetorial e os acrescenta em uma query de relacionamentos.
        Retorna a query completa em Cypher. Esta ferramenta depende dos resultados de uma query vetorial anterior.'''
        cypher = "MATCH "
        indice_node_producao = 0
        for i in range(len(C.entidades)):
            cypher += f"(n{i}:{C.entidades[i]})"
            if i < len(C.relacionamentos):
                cypher += f"-[:{C.relacionamentos[i]}]->"
            if C.entidades[i].lower() == "producao":
                indice_node_producao = i
        
        # Adiciona os resultados da query vetorial
        resultado_ids = [record.get("node").get("id") for record in resultados]
        if resultado_ids:
            ids_str = ", ".join([f"'{id}'" for id in resultado_ids])
            cypher += f" WHERE n{indice_node_producao}.id IN [{ids_str}]"
            if C.filtro:
                cypher += f" AND {C.filtro}"
        elif C.filtro:
            cypher += f" WHERE {C.filtro}"
        return cypher

    def cria_embedding(self, texto:str) -> list[float]:
        '''Cria um embedding a partir de um texto dado. O embedding e
        usado para buscas vetoriais no banco de dados.'''
        pass