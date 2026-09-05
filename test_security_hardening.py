from types import SimpleNamespace

from docx_viewer import DocxViewer
from updater import is_trusted_download_url, DownloadThread
import hashlib


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

def test_updater_hash_verification_failure(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.headers = {'Content-Length': str(len(content))}
        def read(self, block_size):
            res = self.content
            self.content = b""
            return res
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_urlopen(req, *args, **kwargs):
        return MockResponse(b"dummy executable content")

    monkeypatch.setattr("updater.urllib.request.urlopen", mock_urlopen)
    
    wrong_hash = hashlib.sha256(b"wrong content").hexdigest()
    thread = DownloadThread("https://github.com/karefined-eng/eleviewer/releases/download/v1.3.0/EleViewer.exe", wrong_hash)
    
    failed_emitted = []
    thread.failed.connect(lambda msg: failed_emitted.append(msg))
    
    thread.run()
    
    assert len(failed_emitted) == 1
    assert "Security Error" in failed_emitted[0]
    assert "does not match expected hash" in failed_emitted[0]

def test_updater_hash_verification_success(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.headers = {'Content-Length': str(len(content))}
        def read(self, block_size):
            res = self.content
            self.content = b""
            return res
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def mock_urlopen(req, *args, **kwargs):
        return MockResponse(b"dummy executable content")

    monkeypatch.setattr("updater.urllib.request.urlopen", mock_urlopen)
    
    correct_hash = hashlib.sha256(b"dummy executable content").hexdigest()
    thread = DownloadThread("https://github.com/karefined-eng/eleviewer/releases/download/v1.3.0/EleViewer.exe", correct_hash)
    
    finished_emitted = []
    thread.finished.connect(lambda path: finished_emitted.append(path))
    
    thread.run()
    
    assert len(finished_emitted) == 1
