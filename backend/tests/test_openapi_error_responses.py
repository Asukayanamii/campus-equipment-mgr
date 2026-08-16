import unittest

from app.core.openapi import ERROR_RESPONSES
from app.main import app


class OpenApiErrorResponseTests(unittest.TestCase):
    def test_every_operation_references_the_common_error_model(self):
        app.openapi_schema = None
        schema = app.openapi()

        self.assertIn("ErrorResult", schema["components"]["schemas"])
        expected_reference = {"$ref": "#/components/schemas/ErrorResult"}

        for path, path_item in schema["paths"].items():
            for method, operation in path_item.items():
                if method not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                    continue
                for status_code in ERROR_RESPONSES:
                    with self.subTest(path=path, method=method, status_code=status_code):
                        response = operation["responses"][status_code]
                        self.assertEqual(
                            response["content"]["application/json"]["schema"],
                            expected_reference,
                        )
                        self.assertIn("example", response["content"]["application/json"])

    def test_validation_error_uses_the_unified_result_shape(self):
        app.openapi_schema = None
        schema = app.openapi()
        response = schema["paths"]["/user/equipment/{equipmentId}"]["get"]["responses"]["422"]

        self.assertEqual(response["description"], ERROR_RESPONSES["422"]["description"])
        self.assertEqual(response["content"]["application/json"]["example"]["code"], 1)


if __name__ == "__main__":
    unittest.main()
