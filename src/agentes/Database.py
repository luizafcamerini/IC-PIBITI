from neo4j import GraphDatabase
from typing import Optional

class Database():
    '''Classe que representa o banco de dados Neo4j e suas conexoes.'''
    def __init__(self, uri:str, username:str, password:str, databse:Optional[str] = 'neo4j'):
        '''Construtor do Database.
        
        Recebe:
            uri: str; URI de conexao do banco.
            username: str; Nome de usuario de conexao.
            password: str; Senha de conexao.
        '''
        self.__uri = uri
        self.__username = username
        self.__password = password
        self.__database = databse
        self.driver = self.init_driver()
        
    def init_driver(self) -> GraphDatabase.driver:
        '''Funcao que conecta ao banco do Neo4J e 
        verifica se a conexao foi bem sucedida.
        '''
        try:
            driver = GraphDatabase().driver(str(self.__uri), auth=(self.__username, self.__password), database=self.__database)
            driver.verify_connectivity()
            print("Conexao ao Neo4j realizada com sucesso.")
        except Exception as e:
            print("Erro ao conectar ao Neo4j: ", e)
            raise e
        return driver

    def close_driver(self) -> None:
        '''Funcao que fecha a conexao ao banco do Neo4j.'''
        self.driver.close()
        print("Conexao fechada com sucesso.")