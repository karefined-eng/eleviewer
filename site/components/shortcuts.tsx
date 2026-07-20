import type { ReactNode } from 'react'

const shortcuts = [
  { keys: ["Ctrl", "Q"], action: "Quick switcher — fuzzy search your files" },
  { keys: ["Alt", "V"], action: "Toggle the vault sidebar" },
  { keys: ["Ctrl", "T"], action: "Open the web browser panel" },
  { keys: ["Ctrl", "D"], action: "Bookmark the current PDF page" },
  { keys: ["Ctrl", "Shift", "T"], action: "Reopen a closed tab" },
  { keys: ["Ctrl", "Alt", "B"], action: "Toggle the bookmarks panel" },
]

function Kbd({ children }: { children?: ReactNode }) {
  return (
    <kbd className="rounded-md border border-border bg-panel-2 px-2 py-1 font-mono text-[11px] font-medium text-foreground shadow-[0_2px_0_0_var(--border)]">
      {children}
    </kbd>
  )
}

export function Shortcuts() {
  return (
    <section id="shortcuts" className="border-y border-border bg-panel/40">
      <div className="mx-auto max-w-5xl scroll-mt-20 px-5 py-16 sm:py-24">
        <div className="grid items-start gap-10 lg:grid-cols-2">
          <div className="max-w-md">
            <p className="mb-3 font-mono text-xs uppercase tracking-widest text-accent">
              Keyboard-first
            </p>
            <h2 className="text-balance text-3xl font-semibold tracking-tight text-foreground">
              Built for hands that never leave the keyboard
            </h2>
            <p className="mt-4 text-pretty text-[15px] leading-relaxed text-muted-foreground">
              Every core action has a shortcut. Learn six of them and EleViewer
              starts to feel less like an app and more like a reflex.
            </p>
          </div>
          <ul className="flex flex-col gap-px overflow-hidden rounded-xl border border-border bg-border">
            {shortcuts.map((s) => (
              <li
                key={s.action}
                className="flex items-center justify-between gap-4 bg-panel px-5 py-3.5"
              >
                <span className="text-[13px] text-muted-foreground">
                  {s.action}
                </span>
                <span className="flex shrink-0 items-center gap-1">
                  {s.keys.map((k, i) => (
                    <span key={k} className="flex items-center gap-1">
                      {i > 0 && (
                        <span className="text-[11px] text-muted-foreground">
                          +
                        </span>
                      )}
                      <Kbd>{k}</Kbd>
                    </span>
                  ))}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
