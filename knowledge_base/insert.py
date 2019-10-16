from grakn.client import GraknClient


def insert(graql_insert_query):
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace="banking") as session:
            with session.transaction().write() as transaction:
                transaction.query(graql_insert_query)
                transaction.commit()


if __name__ == "__main__":
    graql_insert_query = """
    insert $b isa bank, has name 'KfW', has country 'Germany', has headquarters 'Frankfurt am Main';
    """

    insert(graql_insert_query)
