import {
  Volume2,
  FolderTree,
  Zap,
  History,
  Bookmark,
  Globe,
} from "lucide-react"

const features = [
  {
    icon: Volume2,
    title: "PDFs that read to you",
    body: "Native text-to-speech turns any lecture slide or reading into audio. Study while you commute, cook, or rest your eyes.",
  },
  {
    icon: FolderTree,
    title: "Vault sidebar",
    body: "Point EleViewer at your course folders and every file is one click away. Toggle it with Alt+V and stay in flow.",
  },
  {
    icon: Zap,
    title: "Quick switcher",
    body: "Ctrl+Q opens a VSCode-style fuzzy finder over your recent and pinned files. Type three letters, hit Enter, keep working.",
  },
  {
    icon: History,
    title: "Session restore",
    body: "Close your laptop mid-study session. Reopen EleViewer and every tab comes back exactly where you left it.",
  },
  {
    icon: Bookmark,
    title: "Persistent bookmarks",
    body: "Bookmark PDF pages and files in a dedicated panel. Your place in a 400-page textbook is never lost again.",
  },
  {
    icon: Globe,
    title: "Built-in web panel",
    body: "Open a browser side-by-side with your notes using Ctrl+T. Reference the web without switching windows.",
  },
]

export function Features() {
  return (
    <section id="features" className="mx-auto max-w-5xl scroll-mt-20 px-5 pb-16 sm:pb-24">
      <div className="mb-12 max-w-xl">
        <p className="mb-3 font-mono text-xs uppercase tracking-widest text-accent">
          Features
        </p>
        <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground">
          A study workspace, not another bloated suite
        </h2>
        <p className="mt-4 text-pretty text-[15px] leading-relaxed text-muted-foreground">
          Everything a student needs to read, write, and organize coursework —
          and nothing that slows an old laptop down.
        </p>
      </div>
      <div className="grid gap-px overflow-hidden rounded-xl border border-border bg-border sm:grid-cols-2 lg:grid-cols-3">
        {features.map((f) => (
          <div key={f.title} className="flex flex-col gap-3 bg-panel p-6">
            <f.icon className="h-5 w-5 text-accent" aria-hidden="true" />
            <h3 className="text-[15px] font-semibold text-foreground">
              {f.title}
            </h3>
            <p className="text-[13px] leading-relaxed text-muted-foreground">
              {f.body}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
