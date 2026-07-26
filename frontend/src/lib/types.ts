export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: string
  email: string
  display_name: string | null
  learning_intensity: string
  notification_prefs: Record<string, unknown>
  created_at: string
}

export interface Project {
  id: string
  name: string
  created_at: string
}

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'tool'
  content: string
  authored_by: 'ai' | 'user' | null
  code_diff: string | null
  timestamp: string
}

export interface Session {
  id: string
  project_id: string | null
  source_tool: string
  source_fidelity: 'native' | 'wrapped'
  title: string | null
  started_at: string
  ended_at: string | null
  extraction_status: 'pending' | 'running' | 'completed' | 'failed' | 'insufficient_content'
  created_at: string
}

export interface SessionDetail extends Session {
  messages: Message[]
}

export interface KnowledgeUnit {
  id: string
  project_id: string | null
  session_id: string | null
  source_fidelity: string
  unit_type: 'concept' | 'decision' | 'bug_fix' | 'pattern'
  title: string
  summary: string | null
  difficulty: string | null
  extracted_at: string
}

export type ArtifactFormat =
  | 'flashcard'
  | 'qa'
  | 'self_explanation'
  | 'retrieval_practice'
  | 'synthesis'
  | 'diagram'
  | 'mcq'

export interface Artifact {
  id: string
  scope_type: 'message' | 'chat' | 'project' | 'time_range'
  scope_ref: Record<string, unknown>
  format: ArtifactFormat
  content: ArtifactContent
  generated_at: string
  triggered_by: 'user_action' | 'scheduled_review'
  completed_at: string | null
}

export interface ArtifactContent {
  type: string
  cards?: { front: string; back: string }[]
  questions?: {
    question: string
    expected_points?: string[]
    answer?: string
    kind?: string
    choices?: string[]
    correct_index?: number
    explanation?: string
  }[]
  prompts?: { prompt: string; context?: string }[]
  prompt?: string
  related_titles?: string[]
  mermaid?: string
  explanation?: string
  recall_prompt?: string
}

export interface LearnResponse {
  artifacts: Artifact[]
  units_covered: number
  message: string | null
}

export interface ReviewQueueItem {
  unit: KnowledgeUnit
  artifact: Artifact
  review_state_id: string
  mastery_status: string
  next_review_at: string
  early: boolean
}

export interface ReviewQueue {
  items: ReviewQueueItem[]
  total_due: number
  total_early: number
  projects_in_session: number
  next_due_at: string | null
}

export interface ReviewResult {
  unit_id: string
  mastery_status: string
  next_review_at: string
  interval_days: number
  ease_factor: number
}

export interface ProfileEntry {
  unit: KnowledgeUnit
  mastery_status: 'new' | 'learning' | 'consolidated' | 'stale'
  retention_trend: 'improving' | 'stable' | 'declining' | null
  visibility: 'private' | 'shared'
  entry_id: string
}

export interface Profile {
  entries: ProfileEntry[]
  counts: Record<string, number>
  generated_at: string
}

export interface EngagementMetrics {
  event_counts: Record<string, number>
  total_sessions: number
  learn_usage_rate: number
}

export interface RetentionMetrics {
  curve: { bucket: string; reviews: number; accuracy: number | null }[]
  total_reviews: number
  overall_recall_rate: number | null
}

export interface ActivityDay {
  date: string
  reviews: number
  correct: number
}

export interface IndependenceMetrics {
  window_days: number
  ai_authored: number
  user_authored: number
  ai_assist_ratio: number | null
  note: string
}

export interface GradeVerdict {
  performance: 'correct' | 'partial' | 'incorrect' | null
  justification: string
}

export interface AgentChatResponse {
  session_id: string
  user_message: Message
  assistant_message: Message
}
