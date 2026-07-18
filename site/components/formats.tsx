const formats = [
  { ext: ".docx", label: "Word documents" },
  { ext: ".xlsx", label: "Excel spreadsheets" },
  { ext: ".pdf", label: "PDFs with read-aloud" },
  { ext: ".md", label: "Markdown notes" },
  { ext: ".txt", label: "Plain text" },
]

export function Formats() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-16 sm:py-24">
      <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-5">
        {formats.map((f) => (
          <div
            key={f.ext}
            className="flex flex-col items-center gap-1.5 bg-panel px-4 py-6 text-center"
          >
            <span className="font-mono text-lg font-semibold text-accent">
              {f.ext}
            </span>
            <span className="text-xs text-muted-foreground">{f.label}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
