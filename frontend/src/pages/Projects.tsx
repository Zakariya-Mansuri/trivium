import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button, Card, EmptyState, ErrorNote, Input, PageHeader, Spinner } from '../components/ui'
import { api } from '../lib/api'
import type { Project } from '../lib/types'

export default function Projects() {
  const [projects, setProjects] = useState<Project[] | null>(null)
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [editing, setEditing] = useState<string | null>(null)
  const [editName, setEditName] = useState('')

  const load = () => api<Project[]>('/projects').then(setProjects).catch((e) => setError(e.message))
  useEffect(() => {
    load()
  }, [])

  const create = async (e: FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    setBusy(true)
    setError(null)
    try {
      await api('/projects', { method: 'POST', body: { name: name.trim() } })
      setName('')
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setBusy(false)
    }
  }

  const rename = async (id: string) => {
    if (!editName.trim()) return
    try {
      await api(`/projects/${id}`, { method: 'PATCH', body: { name: editName.trim() } })
      setEditing(null)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rename failed')
    }
  }

  const remove = async (id: string) => {
    if (!confirm('Archive this project? Its sessions and knowledge remain in your history.')) return
    try {
      await api(`/projects/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  return (
    <div className="fade-up">
      <PageHeader title="Projects" subtitle="Group sessions by project — interleaved review pulls across them on purpose." />
      <form onSubmit={create} className="flex gap-3 mb-6 max-w-md">
        <Input placeholder="New project name" value={name} onChange={(e) => setName(e.target.value)} maxLength={200} />
        <Button type="submit" disabled={busy || !name.trim()}>
          Create
        </Button>
      </form>
      <ErrorNote message={error} />

      {!projects ? (
        <Spinner />
      ) : projects.length === 0 ? (
        <EmptyState title="No projects yet" hint="Create one above, then attach sessions to it when importing or chatting with the agent." />
      ) : (
        <div className="grid md:grid-cols-2 gap-4 mt-4">
          {projects.map((p) => (
            <Card key={p.id} className="hover:border-primary-600/60 transition-colors">
              {editing === p.id ? (
                <div className="flex gap-2">
                  <Input value={editName} onChange={(e) => setEditName(e.target.value)} maxLength={200} />
                  <Button onClick={() => rename(p.id)}>Save</Button>
                  <Button variant="ghost" onClick={() => setEditing(null)}>
                    Cancel
                  </Button>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="font-display font-semibold text-ink-100">{p.name}</h2>
                    <div className="flex gap-2 text-xs shrink-0">
                      <button
                        className="text-ink-300 hover:text-ink-100"
                        onClick={() => {
                          setEditing(p.id)
                          setEditName(p.name)
                        }}
                      >
                        Rename
                      </button>
                      <button className="text-ink-300 hover:text-bad-500" onClick={() => remove(p.id)}>
                        Archive
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-ink-300 mt-1">Created {new Date(p.created_at).toLocaleDateString()}</p>
                  <div className="flex gap-4 mt-4 text-sm">
                    <Link to={`/app/sessions?project=${p.id}`} className="text-primary-300 hover:text-primary-400">
                      Sessions →
                    </Link>
                    <Link to={`/app/learn?scope=project&project=${p.id}`} className="text-accent-400 hover:text-accent-500">
                      ✦ Learn this project
                    </Link>
                  </div>
                </>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
