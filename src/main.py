from agentes.AgenteLeituraResposta import AgenteLeituraResposta
from agentes.AgenteRetrieval import AgenteRetrieval
from agentes.Database import Database
import os, dotenv
import json

if __name__ == '__main__':
    dotenv.load_dotenv()
    schema = os.getenv('SCHEMA')
    agente = AgenteLeituraResposta(schema)
    pergunta = input("Digite sua pergunta: ")
    vetorial, simples = agente.processa_pergunta(pergunta)
    while True:
        try:
            vetorial_json = json.loads(vetorial)
            simples_json = json.loads(simples)
            break
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON simples:", simples)
    db = Database(os.getenv('NEO4J_URI'), os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    agente_retrieval = AgenteRetrieval(
        driver=db.driver,
        vector_terms=vetorial_json,
        simple_terms=simples_json,
        index_name=os.getenv('VECTOR_INDEX_NAME'),
        context=os.getenv('CONTEXT'),
        embedder=os.getenv('EMBEDDER_MODEL')
    )
    resultados = agente_retrieval.get_search_results(query_text=pergunta)
    if resultados:
        print("Resultados encontrados:")
        for record in resultados:
            r = dict(record['node'])
            r.pop('embedding', None)
            print("Nó retornado: ", r)
            print("Score: ", record['score'])
    else:
        print("Nenhum resultado encontrado.")
    db.close_driver()