export type DescriptionBlock =
  | { type: 'paragraph'; text: string }
  | { type: 'heading'; text: string }
  | { type: 'list'; items: string[]; ordered?: boolean }

const HEADING_RE = /^(?:#{1,6}\s+(.+)|((?:key benefits|benefits|how to use|directions|who is it (?:best )?for\??|ingredients|what it does|key ingredients)\s*:?))$/i
const BULLET_RE = /^(?:[-•–—]\s*|\*\s+)(.+)$/
const RULE_RE = /^[-*_]{3,}$/

/** Interpret plain-text line breaks, headings, and bullet markers without rendering HTML. */
export function formatProductDescription(description: string): DescriptionBlock[] {
  const blocks: DescriptionBlock[] = []
  let paragraph: string[] = []
  let list: string[] = []
  let ordered = false
  const flushParagraph = () => { if (paragraph.length) blocks.push({ type: 'paragraph', text: paragraph.join(' ') }); paragraph = [] }
  const flushList = () => { if (list.length) blocks.push(ordered ? { type: 'list', items: list, ordered: true } : { type: 'list', items: list }); list = []; ordered = false }

  for (const raw of description.replace(/\r\n?/g, '\n').split('\n')) {
    const line = raw.trim()
    if (!line || RULE_RE.test(line)) { flushParagraph(); flushList(); continue }

    const numbered = line.match(/^\d+[.)]\s+(.+)$/)
    if (numbered) {
      flushParagraph()
      if (list.length && !ordered) flushList()
      ordered = true
      list.push(numbered[1]!.trim())
      continue
    }
    const bullet = line.match(BULLET_RE)
    if (bullet && /[A-Za-z0-9]/.test(bullet[1]!)) {
      flushParagraph()
      if (ordered) flushList()
      list.push(bullet[1]!.trim())
      continue
    }

    flushList()
    const heading = line.match(HEADING_RE)
    if (heading) {
      flushParagraph()
      blocks.push({ type: 'heading', text: (heading[1] ?? heading[2]!).replace(/:$/, '').trim() })
      continue
    }

    paragraph.push(line)
  }

  flushParagraph()
  flushList()
  return blocks
}
