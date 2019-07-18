schema = {
    "transaction": {
        "attributes": ["category", "execution-date", "amount", "reference"],
        "key": "identifier",
        "representation": [
            "execution-date",
            "reference",
            "account-of-receiver.account-number",
            "amount",
        ],
    },
    "contract": {"attributes": ["sign-date"], "key": "identifier", "representation": ["identifier"]},
    "account": {
        "attributes": ["balance", "account-type", "opening-date", "account-number"],
        "key": "account-number",
        "representation": ["provider.name", "account-number", "account-type"],
    },
    "bank": {
        "attributes": [
            "name",
            "headquarters",
            "country",
            "english-website",
            "english-mobile-app",
            "allowed-residents",
            "free-accounts",
            "free-worldwide-withdrawals",
            "english-customer-service",
        ],
        "key": "name",
        "representation": ["name"],
    },
    "person": {
        "attributes": [
            "email",
            "last-name",
            "first-name",
            "gender",
            "phone-number",
            "city",
        ],
        "key": "email",
        "representation": ["first-name", "last-name"],
    },
    "card": {
        "attributes": ["name-on-card", "expiry-date", "created-date", "card-number"],
        "key": "card-number",
        "representation": ["name-on-card", "card-number"],
    },
}
