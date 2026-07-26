"""Language & Prompting skill reports + gap-based learning recommendations.

Two SEPARATE report types, both computed from the user's own messages:
- language:   how clearly and correctly the user writes
- prompting:  how effectively the user instructs AI assistants

Each report = programmatic metrics (deterministic) + LLM qualitative analysis
+ credible-source resources matched to the weaknesses. Reports are cached in
skill_reports and recomputed on demand or when enough new messages exist.
"""
import json
import logging
import re
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.data.resources import match_resources
from app.db.base import utcnow
from app.llm import get_llm
from app.models import (
    KnowledgeProfileEntry,
    KnowledgeUnit,
    Message,
    ReviewHistory,
    ReviewState,
    Session,
    SkillReport,
    User,
)
from app.services.extraction import normalize_title

logger = logging.getLogger(__name__)

MIN_MESSAGES = 5
SAMPLE_LIMIT = 30
MESSAGE_LIMIT = 200
CACHE_MAX_AGE_HOURS = 24

LANGUAGE_SYSTEM_PROMPT = """[TASK:skills_language]
You are a precise, encouraging writing coach. You are given metrics and sample messages a
developer wrote while chatting with AI coding assistants. Assess the LANGUAGE quality only
(clarity, grammar/spelling, vocabulary, structure, tone) — not their technical skill.
Quote short evidence from their actual messages. Be specific and actionable, never insulting.
Respond ONLY with JSON:
{"overall_score": 0-100, "summary": "2-3 sentences",
 "sub_scores": {"clarity": 0-100, "grammar": 0-100, "vocabulary": 0-100, "structure": 0-100, "tone": 0-100},
 "strengths": ["..."],
 "weaknesses": [{"area": "...", "evidence": "short quote or pattern", "tip": "concrete improvement"}]}"""

PROMPTING_SYSTEM_PROMPT = """[TASK:skills_prompting]
You are an expert in prompt engineering reviewing how a developer instructs AI coding
assistants. Assess PROMPTING effectiveness only: context given, specificity of the ask,
constraints stated, expected output described, and iteration quality across follow-ups.
Quote short evidence from their actual prompts. Be specific and actionable.
Respond ONLY with JSON:
{"overall_score": 0-100, "summary": "2-3 sentences",
 "sub_scores": {"context": 0-100, "specificity": 0-100, "constraints": 0-100, "output_format": 0-100, "iteration": 0-100},
 "strengths": ["..."],
 "weaknesses": [{"area": "...", "evidence": "short quote or pattern", "tip": "concrete improvement"}]}"""

GOAL_VERBS = ["fix", "add", "create", "implement", "explain", "refactor", "debug", "build", "write", "convert", "optimize", "improve"]
CONSTRAINT_WORDS = ["must", "should", "only", "without", "don't", "avoid", "keep", "make sure", "ensure"]
OUTPUT_WORDS = ["format", "example", "return", "json", "list", "step", "table", "code block", "show me"]
INFORMAL_TOKENS = ["plz", "pls", " u ", " ur ", "gonna", "wanna", "idk", "btw", "lol", "asap"]


def _user_messages(db: DBSession, user_id: str) -> list[Message]:
    return list(
        db.scalars(
            select(Message)
            .join(Session, Session.id == Message.session_id)
            .where(Session.user_id == user_id, Message.role == "user", Message.authored_by == "user")
            .order_by(Message.timestamp.desc())
            .limit(MESSAGE_LIMIT)
        ).all()
    )


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"[.!?\n]+", text) if s.strip()]


def language_metrics(texts: list[str]) -> dict:
    words_per_msg = []
    all_words: list[str] = []
    questions = 0
    informal = 0
    no_capital = 0
    long_sentences = 0
    sentence_count = 0
    for t in texts:
        words = re.findall(r"[A-Za-z']+", t)
        words_per_msg.append(len(words))
        all_words.extend(w.lower() for w in words)
        if "?" in t:
            questions += 1
        low = f" {t.lower()} "
        if any(tok in low for tok in INFORMAL_TOKENS):
            informal += 1
        first = t.strip()[:1]
        if first and first.islower():
            no_capital += 1
        for s in _sentences(t):
            sentence_count += 1
            if len(s.split()) > 35:
                long_sentences += 1
    total = max(len(texts), 1)
    return {
        "messages_analyzed": len(texts),
        "avg_words_per_message": round(sum(words_per_msg) / total, 1),
        "vocabulary_richness": round(len(set(all_words)) / max(len(all_words), 1), 3),
        "question_rate": round(questions / total, 2),
        "informal_token_rate": round(informal / total, 2),
        "starts_lowercase_rate": round(no_capital / total, 2),
        "overlong_sentence_rate": round(long_sentences / max(sentence_count, 1), 2),
    }


def prompting_metrics(messages: list[Message]) -> dict:
    texts = [m.content for m in messages]
    total = max(len(texts), 1)
    with_context = 0
    with_goal = 0
    with_constraints = 0
    with_output = 0
    for m in messages:
        low = m.content.lower()
        if "```" in m.content or m.code_diff or len(low.split()) > 40:
            with_context += 1
        if any(v in low for v in GOAL_VERBS):
            with_goal += 1
        if any(c in low for c in CONSTRAINT_WORDS):
            with_constraints += 1
        if any(o in low for o in OUTPUT_WORDS):
            with_output += 1
    sessions_seen: dict[str, int] = {}
    for m in messages:
        sessions_seen[m.session_id] = sessions_seen.get(m.session_id, 0) + 1
    followups = sum(1 for c in sessions_seen.values() if c > 1)
    return {
        "messages_analyzed": len(texts),
        "avg_words_per_prompt": round(sum(len(t.split()) for t in texts) / total, 1),
        "context_rate": round(with_context / total, 2),
        "goal_verb_rate": round(with_goal / total, 2),
        "constraint_rate": round(with_constraints / total, 2),
        "output_format_rate": round(with_output / total, 2),
        "sessions_with_followups": followups,
        "sessions_total": max(len(sessions_seen), 1),
    }


def _analyze(system_prompt: str, metrics: dict, samples: list[str]) -> dict:
    payload = json.dumps({"metrics": metrics, "samples": [s[:600] for s in samples[:SAMPLE_LIMIT]]})
    raw = get_llm().complete(
        [{"role": "system", "content": system_prompt}, {"role": "user", "content": payload}],
        json_mode=True,
        max_tokens=3000,
    )
    try:
        analysis = json.loads(raw)
        if not isinstance(analysis, dict) or "overall_score" not in analysis:
            raise ValueError("missing overall_score")
        return analysis
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Skill analysis returned invalid JSON: %s", exc)
        return {
            "overall_score": None,
            "summary": "The analysis model returned an unreadable response — refresh to retry.",
            "sub_scores": {},
            "strengths": [],
            "weaknesses": [],
        }


def compute_report(db: DBSession, user: User, report_type: str, refresh: bool = False) -> SkillReport | dict:
    messages = _user_messages(db, user.id)
    if len(messages) < MIN_MESSAGES:
        return {
            "insufficient": True,
            "message": f"Not enough of your own messages yet ({len(messages)}/{MIN_MESSAGES}). "
            "Chat with the agent or import sessions, then come back.",
        }

    cached = db.scalar(
        select(SkillReport).where(SkillReport.user_id == user.id, SkillReport.report_type == report_type)
    )
    fresh_enough = (
        cached is not None
        and not refresh
        and cached.computed_at > utcnow() - timedelta(hours=CACHE_MAX_AGE_HOURS)
        and len(messages) < cached.message_count + 10
    )
    if fresh_enough:
        return cached

    texts = [m.content for m in messages]
    if report_type == "language":
        metrics = language_metrics(texts)
        analysis = _analyze(LANGUAGE_SYSTEM_PROMPT, metrics, texts)
        skill = "language"
    else:
        metrics = prompting_metrics(messages)
        analysis = _analyze(PROMPTING_SYSTEM_PROMPT, metrics, texts)
        skill = "prompting"

    weakness_keywords = [w.get("area", "") for w in analysis.get("weaknesses", [])]
    resources = match_resources(weakness_keywords, skill=skill, limit=5) or match_resources([], skill=skill, limit=4)

    content = {"metrics": metrics, "analysis": analysis, "resources": resources}
    if cached is None:
        cached = SkillReport(user_id=user.id, report_type=report_type, content=content, message_count=len(messages))
        db.add(cached)
    else:
        cached.content = content
        cached.message_count = len(messages)
        cached.computed_at = utcnow()
    db.commit()
    db.refresh(cached)
    return cached


def gap_recommendations(db: DBSession, user: User, limit: int = 6) -> list[dict]:
    """Knowledge areas the user is weakest in, each with credible resources.
    Weakness evidence: stale mastery, declining trend, or a recent failed recall."""
    rows = db.execute(
        select(ReviewState, KnowledgeUnit)
        .join(KnowledgeUnit, KnowledgeUnit.id == ReviewState.unit_id)
        .where(ReviewState.user_id == user.id, KnowledgeUnit.deleted_at.is_(None))
    ).all()
    trends = {
        e.unit_id: e.retention_trend
        for e in db.scalars(select(KnowledgeProfileEntry).where(KnowledgeProfileEntry.user_id == user.id)).all()
    }

    gaps: list[tuple[int, dict]] = []
    for state, unit in rows:
        reasons = []
        severity = 0
        last_perf = db.scalar(
            select(ReviewHistory.performance)
            .where(ReviewHistory.unit_id == unit.id, ReviewHistory.user_id == user.id)
            .order_by(ReviewHistory.reviewed_at.desc())
            .limit(1)
        )
        if last_perf == "incorrect":
            reasons.append("last recall failed")
            severity += 3
        elif last_perf == "partial":
            reasons.append("last recall was shaky")
            severity += 2
        if state.mastery_status == "stale":
            reasons.append("gone stale")
            severity += 2
        if trends.get(unit.id) == "declining":
            reasons.append("retention declining")
            severity += 2
        if float(state.ease_factor) <= 1.8:
            reasons.append("repeatedly difficult")
            severity += 1
        if not reasons:
            continue
        keywords = re.findall(r"[a-z][a-z0-9+#.]{2,}", normalize_title(unit.title))
        resources = match_resources(keywords + [unit.title.lower()], skill="coding", limit=3)
        if not resources:
            continue
        gaps.append(
            (severity, {"topic": unit.title, "unit_type": unit.unit_type, "reasons": reasons, "resources": resources})
        )
    gaps.sort(key=lambda pair: -pair[0])
    return [g for _, g in gaps[:limit]]
