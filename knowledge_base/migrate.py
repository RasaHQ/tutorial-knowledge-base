from grakn.client import GraknClient
import csv


def build_banking_graph(inputs):
        with GraknClient(uri="localhost:48555") as client:
            with client.session(keyspace="banking") as session:
                for input in inputs:
                    print("Loading from [" + input["data_path"] + "] into Grakn ...")
                    load_data_into_grakn(input, session)


def load_data_into_grakn(input, session):
    items = parse_data_to_dictionaries(input)

    for item in items:
        with session.transaction().write() as transaction:
            graql_insert_query = input["template"](item)
            transaction.query(graql_insert_query)
            transaction.commit()

    print(f"Inserted {str(len(items))} items from [{input['data_path']}] into Grakn.")


def bank_template(bank):
    graql_insert_query = "insert $bank isa bank"
    graql_insert_query += ', has name "' + bank["name"] + '"'
    graql_insert_query += ', has headquarters "' + bank["headquarters"] + '"'
    graql_insert_query += ', has country "' + bank["country"] + '"'
    graql_insert_query += ", has free-accounts " + bank["free-accounts"]
    graql_insert_query += (
        ", has english-customer-service " + bank["english-customer-service"]
    )
    graql_insert_query += ", has english-website " + bank["english-website"]
    graql_insert_query += ", has english-mobile-app " + bank["english-mobile-app"]
    graql_insert_query += (
        ", has free-worldwide-withdrawals " + bank["free-worldwide-withdrawals"]
    )
    graql_insert_query += ', has allowed-residents "' + bank["allowed-residents"] + '"'
    graql_insert_query += ";"
    return graql_insert_query


def person_template(person):
    graql_insert_query = "insert $person isa person"
    graql_insert_query += ', has email "' + person["email"] + '"'
    graql_insert_query += ', has first-name "' + person["first-name"] + '"'
    graql_insert_query += ', has last-name "' + person["last-name"] + '"'
    graql_insert_query += ', has city "' + person["city"] + '"'
    graql_insert_query += ', has phone-number "' + person["phone-number"] + '"'
    graql_insert_query += ', has gender "' + person["gender"] + '"'
    graql_insert_query += ";"
    return graql_insert_query


def account_template(account):
    graql_insert_query = "insert $account isa account"
    graql_insert_query += ", has balance " + str(account["balance"])
    graql_insert_query += ', has account-number "' + account["account-number"] + '"'
    graql_insert_query += ', has account-type "' + account["account-type"] + '"'
    graql_insert_query += ", has opening-date " + str(account["opening-date"])
    graql_insert_query += ";"
    return graql_insert_query


def card_template(card):
    graql_insert_query = "insert $card isa card"
    graql_insert_query += ', has name-on-card "' + card["name-on-card"] + '"'
    graql_insert_query += ", has card-number " + card["card-number"]
    graql_insert_query += ", has expiry-date " + card["expiry-date"]
    graql_insert_query += ", has created-date " + card["created-date"]
    graql_insert_query += ";"
    return graql_insert_query


def attribute_mapping_template(mapping):
    graql_insert_query = "insert $mapping isa attribute-mapping"
    graql_insert_query += ", has mapping-key '" + mapping["mapping-key"] + "'"
    graql_insert_query += ", has mapping-value '" + mapping["mapping-value"] + "'"
    graql_insert_query += ";"
    return graql_insert_query


def entity_type_mapping_template(mapping):
    graql_insert_query = "insert $mapping isa entity-type-mapping"
    graql_insert_query += ", has mapping-key '" + mapping["mapping-key"] + "'"
    graql_insert_query += ", has mapping-value '" + mapping["mapping-value"] + "'"
    graql_insert_query += ";"
    return graql_insert_query


def mention_mapping_template(mapping):
    graql_insert_query = "insert $mapping isa mention-mapping"
    graql_insert_query += ", has mapping-key '" + mapping["mapping-key"] + "'"
    graql_insert_query += ", has mapping-value '" + mapping["mapping-value"] + "'"
    graql_insert_query += ";"
    return graql_insert_query


def contract_template(contract):
    graql_insert_query = (
        'match $bank isa bank, has name "' + contract["provider"] + '"; '
    )
    graql_insert_query += (
        ' $customer isa person, has email "' + contract["customer"] + '"; '
    )
    graql_insert_query += (
        ' $account isa account, has account-number "' + contract["offer"] + '"; '
    )
    graql_insert_query += " insert $contract(provider: $bank, customer: $customer, offer: $account) isa contract; "
    graql_insert_query += "$contract has identifier " + str(contract["identifier"]) + "; "
    graql_insert_query += "$contract has sign-date " + contract["sign-date"] + "; "

    return graql_insert_query


def represented_by_template(represented_by):
    graql_insert_query = (
        'match $account isa account, has account-number "'
        + represented_by["bank-account"]
        + '";'
    )
    graql_insert_query += (
        " $card isa card, has card-number " + represented_by["bank-card"] + "; "
    )
    graql_insert_query += " insert $representation(bank-card: $card, bank-account: $account) isa represented-by; "
    graql_insert_query += "$representation has identifier " + represented_by["identifier"] + "; "
    return graql_insert_query


def transaction_template(transaction):
    graql_insert_query = (
        " match $account-of-receiver isa account, has account-number '"
        + transaction["account-of-receiver"]
        + "';"
    )
    graql_insert_query += (
        " $account-of-creator isa account, has account-number '"
        + transaction["account-of-creator"]
        + "';"
    )
    graql_insert_query += (
        "insert $transaction(account-of-receiver: $account-of-receiver, account-of-creator: $account-of-creator) isa transaction; "
        + "$transaction has identifier "
        + str(transaction["identifier"])
        + "; "
        + "$transaction has amount "
        + str(transaction["amount"])
        + "; "
        + "$transaction has reference '"
        + transaction["reference"]
        + "';"
        + "$transaction has category '"
        + transaction["category"]
        + "';"
        + "$transaction has execution-date "
        + transaction["execution-date"]
        + ";"
    )
    return graql_insert_query


def parse_data_to_dictionaries(input):
    items = []
    with open(input["data_path"] + ".csv") as data:  # 1
        for row in csv.DictReader(data, skipinitialspace=True):
            item = {key: value for key, value in row.items()}
            items.append(item)  # 2
    return items


if __name__ == "__main__":
    inputs = [
        {"data_path": "./knowledge_base/data/person", "template": person_template},
        {"data_path": "./knowledge_base/data/account", "template": account_template},
        {"data_path": "./knowledge_base/data/bank", "template": bank_template},
        {"data_path": "./knowledge_base/data/card", "template": card_template},
        {
            "data_path": "./knowledge_base/data/attribute_mapping",
            "template": attribute_mapping_template,
        },
        {
            "data_path": "./knowledge_base/data/mention_mapping",
            "template": mention_mapping_template,
        },
        {
            "data_path": "./knowledge_base/data/entity_type_mapping",
            "template": entity_type_mapping_template,
        },
        {
            "data_path": "./knowledge_base/data/represented-by",
            "template": represented_by_template,
        },
        {
            "data_path": "./knowledge_base/data/transaction",
            "template": transaction_template,
        },
        {"data_path": "./knowledge_base/data/contract", "template": contract_template},
    ]

    build_banking_graph(inputs)
