"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { Download, X, ExternalLink } from "lucide-react"
import { Logo } from "./logo"
import { GitHubIcon } from "./github-icon"
import { MenuIcon } from "./menu-icon"
import { GITHUB_URL, RELEASES_URL } from "@/lib/links"

export function SiteHeader() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  useEffect(() => {
    if (isMenuOpen) {
      document.body.classList.add("no-scroll")
    } else {
      document.body.classList.remove("no-scroll")
    }
  }, [isMenuOpen])

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
          <a
            href="#features"
            className="transition-colors hover:text-foreground"
          >
            Features
          </a>
          <a
            href="#shortcuts"
            className="transition-colors hover:text-foreground"
          >
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
            className="flex h-8 items-center gap-1.5 rounded-md text-muted-foreground transition-colors hover:bg-panel hover:text-foreground"
            aria-label="EleViewer on GitHub"
          >
            <GitHubIcon className="h-4 w-4" />
            <ExternalLink className="ml-1 h-3 w-3" />
          </a>
          <a
            href={RELEASES_URL}
            target="_blank"
            rel="noreferrer"
            className="flex h-8 items-center gap-1.5 rounded-md bg-primary px-3 text-[13px] font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Download className="h-3.5 w-3.5" />
            Download <ExternalLink className="ml-1 h-3 w-3" />
          </a>
          <button
            type="button"
            className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-panel hover:text-foreground md:hidden"
            onClick={() => setIsMenuOpen(true)}
            aria-label="Open menu"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
      {isMenuOpen && (
        <div className="fixed inset-0 z-50 bg-background/95 backdrop-blur-md">
          <div className="mx-auto max-w-5xl px-5">
            <div className="flex h-14 items-center justify-between">
              <Link
                href="/"
                aria-label="EleViewer home"
                onClick={() => setIsMenuOpen(false)}
              >
                <Logo />
              </Link>
              <button
                type="button"
                className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground"
                onClick={() => setIsMenuOpen(false)}
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <nav
              aria-label="Mobile navigation"
              className="mt-8 flex flex-col items-center gap-6 text-center text-lg font-medium"
            >
              <a
                href="#features"
                className="w-full rounded-md p-3 transition-colors hover:bg-panel"
                onClick={() => setIsMenuOpen(false)}
              >
                Features
              </a>
              <a
                href="#shortcuts"
                className="w-full rounded-md p-3 transition-colors hover:bg-panel"
                onClick={() => setIsMenuOpen(false)}
              >
                Shortcuts
              </a>
              <a
                href="#open-source"
                className="w-full rounded-md p-3 transition-colors hover:bg-panel"
                onClick={() => setIsMenuOpen(false)}
              >
                Open Source
              </a>
            </nav>
          </div>
        </div>
      )}
    </header>
  )
}
