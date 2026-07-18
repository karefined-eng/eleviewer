import { SiteHeader } from "@/components/site-header"
import { Hero } from "@/components/hero"
import { Formats } from "@/components/formats"
import { Features } from "@/components/features"
import { Shortcuts } from "@/components/shortcuts"
import { OpenSource } from "@/components/open-source"
import { DownloadCta } from "@/components/download-cta"
import { SiteFooter } from "@/components/site-footer"

export default function Home() {
  return (
    <>
      <SiteHeader />
      <main>
        <Hero />
        <Formats />
        <Features />
        <Shortcuts />
        <OpenSource />
        <DownloadCta />
      </main>
      <SiteFooter />
    </>
  )
}
