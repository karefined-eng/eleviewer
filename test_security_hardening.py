from types import SimpleNamespace

from docx_viewer import DocxViewer
from updater import is_trusted_download_url


def _make_doc(text):
    run = SimpleNamespace(
        _element=SimpleNamespace(findall=lambda pattern: []),
        text=text,
        bold=False,
        italic=False,
        underline=False,
    )
    paragraph = SimpleNamespace(
        style=SimpleNamespace(name="Normal"),
        runs=[run],
    )
    part = SimpleNamespace(rels={})
    return SimpleNamespace(paragraphs=[paragraph], tables=[], part=part)


def test_docx_text_is_escaped_before_html_rendering():
    viewer = DocxViewer.__new__(DocxViewer)
    rendered = viewer._build_html_from_docx(_make_doc("<script>alert(1)</script>"))

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "<script>alert(1)</script>" not in rendered


def test_updater_accepts_only_trusted_https_download_hosts():
    assert is_trusted_download_url(
        "https://github.com/karefined-eng/eleviewer/releases/download/v1.3.0/EleViewer.exe"
    )
    assert is_trusted_download_url(
        "https://release-assets.githubusercontent.com/example.exe"
    )
    assert not is_trusted_download_url("http://github.com/example.exe")
    assert not is_trusted_download_url("https://example.com/example.exe")
    assert not is_trusted_download_url("file:///tmp/example.exe")
