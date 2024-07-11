"""
A simple SQL wrapper for Apache AGE using psycopg2 connection pooling.

It supports operations such as creating and dropping graphs, creating vertex and edge labels, 
creating vertices and edges, retrieving graph and label information, and creating SQL and
cypher queries.
"""

from psycopg2 import pool
import logging
from .models import Vertex, Edge
from .utils import format_properties


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
    

    def setup(self):
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
    def create_vertex(self, graph_name: str, label_or_vertex, properties: dict = None):
        """
        Creates a vertex in the specified graph.

        This function handles two types of inputs for the label or vertex:
        1. If `label_or_vertex` is an instance of `Vertex`, it extracts the label and properties
        from the provided `Vertex` instance.
        2. If `label_or_vertex` is a string, it uses the string as the label and uses the provided
        properties dictionary.

        Args:
            graph_name (str): The name of the graph where the vertex will be created.
            label_or_vertex (str or Vertex): The label of the vertex or a `Vertex` instance.
            properties (dict, optional): A dictionary of properties for the vertex. Defaults to None.

        Returns:
            None

        Example:
            create_vertex('my_graph', 'Person', {'name': 'Alice', 'age': 30})
            create_vertex('my_graph', Vertex('Person', {'name': 'Bob', 'age': 25}))
        """

        if isinstance(label_or_vertex, Vertex):
            # If label_or_vertex is a Vertex instance, extract label and properties
            # from it.
            vertex = label_or_vertex
            label = vertex.label
            format_props = format_properties(vertex.properties) if bool(vertex.properties) else {}
        
        else:
            # If label_or_vertex is a string, use it as the label and use provided
            # properties.
            label = label_or_vertex
            format_props = format_properties(properties) if bool(properties) else {}


        query = f"""
        SELECT * FROM cypher('{graph_name}', $$
        CREATE (n:{label} {format_props})
        $$) as (n agtype);
        """
        self.execute_query(query)
        

    def create_edge(self, graph_name:str, label_or_edge, properties:dict = None, 
                    from_vertex:Vertex = None, to_vertex:Vertex = None):
        """
        Creates an edge between two vertices in the specified graph.

        This function handles two types of inputs for the label or edge:
        1. If `label_or_edge` is an instance of `Edge`, it extracts the label, properties, and 
        the from/to vertices from the provided `Edge` instance.
        2. If `label_or_edge` is a string, it uses the string as the label and uses the provided
        properties dictionary along with the provided from/to vertices.

        Args:
            graph_name (str): The name of the graph where the edge will be created.
            label_or_edge (str or Edge): The label of the edge or an `Edge` instance.
            properties (dict, optional): A dictionary of properties for the edge. Defaults to None.
            from_vertex (Vertex, optional): The source vertex for the edge. Required if `label_or_edge` is a string.
            to_vertex (Vertex, optional): The target vertex for the edge. Required if `label_or_edge` is a string.

        Returns:
            None

        Example:
            create_edge('my_graph', 'KNOWS', {'since': 2020}, from_vertex=Vertex('Person', {'name': 'Alice'}), to_vertex=Vertex('Person', {'name': 'Bob'}))
            create_edge('my_graph', Edge('KNOWS', {'since': 2020}, from_vertex=Vertex('Person', {'name': 'Alice'}), to_vertex=Vertex('Person', {'name': 'Bob'})))
        """
        
        if isinstance(label_or_edge, Edge):
            # If label_or_edge is an Edge instance, extract label and properties
            # from it.
            e_label = label_or_edge.label

            e_props = format_properties(label_or_edge.properties) if bool(label_or_edge.properties) else {}
            f_v_props = format_properties(label_or_edge.from_vertex.properties) if bool(label_or_edge.from_vertex.properties) else {}
            t_v_props = format_properties(label_or_edge.to_vertex.properties) if bool(label_or_edge.to_vertex.properties) else {}

            f_v_label = label_or_edge.from_vertex.label
            t_v_label = label_or_edge.to_vertex.label
        
        else:
            # If label_or_edge is a string, use it as the label and use provided
            # properties.
            e_label = label_or_edge

            e_props = format_properties(properties) if bool(properties) else {}
            f_v_props = format_properties(from_vertex.properties) if bool(from_vertex.properties) else {}
            t_v_props = format_properties(to_vertex.properties) if bool(to_vertex.properties) else {}

            f_v_label = from_vertex.label
            t_v_label = to_vertex.label

        # The MERGE clause ensures that if the specified vertices already exist, 
        # they will be reused to create the edge; if not, the vertices will be 
        # created first before the edge is created.
        query = f"""
        SELECT * FROM cypher('{graph_name}', $$
        MERGE (a:{f_v_label} {f_v_props})
        MERGE (b:{t_v_label} {t_v_props})
        CREATE (a)-[e:{e_label} {e_props}]->(b)
        $$) as (n agtype);
        """
        self.execute_query(query)


