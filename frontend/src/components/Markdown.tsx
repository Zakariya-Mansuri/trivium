import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/** Themed markdown renderer for assistant output and artifact content. */
export default function Markdown({ children }: { children: string }) {
  return (
    <div className="md-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  )
}
