import { Download, Github } from "lucide-react"
import { AppMockup } from "./app-mockup"
import { GITHUB_URL, RELEASES_URL } from "@/lib/links"

export function Hero() {
  return (
    <section className="mx-auto max-w-5xl px-5 pt-16 sm:pt-24">
      <div className="mx-auto max-w-2xl text-center">
        <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-border bg-panel px-3 py-1 font-mono text-[11px] text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          Free &amp; open source · Windows 10/11
        </p>
        <h1 className="text-balance text-4xl font-semibold tracking-tight text-foreground sm:text-5xl">
          Every file your professor throws at you. One free app.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-pretty text-[15px] leading-relaxed text-muted-foreground">
          EleViewer opens and edits DOCX, XLSX, PDF, Markdown, and TXT in one
          lightweight study workspace — with text-to-speech for PDFs, a file
          vault, and session restore. 16 MB. No install. No account. No cost.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a
            href={RELEASES_URL}
            target="_blank"
            rel="noreferrer"
            className="flex h-11 items-center gap-2 rounded-lg bg-primary px-6 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Download className="h-4 w-4" />
            Download for Windows
          </a>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="flex h-11 items-center gap-2 rounded-lg border border-border bg-panel px-6 text-sm font-medium text-foreground transition-colors hover:bg-panel-2"
          >
            <Github className="h-4 w-4" />
            View on GitHub
          </a>
        </div>
        <p className="mt-4 font-mono text-[11px] text-muted-foreground">
          MIT licensed · portable .exe · no telemetry
        </p>
      </div>

      <div className="mt-14 sm:mt-20">
        <AppMockup />
      </div>
    </section>
  )
}
