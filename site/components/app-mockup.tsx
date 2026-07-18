import {
  FileText,
  FileSpreadsheet,
  File,
  Folder,
  FolderOpen,
  Bookmark,
  Volume2,
  Search,
} from "lucide-react"

const tabs = [
  { name: "biology-notes.md", icon: FileText, active: true },
  { name: "lecture-04.pdf", icon: File, active: false },
  { name: "lab-data.xlsx", icon: FileSpreadsheet, active: false },
  { name: "essay-draft.docx", icon: FileText, active: false },
]

const vaultItems = [
  { name: "Semester 2", icon: FolderOpen, depth: 0 },
  { name: "biology-notes.md", icon: FileText, depth: 1, active: true },
  { name: "lecture-04.pdf", icon: File, depth: 1 },
  { name: "lab-data.xlsx", icon: FileSpreadsheet, depth: 1 },
  { name: "Past Papers", icon: Folder, depth: 0 },
  { name: "Readings", icon: Folder, depth: 0 },
]

export function AppMockup() {
  return (
    <div
      className="overflow-hidden rounded-xl border border-border bg-[#1e1e1e] shadow-[0_24px_80px_-24px_rgba(0,0,0,0.8)]"
      role="img"
      aria-label="EleViewer app window showing a markdown file open beside a vault sidebar with PDF, Excel, and Word files in tabs"
    >
      {/* Title bar */}
      <div className="flex items-center justify-between border-b border-[#333] bg-[#252526] px-4 py-2">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#444]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#444]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#444]" />
        </div>
        <span className="font-mono text-[11px] text-[#888]">
          EleViewer — biology-notes.md
        </span>
        <div className="flex items-center gap-3 text-[#888]">
          <Search className="h-3.5 w-3.5" />
          <Bookmark className="h-3.5 w-3.5" />
          <Volume2 className="h-3.5 w-3.5 text-accent" />
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex border-b border-[#333] bg-[#252526]">
        {tabs.map((tab) => (
          <div
            key={tab.name}
            className={`flex items-center gap-1.5 border-r border-[#333] px-3 py-1.5 font-mono text-[11px] ${
              tab.active
                ? "bg-[#1e1e1e] text-white"
                : "bg-[#2d2d2d] text-[#999]"
            }`}
          >
            <tab.icon className="h-3 w-3" />
            <span className="hidden sm:inline">{tab.name}</span>
            <span className="sm:hidden">{tab.name.split(".").pop()}</span>
          </div>
        ))}
      </div>

      <div className="flex">
        {/* Vault sidebar */}
        <div className="hidden w-44 shrink-0 border-r border-[#333] bg-[#252526] py-2 md:block">
          <p className="px-3 pb-2 font-mono text-[10px] uppercase tracking-widest text-[#777]">
            Vault
          </p>
          {vaultItems.map((item) => (
            <div
              key={item.name}
              className={`flex items-center gap-2 py-1 text-[11px] ${
                item.active ? "bg-[#2d2d2d] text-white" : "text-[#999]"
              }`}
              style={{ paddingLeft: `${12 + item.depth * 14}px` }}
            >
              <item.icon className="h-3 w-3 shrink-0" />
              <span className="truncate">{item.name}</span>
            </div>
          ))}
        </div>

        {/* Editor pane */}
        <div className="min-w-0 flex-1 bg-[#1e1e1e] p-4 font-mono text-[12px] leading-relaxed sm:p-5">
          <p className="text-[#6cb6ff]"># Cell Respiration — Week 4</p>
          <p className="mt-3 text-[#e0e0e0]">
            Glycolysis happens in the <span className="text-white">cytoplasm</span> and
            produces 2 ATP net.
          </p>
          <p className="mt-2 text-[#e0e0e0]">
            <span className="text-[#6cb6ff]">## Key stages</span>
          </p>
          <p className="mt-2 text-[#e0e0e0]">- Glycolysis → pyruvate</p>
          <p className="text-[#e0e0e0]">- Krebs cycle → NADH, FADH2</p>
          <p className="text-[#e0e0e0]">
            - Electron transport chain → <span className="text-white">~34 ATP</span>
          </p>
          <p className="mt-3 text-[#777]">
            {"> Exam tip: know where each stage happens."}
          </p>
          <div className="mt-4 flex items-center gap-2 rounded border border-[#333] bg-[#252526] px-2.5 py-1.5">
            <Volume2 className="h-3 w-3 text-accent" />
            <span className="text-[10px] text-[#999]">
              Reading aloud: lecture-04.pdf — page 12 of 38
            </span>
          </div>
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between border-t border-[#333] bg-[#1e1e1e] px-4 py-1.5 font-mono text-[10px] text-[#777]">
        <span>4 tabs · session saved</span>
        <span className="hidden sm:inline">Ctrl+Q quick switch · Alt+V vault</span>
        <span>md · UTF-8</span>
      </div>
    </div>
  )
}
