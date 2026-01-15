from langchain.tools import tool
from langchain.agents import create_tool_calling_agent
from cohere import ClientV2
import os, neo4j, json
from pydantic import BaseModel
from dotenv import load_dotenv
from ..typos import *

load_dotenv()

class Agente():
    '''Agente de IA que utiliza tools para buscar e responder questoes sobre o banco de dados.'''
    def __init__(self):
        self.model = os.getenv('CHAT_MODEL')
        self.agent = create_tool_calling_agent(self.model,
                                                tools = [self.interpreta_pergunta,
                                                        self.recolhe_dados, self.cria_query_relacionamentos,
                                                        self.cria_query_vetorial, self.cria_query_nodes])
        self.missing_slots = set()
        self.done_slots = set()
    
    @tool
    def check_resposta_completa(self, resposta:str):
        '''Verifica se a resposta da LLM está completa para responder a pergunta.'''
        if len(self.missing_slots) == 0:
            if len(self.done_slots) > 0:
                return True
        return False
    
    @tool
    def recolhe_dados(self, query:str, parameters:dict):
        '''Recolhe dados do banco de dados a partir de uma query em Cypher dada.'''
        pass
    
    @tool
    def cria_query_relacionamentos(self, C: CypherRelacionamentoInput) -> str:
        '''Cria uma query um Cypher focada apenas em relacionamentos do banco de dados.'''
        pass
    
    @tool
    def cria_query_vetorial(self, C: CypherVetorialInput) -> str:
        '''Cria uma query um Cypher focada apenas em busca vetorial de titulos de 
        producoes do banco de dados.'''
        cypher_vetorial = ""
        embedding_list = [self.cria_embedding(at for at in C.atributos)]
        for embedding in embedding_list:
            cypher_vetorial += """
                CALL db.index.vector.queryNodes($index, 10, $embedding)
                YIELD node, score
                WHERE node = node_obj
                RETURN node, score
                ORDER BY score DESCENDING;
            """
        return cypher_vetorial
    
    @tool
    def cria_query_nodes(self, C: CypherNodeInput) -> str:
        '''Cria uma query um Cypher focada apenas em nos do banco de dados.'''
        pass
    
    def cria_embedding(self, texto:str) -> list[float]:
        '''Cria um embedding a partir de um texto dado.'''
        pass