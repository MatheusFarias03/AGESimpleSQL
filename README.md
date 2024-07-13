# AGESimpleSQL
AGESimpleSQL is a simple SQL wrapper for Apache AGE using `psycopg2` [connection pooling](https://www.psycopg.org/psycopg3/docs/advanced/pool.html). It supports operations such as creating and dropping graphs, creating vertex and edge labels, creating vertices and edges, retrieving graph and label information, and executing SQL and Cypher queries. It is not the official driver for Apache AGE.

[Apache AGE](https://age.apache.org/) is a PostgreSQL extension that provides graph database functionality. The goal of the Apache AGE project is to create single storage that can handle both relational and graph model data so that users can use standard ANSI SQL along with openCypher, the Graph query language.


## Usage
```python
from age_simple_sql import AGESimpleSQL
from age_simple_sql.models import Vertex

# Initialize the AGESimpleSQL instance
db = AGESimpleSQL(
    user="your_db_user",
    password="your_db_password",
    host="your_db_host",
    port=your_db_port,
    dbname="your_db_name",
    logfile="path/to/your/logfile.log"
)

# Call setup to load the AGE extension commands
db.setup()

# Example usage
db.create_graph("TestGraph")
db.create_vertex_label("TestGraph", "Book")
book = Vertex(label="Book", properties={"Title": "The Hobbit"})
db.create_vertex("TestGraph", vertex)

author = Vertex(label="Author", properties={"Name": "J.R.R.Tolkien"})
wrote = Edge(label="WROTE", from_vertex=author, to_vertex=book)
db.create_edge("TestGraph", wrote)
```

## Testing
This repo contains the `tests` folder, which includes a bash script, a python script, and the log file of the test. Executing the bash script will pull the apache/age docker image and run it on the background. Then, it is going to call the python test script and execute it. Finally, it stops and removes the container.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss what you would like to change.

## For more information about Apache AGE
* Apache Age Website: https://age.apache.org/
* Github: https://github.com/apache/age
* Documentation: https://age.apache.org/age-manual/master/index.html

## License
[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0)