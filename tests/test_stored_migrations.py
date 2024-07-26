from randonneur import migrate_edges_with_stored_data


def test_migrate_exchanges_integration():
    given = [
        {
            "edges": [
                {"name": "babur", "unit": "kg", "amount": 42.0},
            ],
        }
    ]
    expected = [
        {
            "edges": [
                {"name": "babur", "unit": "kilogram", "amount": 42.0},
            ],
        }
    ]

    result = migrate_edges_with_stored_data(
        graph=given, label="generic-brightway-units-normalization"
    )
    assert result == expected
