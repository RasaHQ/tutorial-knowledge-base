import os

import grakn


KEYSPACE = "banking"
URI = "localhost:48555"


def execute_entity_query(query, grakn_client):
    with grakn_client.session(keyspace=KEYSPACE) as session:
        with session.transaction(grakn.TxType.READ) as tx:
            result = tx.query(query)

            concepts = result.collect_concepts()

            entities = []

            for c in concepts:
                attrs = c.attributes()
                entity = {"id": c.id}
                for each in attrs:
                    entity[each.type().label()] = each.value()
                entities.append(entity)

            return entities


def get_entities(entity_type, grakn_client):
    return execute_entity_query(f"match $x isa {entity_type}; get;", grakn_client)


def write_to_file(file_name, entities):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w+", encoding="utf-8") as f:
        for e in entities:
            f.write(f"{e}\n")


def run():
    grakn_client = grakn.Grakn(uri=URI)

    entities = get_entities("person", grakn_client)
    people = list(map(lambda x: x["first-name"] + " " + x["last-name"], entities))
    people = people + list(map(lambda x: x["first-name"], entities))
    write_to_file("lookup_person.txt", set(people))

    entities = get_entities("bank", grakn_client)
    bank = list(map(lambda x: x["name"], entities))
    write_to_file("lookup_bank.txt", set(bank))


if __name__ == "__main__":
    run()
