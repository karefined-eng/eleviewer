import pytest
from auditory_cleaner import clean_for_speech

def test_strip_urls():
    text = "Visit https://google.com for more info."
    assert clean_for_speech(text) == "Visit  for more info."

def test_strip_markdown_links():
    text = "Check out [Google](https://google.com)."
    assert clean_for_speech(text) == "Check out Google."

def test_strip_markdown_formatting():
    text = "# Main Title\n**Bold text** and _italic_ or `code`."
    assert clean_for_speech(text) == "Main Title\nBold text and italic or code."

def test_strip_task_lists():
    text = "- [ ] Unfinished task\n- [x] Finished task\n* Normal list"
    assert clean_for_speech(text) == "Unfinished task\nFinished task\nNormal list"

def test_strip_pdf_page_numbers():
    text = "Some text on page.\n12\nMore text.\nPage 14\nEven more.\nPage 1 of 2\nDone."
    expected = "Some text on page.\n\nMore text.\n\nEven more.\n\nDone."
    assert clean_for_speech(text) == expected

def test_latex_expansion():
    text = "The value of \\sigma and \\alpha."
    assert clean_for_speech(text) == "The value of sigma and alpha."
