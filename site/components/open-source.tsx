import { Scale, HardDrive, ShieldOff, GitFork } from "lucide-react"
import { GITHUB_URL, LICENSE_URL } from "@/lib/links"

const principles = [
  {
    icon: Scale,
    title: "MIT licensed",
    body: "Use it, fork it, ship it in your own project. No strings.",
  },
  {
    icon: HardDrive,
    title: "16 MB, portable",
    body: "One .exe. Runs from a USB stick or a locked-down lab machine.",
  },
  {
    icon: ShieldOff,
    title: "No account, no telemetry",
    body: "Your files stay on your machine. Nothing phones home.",
  },
  {
    icon: GitFork,
    title: "Yours to build on",
    body: "Clean Python + PySide6 codebase with a simple factory pattern.",
  },
]

export function OpenSource() {
  return (
    <section id="open-source" className="mx-auto max-w-5xl scroll-mt-20 px-5 py-16 sm:py-24">
      <div className="mb-12 max-w-xl">
        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-accent">
          Open source, forever
        </p>
        <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground">
          Free because someone&apos;s free software got us here
        </h2>
        <p className="mt-4 text-pretty text-[15px] leading-relaxed text-muted-foreground">
          EleViewer exists because open-source tools made its creator&apos;s
          education possible. It will never cost money, show ads, or collect
          your data. If it helps you, star it, share it, or contribute.
        </p>
      </div>
      <div className="grid gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
        {principles.map((p) => (
          <div key={p.title} className="flex flex-col gap-3 bg-panel p-6">
            <p.icon className="h-5 w-5 text-accent" aria-hidden="true" />
            <h3 className="text-sm font-semibold text-foreground">{p.title}</h3>
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              {p.body}
            </p>
          </div>
        ))}
      </div>
      <p className="mt-6 text-[13px] text-muted-foreground">
        Read the{" "}
        <a
          href={LICENSE_URL}
          target="_blank"
          rel="noreferrer"
          className="text-accent underline-offset-4 hover:underline"
        >
          MIT license
        </a>{" "}
        or browse the{" "}
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          className="text-accent underline-offset-4 hover:underline"
        >
          source code
        </a>
        .
      </p>
    </section>
  )
}
