from typing import Any, Optional
from neo4j_graphrag.types import RawSearchResult
import cohere, json
from dotenv import load_dotenv
import os

class AgenteLeituraResposta():
    '''Classe que representa um agente responsavel pela leitura,
    interpretacao, segmentacao e resposta de uma pergunta em
    linguagem natural.'''
    
    def __init__(self, schema:str, context:str = None):
        '''Construtor do AgenteLeituraResposta.
        
        Recebe:
            schema: str; Esquema do banco de dados.
            context: str; (Optional) O contexto a ser dado a LLM.
            O contexto precisa de duas bind variables (%s), para o schema
            e para a pergunta, nessa ordem.
        '''
        if not context:
            self.context = os.getenv('CONTEXT')
        load_dotenv()
        self.schema = schema
        self.client = cohere.ClientV2(api_key=os.getenv('COHERE_API_KEY'))
        
    def processa_pergunta(self, pergunta)-> tuple[str,str]:
        '''Funcao que processa uma pergunta e a segmenta em
        termos vetoriais e termos simples, e os retorna nessa ordem.
        
        Recebe:
            pergunta: str; A pergunta feita pelo usuario.'''
        vetor = self._identifica_vetor(self.context % (self.schema, pergunta))
        simples = self._identifica_simples(self.context % (self.schema, pergunta))
        return vetor,simples
    
    def _identifica_vetor(self, pergunta_completa:str) -> str:
        '''Funcao que identifica o(s) termo(s) para a busca semantica.
        
        Recebe:
            pergunta_completa: str; A pergunta feita pelo usuario, com contexto e schema.'''
        funcao = """
            Identifique, na pergunta do usuario, qual é(são) o(s) termos(s) para BUSCA VETORIAL.
            Na sua resposta, NÃO RESPONDA NADA ALÉM DO(S) TERMO(S) PARA BUSCA VETORIAL.
            SEMPRE responda em formato de dicionario e sublista (mesmo tendo apenas um ou nenhum termo!!!!),
            como {"embedding":["termo1", "atributo2": "termo2"]}. 
        """
        resposta = self.client.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": pergunta_completa + funcao}],
            response_format={"type":"json_object"}
        )
        return resposta.message.content[0].text
    
    def _identifica_simples(self, pergunta_completa:str) -> str:
        '''Funcao que identifica o(s) termo(s) para a busca 
        simples (por igualdade).
        
        Recebe:
            pergunta_completa: str; A pergunta feita pelo usuario, com contexto e schema.'''
        funcao = """
        Identifique na pergunta do usuário os termos para busca simples e seus atributos do schema.
        O nó principal da pergunta (o que se quer buscar) deve ser chamado de "node_obj".
        Responda SOMENTE em formato de dicionário com subdicionários (mesmo que haja só um ou nenhum termo).
        Nunca explique, apenas retorne o dicionário.
        Exemplo 1:
        Pergunta: "Quais são os livros de 2025 do professor Arthur Leite que falem sobre meio ambiente?"
        Nó objetivo: Producao
        Resposta:
        {"node_obj": {"ano": 2025, "tipo": "Book"},
        "Professor": {"nome": "Arthur Leite"}}
        Exemplo 2:
        Pergunta: "Quais as produções do professor Fulano sobre banco de dados?"
        Nó objetivo: Producao
        Resposta:
        {"node_obj": {},
        "Professor": {"nome": "Fulano"}}
        """
        resposta = self.client.chat(
            model="command-a-03-2025",
            messages=[{"role": "user", "content": pergunta_completa + funcao}],
            response_format={"type":"json_object"}
        )
        return resposta.message.content[0].text
    
    def formula_resposta(self, pergunta:str, dados: RawSearchResult) -> str:
        '''Funcao que formula uma resposta final para o usuario com
        base nos dados recolhidos.
        
        Recebe:
            pergunta: str; A pergunta feita pelo usuario.
            dados: RawSearchResult; Os dados recolhidos do banco.'''
        funcao = """
        Com base nos dados recebidos, na pergunta do usuario e no contexto gere uma resposta à
        pergunta do usuario de forma completa, descrevendo os dados recebidos
        """
        return
    
if __name__ == '__main__':
    schema = """
    Node properties:
    Professor (nome: STRING, lattes: INT)
    Producao (titulo: STRING, ano: INT, tipo: "Article"|"Thesis"|"Chapter"|"Book", embedding: VECTOR)
    Departamento (nome: STRING)
    Relationship properties:
    PRODUZ ()
    PERTENCE_AO_DEPT ()
    The relationships:
    (:Professor)-[:PRODUZ]->(:Producao)
    (:Professor)-[:PERTENCE_AO_DEPT]->(:Departamento)
    Indexes:
    producao-embeddings (VECTOR INDEX ON Producao.embedding)
    """
    agente = AgenteLeituraResposta(schema)
    vetorial, simples = agente.processa_pergunta('Quais são os livros de 2025 do professor Arthur Leite que falem sobre natureza?')
    while True:
        try:
            vetorial_json = json.loads(vetorial)
            simples_json = json.loads(simples)
            break
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON simples:", simples)