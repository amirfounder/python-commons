"""
ModelSchema: {
    "Recruiter": {
        "type": "Recruiter",
        "properties": {
            "name": {
                "type": "int",
                "default": null
            },
            "age": {
                "type": "int",
                "default": null
            },
            "touchpoints": {
                "type": "dict",
                "default": {},
                "key: {
                    "type": "str"
                },
                "value": {
                    "type": TouchPoint,
                    "is_model": true
                }
            }
        }
    },
    "TouchPoint": {
        "type": "TouchPoint",
        "properties": {
            "contact": {

            }
        }
    }
}
"""