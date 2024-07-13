from age_simple_sql import AGESimpleSQL, Vertex, Edge

age = AGESimpleSQL(
    host='localhost',
    password='postgresPW',
    user='postgresUser',
    dbname='postgresDB',
    port=5455,
    logfile='tests/test_logs.log'
)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def create_graph_test():
    test_header = 'CREATE GRAPH'
    age.create_graph('Library')
    result = age.get_graphs()
    if 'Library' in result:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else: 
        test_message = f"ERROR: expected 'Library' in graphs, but got {result}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def drop_graph_test():
    test_header = 'DROP GRAPH'
    age.drop_graph('Library')
    result = age.get_graphs()
    if 'Library' not in result:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else:
        test_message = f"ERROR: expected 'Library' not in graphs, but got {result}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def create_vertex_label_test():
    test_header = 'CREATE VERTEX LABEL'
    age.create_vertex_label('Library', 'Book')
    labels = age.get_labels()
    if 'Book' in labels:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else:
        test_message = f"ERROR: expected 'Book' in labels, but got {labels}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def create_edge_label_test():
    test_header = 'CREATE EDGE LABEL'
    age.create_edge_label('Library', 'WROTE')
    labels = age.get_labels()
    if 'WROTE' in labels:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else:
        test_message = f"ERROR: expected 'WROTE' in labels, but got {labels}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def show_labels_test():
    test_header = 'SHOW LABELS'
    result = age.get_labels()
    if 'Book' and 'WROTE' in result:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else: 
        test_message = f"ERROR: expected 'Book' and 'WROTE' in labels, but got {result}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def drop_label_test():
    test_header = 'DROP LABEL'
    age.drop_label('Library', 'Book')
    labels = age.get_labels()
    if 'Book' not in labels:
        test_message = 'OK'
        color_message = bcolors.OKGREEN
    else:
        test_message = f"Expected 'Book' not in labels, but got {labels}"
        color_message = bcolors.FAIL
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def vertex_creation_test():
    test_header = 'CREATE VERTICES'
    try:
        # Testing without Vertex instance.
        hobbit = Vertex('Book', {'Title': 'The Hobbit', 'Author': 'J.R.R.Tolkien'})
        age.create_vertex('Library', hobbit)
        
        # Testing without properties.
        no_book = Vertex('Book', {})
        age.create_vertex('Library', no_book)

        test_message = 'OK'
        color_message = bcolors.OKGREEN
    
    except Exception:
        test_message = f"Couldn't create vertices correctly."
        color_message = bcolors.FAIL
    
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def edge_creation_test():
    test_header = 'CREATE EDGES'
    try:
        author = Vertex('Author', {'Name': 'Stephen King'})
        book = Vertex('Book', {'Title': 'Life of Chuck'})
        edge = Edge('Wrote', author, book, {})
        age.create_edge('Library', edge)

        test_message = 'OK'
        color_message = bcolors.OKGREEN

    except Exception:
        test_message = f"Couldn't create edges correctly."
        color_message = bcolors.FAIL
    
    print(color_message, test_header, ': ', test_message, bcolors.ENDC)


def execute_tests():
    try:
        print('\n============== AGESimpleSQL UNIT TESTING ==============\n')
        age.setup()

        create_graph_test()
        create_vertex_label_test()
        create_edge_label_test()
        
        show_labels_test()
        show_labels_test()

        vertex_creation_test()

        edge_creation_test()

        drop_label_test()
        drop_graph_test()
        print('\n=======================================================\n')

    except Exception as e:
        print(bcolors.FAIL, f'ERROR: {e}', bcolors.ENDC)

execute_tests()
