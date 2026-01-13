# Iniciação Científica PIBITI 2024-2025
Este repositório contém o projeto de pesquisa e desenvolvimento da aluna Luíza Ferreira Camerini orientada pelo professor Sergio Lifschitz na PUC-Rio.

Este projeto tem como objetivo implementar uma dinâmica de Retrieval Augumented Generation (RAG) que sirva de grande suporte ao sistema atual Quem@PUC ([clique aqui para acessar](https://quempuc.biobd.inf.puc-rio.br/)), possibilitando assim que perguntas de linguagem natural sobre competências de professores da PUC-Rio sejam respondidas de forma rápida e precisa.

## Estrutura do repositório
A estrutura desta repositório é bem simpliicada:
```
├── agentes/
│   ├── AgenteLeituraResposta.py
│   └── AgenteRetrieval.py
├── testes/
│   ├── busca_vetorial.py
│   └── cria_kg.ipynb
│   └── embeddings.ipynb
│   └── graphrag_text2cypher.ipynb
│   └── graphrag.ipynb
├── .env
├── .gitignore
├── README.md
├── requirements.txt
```

### Agentes de IA
No diretório ```agentes/```, temos classes que representam os três componentes principais deste RAG: o agente de leitura, o agente de retrieval e o agente de resposta.

Como diz a [documentação deste projeto](https://docs.google.com/document/d/1LkRXDiEh6nJGmBGXoUgyOkFAM1ZRdUm5/edit?usp=sharing&ouid=101372134932259489935&rtpof=true&sd=true), houve várias razões do porquê separar a dinâmica de RAG em três componentes, como o tipo de pergunta de competência que buscou-se responder e o que deveria ser levado em consideração do lado do banco de dados para o contexto dado à LLM.
```
├── agentes/
    ├── AgenteLeituraResposta.py
    └── AgenteRetrieval.py
```

#### AgenteLeituraResposta
Este agente é responsável por receber a pergunta do usuário e segmentar a pergunta em duas

#### AgenteRetrieval
Para o modelo de embedding, usamos o ```paraphrase-multilingual-mpnet-base-v2``` ou qualquer outro compatível com o framework [Hugging Face sentence-transformers](https://python.langchain.com/docs/integrations/text_embedding/sentence_transformers/#setup) do LangChain.

### Variáveis de ambiente

Coloque as variáveis de ambiente em um arquivo `.env` na raiz do projeto (não comite esse arquivo). Abaixo há uma breve descrição das variáveis usadas por este projeto e exemplos de valores.

- **NEO4J_URI**: URL de conexão com o Neo4j. Exemplo: `bolt://localhost:7687` ou `neo4j+s://<host>:7687`. Obrigatória se o projeto acessar o banco Neo4j.
- **NEO4J_USERNAME**: Usuário do Neo4j (ex.: `neo4j`).
- **NEO4J_PASSWORD**: Senha do Neo4j.
- **NEO4J_DATABASE**: Nome do database Neo4j a ser usado (ex.: `neo4j`).
- **COHERE_API_KEY**: Chave da API da Cohere (necessária se o sistema usar Cohere para geração ou embeddings).
- **SCHEMA**: (Opcional) string que identifica o schema ou prefixo usado na criação de entidades/nós no grafo.
- **CONTEXT**: (Opcional) contexto padrão que o agente de leitura/resposta pode usar ao construir promptos para a LLM.
- **VECTOR_INDEX_NAME**: Nome do índice vetorial (namespace) usado pelo provedor de vetores/embedding.
- **EMBEDDER_MODEL**: Nome do modelo de embedding a ser usado (ex.: `paraphrase-multilingual-mpnet-base-v2` ou outro modelo compatível com sentence-transformers/Hugging Face).