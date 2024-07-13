"""
A simple SQL wrapper for Apache AGE using psycopg2 connection pooling.

It supports operations such as creating and dropping graphs, creating vertex and edge labels, 
creating vertices and edges, retrieving graph and label information, and creating SQL and
cypher queries.
"""

from psycopg2 import pool
import logging
from .models import Vertex, Edge


# bin/pg_ctl -D demo -l logfile start
# bin/psql demo
# psycopg2-binary


class AGESimpleSQL():
    """
    A class to handle connections and operations with an Apache AGE-enabled PostgreSQL database.
    """

    def __init__(self, user:str, password:str, host:str, 
                 port:int, dbname:str, logfile:str) -> None:
        """
        Initialize the AGESimpleSQL instance with database connection parameters and setup logging.

        Args:
            user (str): The database user.
            password (str): The database password.
            host (str): The database host.
            port (int): The database port.
            dbname (str): The database name.
            logfile (str): The path to the logfile.
        """

        # Database configurations.
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.logfile = logfile

        # Create the log file.
        logging.basicConfig(level=logging.INFO, filename=self.logfile, filemode='w',
                            format="%(asctime)s - %(levelname)s - %(message)s")

        # Initialize the connection pool.
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,  # Min and max connections
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.dbname
            )
            logging.info("Database connection pool created successfully")
        
        except Exception as e:
            logging.exception(f"Error creating connection pool: {e}")

    
    def get_connection(self):
        """
        Get a connection from the connection pool.

        Returns:
            connection: A psycopg2 connection object.
        """
        try:
            connection = self.connection_pool.getconn()
            return connection
        except Exception as e:
            logging.exception(f'Error establishing connection: {e}')

    
    def release_connection(self, conn):
        """
        Release a connection back to the connection pool.

        Args:
            conn: The psycopg2 connection object to release.
        """
        try:
            self.connection_pool.putconn(conn)
        except Exception as e:
            logging.exception(f'Error releasing connection: {e}')

    
    def close_all_connections(self):
        """
        Close all connections in the connection pool.
        """
        try:
            self.connection_pool.closeall()
        except Exception as e:
            logging.exception(f'Error closing all connections: {e}')


    def execute_query(self, query:str, params:tuple = None, fetch:bool = False):
        """
        Execute a SQL query with optional parameters and fetch results if required.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to use in the SQL query. Defaults to None.
            fetch (bool, optional): Whether to fetch and return the results. Defaults to False.

        Returns:
            result: The fetched results if fetch is True, otherwise None.
        """
        conn = self.get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(query, params)
                if fetch:
                    result = cur.fetchall()
                else:
                    conn.commit()
                    result = None
                cur.close()
                self.release_connection(conn)
                logging.info(f"Query executed: {query}")
                return result
            
            except Exception as e:
                logging.exception(f"Error executing `{query}`: {e}")
        
        else:
            logging.exception('Failed to establish a database connection')
        return None
    

    def execute_cypher(self, graph_name:str, cypher_query:str, cypher_return:str):
        query = f"""
        SELECT * FROM cypher('{graph_name}', $$
        {cypher_query}
        $$) AS {cypher_return};
        """
        self.execute_query(query)
    

    def setup(self):
        """
        Sets up the Apache AGE environment for the current database session.

        This function loads the Apache AGE extension and sets the appropriate search paths.
        It should be called immediately after initializing the AGESimpleSQL class instance 
        to enable the execution of openCypher queries.

        Usage:
            agesql = AGESimpleSQL(connection_params)
            agesql.setup()
        """
        query = f"LOAD 'age';"
        self.execute_query(query)

        query = f"SET search_path = ag_catalog, \"$user\", public;"
        self.execute_query(query)
        logging.info(f'AGE has been set up')

    
    def get_graphs(self) -> list:
        """
        Retrieve all graph names from the database.

        Returns:
            list: A list of graph names.
        """
        query = "SELECT * FROM ag_catalog.ag_graph;"
        graphs = self.execute_query(query, fetch=True)
        if graphs:
            graph_names = [graph[1] for graph in graphs]
            logging.info('Retrieval of all graph names has been performed')
            return graph_names
        return []
        
    
    def create_graph(self, graph_name:str):
        """
        Create a new graph in the database.

        Args:
            graph_name (str): The name of the graph to create.
        """
        query = f"SELECT * FROM create_graph(%s);"
        self.execute_query(query, (graph_name,))
        logging.info(f'Graph {graph_name} has been created')
        

    def drop_graph(self, graph_name:str):
        """
        Drop a graph from the database.

        Args:
            graph_name (str): The name of the graph to drop.
        """
        query = f"SELECT * FROM ag_catalog.drop_graph(%s, true);"
        self.execute_query(query, (graph_name,))
        logging.info(f'Graph {graph_name} has been dropped')


    def create_vertex_label(self, graph_name:str, label:str):
        """
        Create a new vertex label in the specified graph.

        Args:
            graph_name (str): The name of the graph.
            label (str): The vertex label to create.
        """
        query = f"SELECT * FROM ag_catalog.create_vlabel(%s, %s);"
        self.execute_query(query, (graph_name, label))
        logging.info(f'Vertex label {graph_name}.{label} has been created')


    def create_edge_label(self, graph_name:str, label:str):
        """
        Create a new edge label in the specified graph.

        Args:
            graph_name (str): The name of the graph.
            label (str): The edge label to create.
        """
        query = f"SELECT * FROM ag_catalog.create_elabel(%s, %s);"
        self.execute_query(query, (graph_name, label))
        logging.info(f'Edge label {graph_name}.{label} has been created')


    def drop_label(self, graph_name:str, label:str):
        """
        Drop a label from the specified graph.

        Args:
            graph_name (str): The name of the graph.
            label (str): The label to drop.
        """
        query = f"SELECT * FROM ag_catalog.drop_label(%s, %s);"
        self.execute_query(query, (graph_name, label))
        logging.info(f'Label {graph_name}.{label} has been dropped')


    def get_labels(self):
        """
        Retrieve all labels from the database.

        Returns:
            list: A list of label names.
        """
        query = "SELECT * FROM ag_catalog.ag_label;"
        labels = self.execute_query(query, fetch=True)
        if labels:
            label_names = [label[0] for label in labels]
            logging.info('Labels have been retrieved')
            return label_names
        return []
    

    # Couldn't make this function work with tuples. It's good to do so because it
    # avoids SQL injections. So, maybe fix this later. 
    def create_vertex(self, graph_name: str, vertex:Vertex):
        """
        Creates a vertex in the specified graph.

        Args:
            graph_name (str): The name of the graph where the vertex will be created.
            vertex (Vertex): The `Vertex` instance.
            
        Returns:
            None

        Example:
            book = Vertex('Book', {'Title': 'Lord of the Rings', 'Author': 'J.R.R.Tolkien'})
            create_vertex('Library', book)
        """
        query = f"""
        CREATE (n:{vertex.label} {vertex.cypher_format_props})
        """
        cypher_return = '(n agtype)'
        self.execute_cypher(graph_name, query, cypher_return)
        

    def create_edge(self, graph_name:str, edge:Edge):
        """
        Creates an edge between two vertices in the specified graph.

        Args:
            graph_name (str): The name of the graph where the edge will be created.
            edge (Edge): The `Edge` instance.

        Returns:
            None

        Example:
            author = Vertex('Author', {'Name': 'Stephen King'})
            book = Vertex('Book', {'Title': 'Life of Chuck'})
            wrote = Edge('WROTE', author, book, {})
            create_edge('Library', wrote)
        """
        # The MERGE clause ensures that if the specified vertices already exist, 
        # they will be reused to create the edge; if not, the vertices will be 
        # created first before the edge is created.
        query = f"""
        MERGE (a:{edge.from_vertex.label} {edge.from_vertex.cypher_format_props})
        MERGE (b:{edge.to_vertex.label} {edge.to_vertex.cypher_format_props})
        CREATE (a)-[e:{edge.label} {edge.cypher_format_props}]->(b)
        """
        cypher_return = '(n agtype)'
        self.execute_cypher(graph_name, query, cypher_return)


