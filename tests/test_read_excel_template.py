from datetime import datetime
from pathlib import Path

import pytest

from randonneur import MappingConstants, read_excel_template
from randonneur.licenses import LICENSES

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture() -> Path:
    return FIXTURES_DIR / "randonneur-matching-template-test-fixture.xlsx"


def test_read_excel_template_default(fixture):
    dp = read_excel_template(fixture)

    expected = [
        {
            "source": {
                "name": r"Electric arc furnace dust {CH}| market for electric arc furnace dust | Cut-off, U",
            },
            "target": {
                "reference product": "electric arc furnace dust",
                "name": "market for electric arc furnace dust",
                "location": "CH",
            },
        },
        {
            "source": {
                "name": r"Electric arc furnace dust {Europe without Switzerland}| market for electric arc furnace dust | Cut-off, U",
            },
            "target": {
                "reference product": "electric arc furnace dust",
                "name": "market for electric arc furnace dust",
                "location": "Europe without Switzerland",
            },
        },
    ]

    assert dp.name == "test_1"
    assert dp.description == "test_description"
    assert dp.contributors == [
        {"title": "Alice", "roles": ["author"], "path": "https://example.com"},
        {"title": "Bob", "roles": ["publisher"], "path": "https://example.com"},
    ]
    assert dp.source_id == "SimaPro-9"
    assert dp.target_id == "ecoinvent-3.10-cutoff"
    assert datetime.fromisoformat(dp.created)
    assert dp.mapping == {
        "source": MappingConstants.SIMAPRO_CSV,
        "target": MappingConstants.ECOSPOLD2,
    }
    assert dp.licenses == [LICENSES["CC-BY-4.0"]]
    assert dp.version == "1"
    assert dp.graph_context == ["edges"]
    assert dp.data["replace"] == expected


def test_read_excel_template_custom_name(fixture):
    dp = read_excel_template(fixture, worksheet="Custom-name")
    assert dp.name == "test-custom-name"


def test_read_excel_template_missing_section(fixture):
    with pytest.raises(ValueError) as excinfo:
        read_excel_template(fixture, worksheet="Missing-section")
        assert "Missing required section Metadata" in str(excinfo.value)


def test_read_excel_template_custom_license(fixture):
    with pytest.raises(KeyError) as excinfo:
        read_excel_template(fixture, worksheet="Custom-license")
        assert "Can't find given license short name" in str(excinfo.value)

    read_excel_template(
        fixture,
        worksheet="Custom-license",
        license_mapping={
            "foo": {
                "name": "bar",
                "path": "https://example.com",
                "title": "Foo bar license",
            }
        },
    )


def test_read_excel_template_wrong_metadata(fixture):
    with pytest.raises(KeyError) as excinfo:
        read_excel_template(fixture, worksheet="Wrong-metadata")
        assert "Can't understand metadata field" in str(excinfo.value)


def test_read_excel_template_wrong_contributors(fixture):
    with pytest.raises(KeyError) as excinfo:
        read_excel_template(fixture, worksheet="Wrong-contributors")
        assert "Can't find given contributor field" in str(excinfo.value)


def test_read_excel_template_wrong_column_index(fixture):
    with pytest.raises(ValueError) as excinfo:
        read_excel_template(fixture, worksheet="Column-offset")
        assert "'Source' must be the first column in data headers" in str(excinfo.value)


def test_read_excel_template_missing_data(fixture):
    with pytest.raises(ValueError) as excinfo:
        read_excel_template(fixture, worksheet="Missing-data")
        assert "No data found" in str(excinfo.value)


def test_read_excel_template_column_label_not_in_mapping(fixture):
    with pytest.raises(ValueError) as excinfo:
        read_excel_template(fixture, worksheet="Not-in-mapping")
        assert "Data label location not defined in" in str(excinfo.value)


def test_read_excel_template_data_headers(fixture):
    with pytest.raises(ValueError) as excinfo:
        read_excel_template(fixture, worksheet="Data-headers")
        assert "Can't find 'Target' in data headers" in str(excinfo.value)
