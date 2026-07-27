

from dataclasses import FrozenInstanceError
import unittest

from framework.context import EPContext


class EPContextTestCase(unittest.TestCase):
    """Tests de EPContext."""

    def test_create_context(self):
        """Un contexte est créé avec les valeurs fournies."""

        context = EPContext(
            operator="operator",
            client_environment="environment",
            company="company",
            project="project",
        )

        self.assertEqual(context.operator, "operator")
        self.assertEqual(context.client_environment, "environment")
        self.assertEqual(context.company, "company")
        self.assertEqual(context.project, "project")

    def test_context_without_company(self):
        """Le contexte accepte une société absente."""

        context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        self.assertIsNone(context.company)
        self.assertIsNone(context.project)

    def test_context_without_project(self):
        """Le contexte accepte un projet absent."""

        context = EPContext(
            operator="operator",
            client_environment="environment",
            company="company",
        )

        self.assertEqual(context.company, "company")
        self.assertIsNone(context.project)

    def test_context_is_immutable(self):
        """EPContext est immuable."""

        context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        with self.assertRaises(FrozenInstanceError):
            context.operator = "new_operator"

    def test_context_uses_slots(self):
        """Aucun nouvel attribut ne peut être ajouté."""

        context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        with self.assertRaises(
            (AttributeError, TypeError, FrozenInstanceError)
        ):
            context.new_attribute = "value"


if __name__ == "__main__":
    unittest.main()