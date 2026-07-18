import { Logo } from "./logo"
import { GITHUB_URL, RELEASES_URL, LICENSE_URL, ISSUES_URL } from "@/lib/links"

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-5xl flex-col items-start justify-between gap-6 px-5 py-10 sm:flex-row sm:items-center">
        <div className="flex flex-col gap-2">
          <Logo />
          <p className="text-xs text-muted-foreground">
            Built by Elevon (ka.refined) in Accra, Ghana. Free forever.
          </p>
        </div>
        <nav
          aria-label="Footer navigation"
          className="flex flex-wrap gap-x-6 gap-y-2 text-[13px] text-muted-foreground"
        >
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
          <a
            href={RELEASES_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            Releases
          </a>
          <a
            href={ISSUES_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            Report a bug
          </a>
          <a
            href={LICENSE_URL}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-foreground"
          >
            MIT License
          </a>
        </nav>
      </div>
    </footer>
  )
}
