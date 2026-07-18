import type { Metadata, Viewport } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"

const geistSans = Geist({ subsets: ["latin"], variable: "--font-geist-sans" })
const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
})

export const metadata: Metadata = {
  title: "EleViewer — Every file your professor throws at you. One free app.",
  description:
    "EleViewer is a free, open-source study workspace for Windows. Open and edit DOCX, XLSX, PDF (with text-to-speech), Markdown, and TXT in one lightweight 16 MB app. No install. No account. No cost.",
  keywords: [
    "EleViewer",
    "free document viewer",
    "open source",
    "student tools",
    "PDF text to speech",
    "DOCX viewer",
    "XLSX viewer",
    "markdown editor",
    "Windows",
  ],
  openGraph: {
    title: "EleViewer — The free study workspace for Windows",
    description:
      "Open DOCX, XLSX, PDF, Markdown, and TXT in one lightweight free app. Open source, forever.",
    type: "website",
  },
}

export const viewport: Viewport = {
  themeColor: "#131313",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`bg-background ${geistSans.variable} ${geistMono.variable}`}
    >
      <body className="font-sans">{children}</body>
    </html>
  )
}
