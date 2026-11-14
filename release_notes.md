# EleViewer v1.3.7: Faster loading and safer study sessions

EleViewer v1.3.7 improves the everyday study loop: files open without blocking
the window, vault search stays fast after the first scan, and two fragile startup
paths now fail gracefully.

## What’s improved

- **Vault search:** A persistent local filename index makes repeated course-folder
  searches faster while removing entries for files that no longer exist.
- **Document loading:** DOCX, PPTX, and XLSX parsing now runs in the background
  through the normal file-opening path, keeping the interface responsive.
- **Web Panel:** A temporary Windows file lock or startup problem no longer crashes EleViewer. The app now keeps running and explains when the browser panel needs to be tried again.
- **Read Aloud:** Reading can fall back to Windows’ built-in voice when the usual offline speech engine cannot start.

This update keeps your files local and does not change the app’s offline-first workflow.

---
*Have a suggestion? Share it on our [GitHub Issues page](https://github.com/karefined-eng/eleviewer/issues).*
