

import unittest

from framework.button import ButtonAction


class ButtonActionTests(unittest.TestCase):

    def test_values(self):
        self.assertEqual(
            ButtonAction.EXECUTE.value,
            "execute",
        )

        self.assertEqual(
            ButtonAction.CANCEL.value,
            "cancel",
        )

        self.assertEqual(
            ButtonAction.DANGER.value,
            "danger",
        )


if __name__ == "__main__":
    unittest.main()