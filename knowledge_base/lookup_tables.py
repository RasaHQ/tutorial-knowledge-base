import os
from grakn.client import GraknClient


KEYSPACE = "banking"
URI = "localhost:48555"


def execute_entity_query(query):
    with  GraknClient(uri=URI) as client:
        with client.session(keyspace=KEYSPACE) as session:
           with session.transaction().read() as read_transaction:
                result = read_transaction.query(query)

                concepts = result.collect_concepts()

                entities = []

                for c in concepts:
                    attrs = c.attributes()
                    entity = {"id": c.id}
                    for each in attrs:
                        entity[each.type().label()] = each.value()
                    entities.append(entity)

                return entities


def get_entities(entity_type):
    return execute_entity_query(f"match $x isa {entity_type}; get;")


def write_to_file(file_name, entities):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w+", encoding="utf-8") as f:
        for e in entities:
            f.write(f"{e}\n")


def run():  

    entities = get_entities("person")
    people = list(map(lambda x: x["first-name"] + " " + x["last-name"], entities))
    people = people + list(map(lambda x: x["first-name"], entities))
    write_to_file("lookup_person.txt", set(people))

    entities = get_entities("bank")
    bank = list(map(lambda x: x["name"], entities))
    write_to_file("lookup_bank.txt", set(bank))


if __name__ == "__main__":
    run()
