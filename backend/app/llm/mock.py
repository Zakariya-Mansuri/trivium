"""Deterministic mock LLM provider.

Produces content-aware output using heuristics so the entire product loop
(agent chat -> extraction -> artifact generation) works and is testable
without any API key. Services embed a task marker in the system prompt
([TASK:agent_chat] / [TASK:extraction] / [TASK:artifact]) which this
provider dispatches on.
"""
import json
import re

from app.llm.base import LLMProvider

TECH_TERMS = [
    "fastapi", "react", "jwt", "oauth", "postgresql", "postgres", "sqlite", "redis",
    "docker", "kubernetes", "async", "asyncio", "sqlalchemy", "alembic", "tailwind",
    "vite", "typescript", "javascript", "python", "rust", "tauri", "websocket",
    "rest api", "graphql", "cors", "middleware", "authentication", "authorization",
    "hashing", "bcrypt", "index", "migration", "transaction", "cache", "queue",
    "rate limit", "pagination", "orm", "n+1", "recursion", "closure", "decorator",
    "generator", "dependency injection", "state management", "hook", "component",
    "props", "reducer", "spaced repetition", "embedding", "vector", "llm",
]

BUG_SIGNALS = ["bug", "error", "exception", "traceback", "fix", "fixed", "crash", "fail", "broken", "issue"]
DECISION_SIGNALS = ["decided", "chose", "instead of", "tradeoff", "trade-off", "option", "alternative", "versus", " vs ", "why not", "better to", "opted"]
PATTERN_SIGNALS = ["pattern", "again", "similar to", "same as", "recurring", "as before", "like last time", "reuse"]
ARCH_SIGNALS = ["architecture", "component", "service", "layer", "pipeline", "flow", "diagram", "system design", "microservice", "module"]


def _find_terms(text: str, limit: int = 6) -> list[str]:
    low = text.lower()
    found = []
    for term in TECH_TERMS:
        if term in low and term not in found:
            found.append(term)
        if len(found) >= limit:
            break
    return found


def _classify(text: str) -> tuple[str, str]:
    """Returns (unit_type, signal) for a chunk of conversation text."""
    low = text.lower()
    for s in DECISION_SIGNALS:
        if s in low:
            return "decision", s
    for s in BUG_SIGNALS:
        if s in low:
            return "bug_fix", s
    for s in PATTERN_SIGNALS:
        if s in low:
            return "pattern", s
    return "concept", "default"


def _difficulty(text: str) -> str:
    low = text.lower()
    advanced = ["distributed", "concurrency", "race condition", "optimization", "sharding", "consensus", "n+1"]
    novice = ["what is", "how do i", "basics", "beginner", "simple", "introduction"]
    if any(s in low for s in advanced):
        return "advanced"
    if any(s in low for s in novice):
        return "novice"
    return "intermediate"


class MockProvider(LLMProvider):
    name = "mock"

    def complete(self, messages: list[dict], *, json_mode: bool = False, max_tokens: int = 2048) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        user_text = "\n".join(m["content"] for m in messages if m["role"] == "user")
        if "[TASK:extraction]" in system:
            return self._extract(user_text)
        if "[TASK:artifact]" in system:
            return self._artifact(user_text)
        if "[TASK:skills_language]" in system:
            return self._skills(user_text, "language")
        if "[TASK:skills_prompting]" in system:
            return self._skills(user_text, "prompting")
        return self._chat(messages)

    # --- skill reports (deterministic scoring from the provided metrics) ---

    def _skills(self, payload_text: str, kind: str) -> str:
        try:
            metrics = json.loads(payload_text).get("metrics", {})
        except json.JSONDecodeError:
            metrics = {}

        def clamp(v: float) -> int:
            return int(max(5, min(98, v)))

        if kind == "language":
            sub = {
                "clarity": clamp(85 - metrics.get("overlong_sentence_rate", 0) * 100),
                "grammar": clamp(90 - metrics.get("starts_lowercase_rate", 0) * 60 - metrics.get("informal_token_rate", 0) * 60),
                "vocabulary": clamp(40 + metrics.get("vocabulary_richness", 0.4) * 100),
                "structure": clamp(60 + min(metrics.get("avg_words_per_message", 10), 40)),
                "tone": clamp(88 - metrics.get("informal_token_rate", 0) * 80),
            }
            weaknesses = []
            if metrics.get("starts_lowercase_rate", 0) > 0.4:
                weaknesses.append({"area": "grammar", "evidence": "many messages start lowercase", "tip": "Capitalize sentence starts — it carries into docs and commits."})
            if metrics.get("overlong_sentence_rate", 0) > 0.2:
                weaknesses.append({"area": "clarity", "evidence": "long run-on sentences", "tip": "Split sentences over ~25 words; one idea per sentence."})
            if not weaknesses:
                weaknesses.append({"area": "conciseness", "evidence": "some repeated phrasing", "tip": "Trim filler words; lead with the point."})
        else:
            sub = {
                "context": clamp(30 + metrics.get("context_rate", 0) * 65),
                "specificity": clamp(30 + metrics.get("goal_verb_rate", 0) * 65),
                "constraints": clamp(25 + metrics.get("constraint_rate", 0) * 70),
                "output_format": clamp(25 + metrics.get("output_format_rate", 0) * 70),
                "iteration": clamp(40 + (metrics.get("sessions_with_followups", 0) / max(metrics.get("sessions_total", 1), 1)) * 55),
            }
            weaknesses = []
            if metrics.get("constraint_rate", 0) < 0.3:
                weaknesses.append({"area": "constraints", "evidence": "prompts rarely state limits", "tip": "Say what the answer must and must not do (stack, style, scope)."})
            if metrics.get("output_format_rate", 0) < 0.3:
                weaknesses.append({"area": "output_format", "evidence": "expected output rarely described", "tip": "Ask for the shape you want: 'return a diff', 'give 3 options with tradeoffs'."})
            if not weaknesses:
                weaknesses.append({"area": "context", "evidence": "occasional missing error text", "tip": "Paste the exact error and the relevant code, not a paraphrase."})

        overall = int(sum(sub.values()) / len(sub))
        return json.dumps(
            {
                "overall_score": overall,
                "summary": f"Based on {metrics.get('messages_analyzed', 0)} of your messages, your {kind} skills score {overall}/100. "
                "(Offline analysis — configure a real LLM provider for deeper feedback.)",
                "sub_scores": sub,
                "strengths": ["Consistent engagement with concrete coding problems"],
                "weaknesses": weaknesses,
            }
        )

    # --- agent chat ---

    def _chat(self, messages: list[dict]) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        terms = _find_terms(last_user)
        topic = terms[0] if terms else "your question"
        lines = [
            f"Here's how I'd approach {topic}:",
            "",
            "1. Start by isolating the core requirement and the constraint that matters most.",
            f"2. For {topic}, the idiomatic approach is to keep the implementation small and explicit, then iterate.",
            "3. Add a focused test around the behavior before refactoring further.",
        ]
        if any(s in last_user.lower() for s in BUG_SIGNALS):
            lines.append(
                "\nSince this looks like a bug, check the exact error message and the state right before the failure — "
                "most issues of this kind come from an unexpected None/empty value or a mismatched type at the boundary."
            )
        code_hint = re.search(r"```(\w+)?", last_user)
        if code_hint:
            lines.append("\n```python\n# minimal illustrative example\ndef solve(data):\n    validated = validate(data)\n    return process(validated)\n```")
        lines.append(
            "\n(Note: this response was generated by Trivium's offline mock provider — "
            "configure LLM_PROVIDER/LLM_API_KEY for a real model.)"
        )
        return "\n".join(lines)

    # --- extraction ---

    def _extract(self, transcript: str) -> str:
        blocks = [b.strip() for b in re.split(r"\n(?=\[(?:user|assistant|tool)\])", transcript) if b.strip()]
        units: list[dict] = []
        seen_titles: set[str] = set()
        for block in blocks:
            terms = _find_terms(block)
            if not terms and len(block) < 80:
                continue
            unit_type, signal = _classify(block)
            main = terms[0] if terms else (block.splitlines()[0][:60].strip() or "general approach")
            title_map = {
                "concept": f"Understanding {main}",
                "decision": f"Decision: choosing an approach for {main}",
                "bug_fix": f"Bug fix involving {main}",
                "pattern": f"Recurring pattern: {main}",
            }
            title = title_map[unit_type]
            if title in seen_titles:
                continue
            seen_titles.add(title)
            snippet = re.sub(r"\s+", " ", block)[:220]
            units.append(
                {
                    "unit_type": unit_type,
                    "title": title,
                    "summary": f"From this session: {snippet}",
                    "difficulty": _difficulty(block),
                    "signal": signal,
                    "concepts": terms[:4],
                }
            )
            if len(units) >= 8:
                break
        return json.dumps({"units": units})

    # --- artifact generation ---

    def _artifact(self, payload_text: str) -> str:
        try:
            payload = json.loads(payload_text)
        except json.JSONDecodeError:
            payload = {"format": "qa", "units": []}
        fmt = payload.get("format", "qa")
        units = payload.get("units", [])
        titles = [u.get("title", "concept") for u in units] or ["the concept"]
        summaries = {u.get("title", ""): u.get("summary", "") for u in units}

        if fmt == "flashcard":
            cards = [
                {
                    "front": f"Explain, from memory: {t}",
                    "back": summaries.get(t) or f"Recall what you learned about {t} in this session.",
                }
                for t in titles
            ]
            return json.dumps({"type": "flashcard", "cards": cards})

        if fmt == "qa":
            questions = [
                {
                    "question": f"Without looking at the code, explain the reasoning behind '{t}'. What were the alternatives, and why was this chosen?",
                    "expected_points": [
                        "States the chosen approach accurately",
                        "Names at least one alternative that was considered",
                        "Explains the tradeoff that drove the decision",
                    ],
                    "kind": "recall",
                }
                for t in titles
            ]
            return json.dumps({"type": "qa", "questions": questions})

        if fmt == "self_explanation":
            prompts = [
                {
                    "prompt": f"Why did this approach work here for '{t}' — and describe a concrete situation where it would NOT be the right choice.",
                    "context": summaries.get(t, ""),
                }
                for t in titles
            ]
            return json.dumps({"type": "self_explanation", "prompts": prompts})

        if fmt == "retrieval_practice":
            questions = [
                {
                    "question": f"You hit this before: {t}. From memory — what was the root cause, and what was the fix?",
                    "answer": summaries.get(t) or "Recall the root cause and the fix applied in the session.",
                }
                for t in titles
            ]
            return json.dumps({"type": "retrieval_practice", "questions": questions})

        if fmt == "synthesis":
            return json.dumps(
                {
                    "type": "synthesis",
                    "prompt": (
                        "This idea has come up more than once: "
                        + ", ".join(titles)
                        + ". Without notes, write a short unified explanation of the underlying principle "
                        "and where you've applied it across your projects."
                    ),
                    "related_titles": titles,
                }
            )

        if fmt == "mcq":
            questions = []
            distractor_pool = [
                "It only applies when the code runs in production",
                "It is handled automatically by the framework with no configuration",
                "It was a limitation of the programming language itself",
            ]
            for t in titles:
                correct = summaries.get(t) or f"The approach captured in '{t}' from your own session"
                questions.append(
                    {
                        "question": f"Which statement best describes '{t}'?",
                        "choices": [correct[:180], *distractor_pool],
                        "correct_index": 0,
                        "explanation": f"This comes directly from your session: {correct[:200]}",
                    }
                )
            return json.dumps({"type": "mcq", "questions": questions})

        if fmt == "diagram":
            safe = [re.sub(r"[^a-zA-Z0-9 _-]", "", t)[:40] or "node" for t in titles]
            nodes = "\n".join(f'  N{i}["{t}"]' for i, t in enumerate(safe))
            edges = "\n".join(f"  N{i} --> N{i + 1}" for i in range(len(safe) - 1)) if len(safe) > 1 else ""
            mermaid = f"flowchart TD\n{nodes}\n{edges}".rstrip()
            return json.dumps(
                {
                    "type": "diagram",
                    "mermaid": mermaid,
                    "explanation": "Component relationship derived from the knowledge units in this scope. "
                    "Before revealing, sketch from memory how these pieces connect.",
                    "recall_prompt": "From memory: how do these components interact, and in what order does data flow?",
                }
            )

        return json.dumps({"type": "qa", "questions": [{"question": f"Explain {titles[0]}.", "expected_points": [], "kind": "recall"}]})
