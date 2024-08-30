class MappingConstants:
    SIMAPRO_CSV = {
        "expression language": "like JSONPath",
        "labels": {
            "identifier": 'Process[*]."Process identifier".text',
            "name": "Process[*].Products[*].text[0]",
            "platform_id": 'Process[*]."Platform Identifier"',
            "unit": [
                '["Emissions to air/", Process[*]."Emissions to air".[2]]',
                '["Emissions to soil/", Process[*]."Emissions to soil".[2]]',
                '["Emissions to water/", Process[*]."Emissions to water".[2]]',
                '["Resources/", Process[*]."Resources".[2]]',
            ],
            "context": [
                '["Emissions to air/", Process[*]."Emissions to air".[1]]',
                '["Emissions to soil/", Process[*]."Emissions to soil".[1]]',
                '["Emissions to water/", Process[*]."Emissions to water".[1]]',
                '["Resources/", Process[*]."Resources".[1]]',
            ],
        },
    }
    ECOSPOLD2 = {
        "expression language": "XPath",
        "labels": {
            "filename": "concat(//*:activity/@id, '_', //*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/@intermediateExchangeId, '.spold')",
            "name": "//*:activityName/text()",
            "location": "//*:geography/*:shortname/text()",
            "reference product": "//*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/*:name/text()",
            "unit": "//*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/*:unitName/text()",
        },
    }
    ECOSPOLD1_BIO = {
        "expression language": "XPath",
        "labels": {
            "name": "//*:exchange[*:outputGroup = '4' or *:outputGroup = '5']/@name",
            "unit": "//*:exchange[*:outputGroup = '4' or *:outputGroup = '5']/@unit",
            "context": [
                "//*:exchange[*:outputGroup = '4' or *:outputGroup = '5']/@category",
                "//*:exchange[*:outputGroup = '4' or *:outputGroup = '5']/@subCategory",
            ],
        },
    }
    ECOSPOLD2_BIO = {
        "expression language": "XPath",
        "labels": {
            "name": "//*:elementaryExchange/*:name/text()",
            "unit": "//*:elementaryExchange/*:unitName/text()",
            "uuid": "//*:elementaryExchange/@elementaryExchangeId",
            "formula": "//*:elementaryExchange/@formula",
            "context": [
                "//*:elementaryExchange/*:compartment/*:compartment/text()",
                "//*:elementaryExchange/*:compartment/*:subcompartment/text()",
            ],
        },
    }
    ECOSPOLD2_BIO_FLOWMAPPER = {
        "expression language": "XPath",
        "labels": {
            "name": "//*:elementaryExchange/*:name/text()",
            "CAS number": "//*:elementaryExchange/@casNumber",
            "unit": "//*:elementaryExchange/*:unitName/text()",
            "identifier": "//*:elementaryExchange/@elementaryExchangeId",
            "context": [
                "//*:elementaryExchange/*:compartment/*:compartment/text()",
                "//*:elementaryExchange/*:compartment/*:subcompartment/text()",
            ],
        },
    }
