export type DescriptionBlock =
  | { type: 'paragraph'; text: string }
  | { type: 'heading'; text: string }
  | { type: 'list'; items: string[] }

/** Interpret plain-text line breaks and explicit list markers without rendering HTML. */
export function formatProductDescription(description: string): DescriptionBlock[] {
  const blocks: DescriptionBlock[] = []
  let paragraph: string[] = []
  let list: string[] = []
  const flushParagraph = () => { if (paragraph.length) blocks.push({ type: 'paragraph', text: paragraph.join(' ') }); paragraph = [] }
  const flushList = () => { if (list.length) blocks.push({ type: 'list', items: list }); list = [] }
  for (const raw of description.replace(/\r\n?/g, '\n').split('\n')) {
    const line = raw.trim()
    if (!line) { flushParagraph(); flushList(); continue }
    const bullet = line.match(/^(?:[-*•]\s+)(.+)$/)
    if (bullet) { flushParagraph(); list.push(bullet[1]!); continue }
    flushList()
    if (/^(?:key benefits|benefits|how to use|directions|who is it (?:best )?for\??|ingredients)\s*:?$/i.test(line)) {
      flushParagraph(); blocks.push({ type: 'heading', text: line.replace(/:$/, '') }); continue
    }
    paragraph.push(line)
  }
  flushParagraph(); flushList()
  return blocks
}
