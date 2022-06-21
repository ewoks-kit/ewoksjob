def test_workflow():
    return {
        "graph": {"id": "sleepgraph", "schema_version": "1.0"},
        "nodes": [
            {
                "id": "sleepnode",
                "task_type": "method",
                "task_identifier": "time.sleep",
                "default_inputs": [{"name": 0, "value": 0}],
            },
            {
                "id": "checknode",
                "task_type": "method",
                "task_identifier": "operator.eq",
                "default_inputs": [{"name": 0, "value": None}],
            },
        ],
        "links": [
            {
                "source": "sleepnode",
                "target": "checknode",
                "data_mapping": [{"target_input": 1, "source_output": "return_value"}],
            },
        ],
    }
