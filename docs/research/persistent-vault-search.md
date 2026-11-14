# Persistent vault search rationale

EleViewer's core workflow is reading, researching, and capturing notes without
breaking focus. Searching a connected course folder should therefore feel
immediate and predictable rather than restarting a full filesystem walk for
every keystroke.

The new index keeps the search interaction local and lightweight while
preserving progressive disclosure: the dialog still shows filenames and their
folder context, while the implementation stores only metadata needed to find
and open the file. Refreshing the index in the existing worker keeps scanning
off the UI thread, and stale-file removal prevents results from becoming
misleading after course folders change.
