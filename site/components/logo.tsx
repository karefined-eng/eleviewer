export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="7" fill="#1c1c1c" />
      <rect
        x="0.5"
        y="0.5"
        width="31"
        height="31"
        rx="6.5"
        stroke="#2c2c2c"
      />
      {/* E glyph built from three bars — evokes stacked document lines */}
      <rect x="9" y="9" width="14" height="3" rx="1.5" fill="#f2f2f0" />
      <rect x="11" y="14.5" width="10" height="3" rx="1.5" fill="#6cb6ff" />
      <rect x="9" y="20" width="14" height="3" rx="1.5" fill="#f2f2f0" />
    </svg>
  )
}

export function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <LogoMark />
      <span className="text-[15px] font-semibold tracking-tight text-foreground">
        EleViewer
      </span>
    </span>
  )
}
