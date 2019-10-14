from grakn.client import GraknClient


def insert(graql_insert_query):
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace="banking") as session:
            with session.transaction().write() as transaction:
                transaction.query(graql_insert_query)
                transaction.commit()


if __name__ == "__main__":
    graql_insert_query = """
    match $p isa bank, has name "KfW"; delete $p;
    """

    insert(graql_insert_query)
