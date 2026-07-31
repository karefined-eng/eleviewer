import unittest
from markdown_utils import preprocess_markdown, convert_latex_expr


class TestMarkdownPreprocessing(unittest.TestCase):

    def test_latex_symbols_and_greeks(self):
        expr = r"\alpha^2 + \beta_1 = \infty"
        conv = convert_latex_expr(expr)
        self.assertIn("α<sup>2</sup>", conv)
        self.assertIn("β<sub>1</sub>", conv)
        self.assertIn("∞", conv)

    def test_strikethrough(self):
        text = "This is ~~deleted~~ text."
        html = preprocess_markdown(text)
        self.assertIn("<del>deleted</del>", html)

    def test_task_lists(self):
        text = "- [ ] Unchecked item\n- [x] Completed item"
        html = preprocess_markdown(text)
        self.assertIn("☐", html)
        self.assertIn("☑", html)

    def test_block_math(self):
        text = "$$\\int_{0}^{\\infty} f(x) dx$$"
        html = preprocess_markdown(text)
        self.assertIn("∫", html)
        self.assertIn("<sub>0</sub>", html)
        self.assertIn("font-family:'Cambria Math'", html)


if __name__ == "__main__":
    unittest.main()
