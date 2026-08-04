import unittest
from PySide6.QtWidgets import QApplication
from markdown_renderer import MarkdownViewer
from markdown_utils import preprocess_markdown, convert_latex_expr


class TestMarkdownPreprocessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

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

    def test_preview_cache_reuses_rendered_html(self):
        viewer = MarkdownViewer(file_path=None, is_html=False)
        sample_text = "# Heading\n\nThis is a preview."
        calls = []
        original_render = viewer._render_markdown

        def counting_render(text):
            calls.append(text)
            return original_render(text)

        viewer._render_markdown = counting_render
        viewer._render_preview_text(sample_text)
        viewer._render_preview_text(sample_text)

        self.assertEqual(len(calls), 1)
        self.assertIn("<html>", viewer.viewer.toHtml())


if __name__ == "__main__":
    unittest.main()
