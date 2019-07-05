import logging
import random
from typing import List, Dict, Any, Optional, Text

import grakn

logger = logging.getLogger(__name__)


class GraphDatabase:
    def __init__(self, uri: Text = "localhost:48555", keyspace: Text = "banking"):
        self.client = grakn.Grakn(uri=uri)
        self.keyspace = keyspace
        self.me = "mitchell.gillis@t-online.de"

    def _thing_to_dict(self, thing):
        """
        Converts a thing (a grakn object) to a dict for easy retrieval of the thing's
        attributes.
        """
        entity = {"id": thing.id, "type": thing.type().label()}
        for each in thing.attributes():
            entity[each.type().label()] = each.value()
        return entity

    def _execute_entity_query(self, query: Text) -> List[Dict[Text, Any]]:
        """
        Executes a query that returns a list of entities with all their attributes.
        """
        with self.client.session(keyspace=self.keyspace) as session:
            with session.transaction(grakn.TxType.READ) as tx:
                logger.debug("Executing Graql Query: " + query)
                result_iter = tx.query(query)
                concepts = result_iter.collect_concepts()
                entities = []
                for c in concepts:
                    entities.append(self._thing_to_dict(c))
                return entities

    def _execute_attribute_query(self, query: Text) -> List[Any]:
        """
        Executes a query that returns the value(s) an entity has for a specific
        attribute.
        """
        with self.client.session(keyspace=self.keyspace) as session:
            with session.transaction(grakn.TxType.READ) as tx:
                print("Executing Graql Query: " + query)
                result_iter = tx.query(query)
                concepts = result_iter.collect_concepts()
                return [c.value() for c in concepts]

    def _execute_relation_query(
        self, query: Text, relation_name: Text
    ) -> List[Dict[Text, Any]]:
        """
        Execute a query that queries for a relation. All attributes of the relation and
        all entities participating in the relation are part of the result.
        """
        with self.client.session(keyspace=self.keyspace) as session:
            with session.transaction(grakn.TxType.READ) as tx:
                print("Executing Graql Query: " + query)
                result_iter = tx.query(query)

                relations = []

                for concept in result_iter:
                    relation_entity = concept.map().get(relation_name)
                    relation = self._thing_to_dict(relation_entity)

                    for (
                        role_entity,
                        entity_set,
                    ) in relation_entity.role_players_map().items():
                        role_label = role_entity.label()
                        thing = entity_set.pop()
                        relation[role_label] = self._thing_to_dict(thing)

                    relations.append(relation)

                return relations

    def _get_me_clause(self, entity_type: Text) -> Text:
        """
        Construct the me clause. Needed to only list, for example, accounts that are
        related to me.

        :param entity_type: entity type

        :return: me clause as string
        """

        clause = ""

        # do not add the me clause to a query asking for banks or people as they are
        # independent of the accounts related to me
        if entity_type not in ["person", "bank"]:
            clause = (
                f"$person isa person, has email '{self.me}';"
                f"$contract(customer: $person, offer: $account, provider: $bank) isa contract;"
            )
        return clause

    def _get_attribute_clause(
        self, attributes: Optional[List[Dict[Text, Text]]] = None
    ) -> Text:
        """
        Construct the attribute clause.

        :param attributes: attributes

        :return: attribute clause as string
        """

        clause = ""

        if attributes:
            clause = ",".join([f"has {a['key']} '{a['value']}'" for a in attributes])
            clause = ", " + clause

        return clause

    def get_attribute_of(
        self, entity_type: Text, key_attribute: Text, entity: Text, attribute: Text
    ) -> List[Any]:
        """
        Get the value of the given attribute for the provided entity.

        :param entity_type: entity type
        :param key_attribute: key attribute of entity
        :param entity: name of the entity
        :param attribute: attribute of interest

        :return: the value of the attribute
        """
        me_clause = self._get_me_clause(entity_type)

        return self._execute_attribute_query(
            f"""
              match 
                {me_clause}
                ${entity_type} isa {entity_type}, has {key_attribute} '{entity}', has {attribute} $a; 
              get $a;
            """
        )

    def _get_transaction_entities(
        self, attributes: Optional[List[Dict[Text, Text]]] = None, limit: int = 5
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for transactions. Restrict the transactions
        by the provided attributes, if any attributes are given.
        As transaction is a relation, query also the related account entities.

        :param attributes: list of attributes
        :param limit: maximum number of transactions to return

        :return: list of transactions
        """

        attribute_clause = self._get_attribute_clause(attributes)
        me_clause = self._get_me_clause("transaction")

        return self._execute_relation_query(
            f"match"
            f"{me_clause}"
            f"$transaction(account-of-receiver: $x, account-of-creator: $account) "
            f"isa transaction{attribute_clause}; "
            f"get $transaction;",
            "transaction",
        )[:limit]

    def _get_account_entities(
        self, attributes: Optional[List[Dict[Text, Text]]] = None, limit: int = 5
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for accounts. Restrict the accounts
        by the provided attributes, if any attributes are given.
        Query the related relation contract, to obtain additional information
        about the bank and the person who owns the account.

        :param attributes: list of attributes
        :param limit: maximum number of accounts to return

        :return: list of accounts
        """

        attribute_clause = self._get_attribute_clause(attributes)
        me_clause = self._get_me_clause("account")

        entities = self._execute_relation_query(
            f"""
                match
                $account isa account{attribute_clause};
                {me_clause}
                get $contract;
            """,
            "contract",
        )[:limit]

        for entity in entities:
            for k, v in entity["offer"].items():
                entity[k] = v
            entity.pop("offer")

        return entities

    def get_entities(
        self,
        entity_type: Text,
        attributes: Optional[List[Dict[Text, Text]]] = None,
        limit: int = 5,
    ) -> List[Dict[Text, Any]]:
        """
        Query the graph database for entities of the given type. Restrict the entities
        by the provided attributes, if any attributes are given.

        :param entity_type: the entity type
        :param attributes: list of attributes
        :param limit: maximum number of entities to return

        :return: list of entities
        """

        if entity_type == "transaction":
            return self._get_transaction_entities(attributes, limit)
        if entity_type == "account":
            return self._get_account_entities(attributes, limit)

        me_clause = self._get_me_clause(entity_type)
        attribute_clause = self._get_attribute_clause(attributes)

        return self._execute_entity_query(
            f"match "
            f"{me_clause}"
            f"${entity_type} isa {entity_type}{attribute_clause}; "
            f"get ${entity_type};"
        )[:limit]

    def lookup(self, lookup_type: Text, lookup_key: Text):
        """
        Query the given lookup table for the provided lookup key.

        :param lookup_type: the name of the lookup table
        :param lookup_key: the lookup key

        :return: the lookup value
        """

        value = self._execute_attribute_query(
            f"match "
            f"$lookup isa {lookup_type}, "
            f"has lookup-key '{lookup_key}', "
            f"has lookup-value $v;"
            f"get $v;"
        )

        if value and len(value) == 1:
            return value[0]
