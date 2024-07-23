class MappingConstants:
    SIMAPRO_CSV = {
        "expression language": "like JSONPath",
        "labels": {
            "identifier": 'Process[*]."Process identifier".text',
            "name": "Process[*].Products[*].text[0]",
            "platform_id": 'Process[*]."Platform Identifier"',
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
    ECOSPOLD2_BIO = {
        "expression language": "XPath",
        "labels": {
            "name": "//*:elementaryExchange/*:name/text()",
            "unit": "//*:elementaryExchange/*:unitName/text()",
            "uuid": "//*:elementaryExchange/@elementaryExchangeId",
        },
    }
