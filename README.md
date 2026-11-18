# EleViewer

![GitHub Release](https://img.shields.io/github/v/release/karefined-eng/eleviewer?style=flat-square&color=blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20|%2011-lightgrey?style=flat-square)
![GitHub Downloads](https://img.shields.io/github/downloads/karefined-eng/eleviewer/total?style=flat-square&color=success)
![GitHub License](https://img.shields.io/github/license/karefined-eng/eleviewer?style=flat-square)
![GitHub Repo stars](https://img.shields.io/github/stars/karefined-eng/eleviewer?style=flat-square&color=gold)

**The all-in-one, distraction-free study workspace for Windows.**

EleViewer helps you keep your readings, assignments, slides, and notes together in one place. It is a completely free, offline-first app that runs instantly on Windows 10 and 11 without needing an administrator password or a Microsoft Office subscription.

![EleViewer Workspace](https://eleviewer.vercel.app/hero-screenshot.png)

## Why use EleViewer?

Instead of juggling five different apps and a web browser with 50 open tabs, EleViewer puts everything you need for a study session in one clean window. 

### 🌟 Killer Features

1. **Split-Screen Web Panel**  
   Read your textbook on the left and browse the web on the right. EleViewer includes a built-in web browser right next to your notes, so you can research without getting distracted by YouTube or social media.

2. **Doc↔Doc Split View**  
   View two documents side-by-side with `Ctrl+\`. Compare a draft against a rubric, read two chapters in parallel, or cross-reference notes while reading a PDF.

3. **Vaults & Live Search**  
   Link your school folder as a "Vault". Our background search engine memorizes where everything is so you can instantly find any file just by typing its name.

4. **Session Restore**  
   Accidentally closed the app? Laptop died? No problem. EleViewer automatically remembers exactly what files you had open, what page you were on, and even where you were scrolled.

5. **Persistent Bookmarks**  
   Drop a bookmark (Ctrl+D) on page 400 of a PDF or save a helpful website. Your bookmarks stay pinned to your workspace forever, so you never lose your spot.

6. **PDF Annotations & Highlighting**  
   Highlight passages in yellow, green, or pink. Add sticky notes anchored to page positions. Draw freehand annotations with the pen tool. Annotations save automatically and reload when you reopen the PDF.

7. **Global Quick Note (Alt+E)**  
   Whenever you have a sudden idea, press `Alt+E` from anywhere on your computer. A quick scratchpad will pop up instantly so you can write it down without breaking your flow.

### 📄 Universal File Support

EleViewer opens all your school files locally:
* **PDFs**: Read smoothly, use the Table of Contents sidebar (`Ctrl+Shift+L`), search in-document (`Ctrl+F`), highlight and annotate, and use Read Aloud voice.
* **Word & PowerPoint (.docx, .pptx)**: Open your assignments and slides instantly without paying for Microsoft Office.
* **Excel (.xlsx, .csv)**: View spreadsheets cleanly.
* **Markdown**: Take beautiful, auto-formatting notes with clipboard-aware paste (images and rich text convert automatically).

### ✏️ Editing & Productivity

- **Undo/Redo**: `Ctrl+Z` / `Ctrl+Y` on the main toolbar for all text editors.
- **Print & Export**: Print any document (`Ctrl+P`) or export to PDF via File > Export as PDF.
- **Clipboard Paste**: Copy an image or formatted text from anywhere and paste it into a note with `Ctrl+V`. Images are saved automatically and inserted as Markdown.
- **Keyboard Shortcuts**: `Ctrl+O` open, `Ctrl+S` save, `Ctrl+N` new note, `Ctrl+D` bookmark, `Ctrl+F` find in document, `Alt+V` toggle vault, `F9` read aloud, `Ctrl+\` split view.

## Choose your Windows download

The [latest EleViewer release](https://github.com/karefined-eng/eleviewer/releases/latest) offers two Windows downloads:

- **Setup installer** (`EleViewer_Setup_v<VERSION>.exe`): runs a setup wizard to install EleViewer. The installer is configured to run without administrator rights and can add shortcuts and file associations.
- **Portable archive** (`EleViewer-Portable.zip`): extract the ZIP file and launch `EleViewer.exe` from the extracted folder. This option does not use the setup wizard.

These are separate downloads: the portable version is a ZIP archive, not a standalone `.exe`.

You can also install EleViewer through WinGet:

```powershell
winget install --id karefined-eng.EleViewer
```

## Privacy and internet use

EleViewer is **offline-first for local document work**. Your local document files are not uploaded as part of ordinary document use, and you do not need an account.

- **Local document work:** files opened from your device are handled locally during ordinary use.
- **Internet-required features:** the built-in web panel and network downloads or updates need an internet connection.
- **Optional reports:** feedback or crash reports are sent only when you choose to submit them. 

## Study and comparison guides

Read the [offline study workspace guide](docs/offline-study-workspace.md) for practical workflows using EleViewer for readings, notes, research, and exam preparation. The [feature comparison](docs/compare.md) explains where EleViewer fits alongside dedicated PDF readers, Microsoft Office, and browser-based workspaces.

For questions, workflow ideas, and community feedback, visit [EleViewer Discussions](https://github.com/karefined-eng/eleviewer/discussions). A branded [social-preview asset](assets/social-preview.svg) is also available for articles, release announcements, and community posts.

## For Developers

Want to help build EleViewer or see how it works under the hood? Check out our [Developer Onboarding Guide](DEVELOPER_ONBOARDING.md) for architecture details, our contribution rules, and instructions on how to build the app from the source code.
