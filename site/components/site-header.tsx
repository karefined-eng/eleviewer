import Link from "next/link"
import { Github, Download } from "lucide-react"
import { Logo } from "./logo"
import { GITHUB_URL, RELEASES_URL } from "@/lib/links"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-5">
        <Link href="/" aria-label="EleViewer home">
          <Logo />
        </Link>
        <nav
          aria-label="Main navigation"
          className="hidden items-center gap-6 text-[13px] text-muted-foreground md:flex"
        >
          <a href="#features" className="transition-colors hover:text-foreground">
            Features
          </a>
          <a href="#shortcuts" className="transition-colors hover:text-foreground">
            Shortcuts
          </a>
          <a
            href="#open-source"
            className="transition-colors hover:text-foreground"
          >
            Open Source
          </a>
        </nav>
        <div className="flex items-center gap-2">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-panel hover:text-foreground"
            aria-label="EleViewer on GitHub"
          >
            <Github className="h-4 w-4" />
          </a>
          <a
            href={RELEASES_URL}
            target="_blank"
            rel="noreferrer"
            className="flex h-8 items-center gap-1.5 rounded-md bg-primary px-3 text-[13px] font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Download className="h-3.5 w-3.5" />
            Download
          </a>
        </div>
      </div>
    </header>
  )
}
