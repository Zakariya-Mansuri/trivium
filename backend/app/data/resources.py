"""Curated learning-resource catalog — credible sources only.

Every entry is from a recognized institution, official documentation, a widely
respected book, or an established free-education platform. Matching is by
topic keywords against the user's weak knowledge areas, or by skill for the
language/prompting reports.
"""

# type: course | video | article | book | docs
# skill: coding | language | prompting
CATALOG: list[dict] = [
    # --- Python / backend ---
    {"title": "MIT 6.100L — Introduction to CS and Programming Using Python", "provider": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/courses/6-100l-introduction-to-cs-and-programming-using-python-fall-2022/", "type": "course", "skill": "coding", "topics": ["python", "programming basics", "functions", "recursion"]},
    {"title": "MIT 6.006 — Introduction to Algorithms", "provider": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/", "type": "course", "skill": "coding", "topics": ["algorithms", "data structures", "complexity", "optimization", "n+1"]},
    {"title": "FastAPI Official Tutorial", "provider": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "docs", "skill": "coding", "topics": ["fastapi", "api", "rest", "middleware", "dependency injection", "async", "uvicorn"]},
    {"title": "Python asyncio Documentation", "provider": "Python.org", "url": "https://docs.python.org/3/library/asyncio.html", "type": "docs", "skill": "coding", "topics": ["async", "asyncio", "concurrency", "event loop"]},
    {"title": "Fluent Python (Luciano Ramalho)", "provider": "O'Reilly (book)", "url": "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/", "type": "book", "skill": "coding", "topics": ["python", "decorator", "generator", "closure", "idiomatic"]},
    # --- Web / frontend ---
    {"title": "CS50's Web Programming with Python and JavaScript", "provider": "Harvard OpenCourseWare (edX)", "url": "https://cs50.harvard.edu/web/", "type": "course", "skill": "coding", "topics": ["web", "javascript", "react", "api", "sql", "django"]},
    {"title": "React Official Docs — Learn React", "provider": "react.dev", "url": "https://react.dev/learn", "type": "docs", "skill": "coding", "topics": ["react", "hooks", "state management", "component", "props", "useeffect", "reducer"]},
    {"title": "MDN Web Docs — JavaScript Guide", "provider": "Mozilla MDN", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "type": "docs", "skill": "coding", "topics": ["javascript", "typescript", "dom", "promise", "closure"]},
    {"title": "Eloquent JavaScript (Marijn Haverbeke, free online)", "provider": "eloquentjavascript.net", "url": "https://eloquentjavascript.net/", "type": "book", "skill": "coding", "topics": ["javascript", "programming basics", "async", "dom"]},
    # --- Databases ---
    {"title": "CMU 15-445 — Database Systems", "provider": "Carnegie Mellon University", "url": "https://15445.courses.cs.cmu.edu/", "type": "course", "skill": "coding", "topics": ["database", "sql", "postgresql", "index", "transaction", "query optimization"]},
    {"title": "Stanford — Databases: Relational Databases and SQL", "provider": "Stanford Online (edX)", "url": "https://www.edx.org/learn/relational-databases/stanford-university-databases-relational-databases-and-sql", "type": "course", "skill": "coding", "topics": ["sql", "database", "relational", "postgresql", "orm", "migration"]},
    {"title": "Use The Index, Luke — SQL Indexing Explained", "provider": "use-the-index-luke.com", "url": "https://use-the-index-luke.com/", "type": "article", "skill": "coding", "topics": ["index", "sql", "performance", "n+1", "query"]},
    # --- Security / auth ---
    {"title": "OWASP Cheat Sheet Series — Authentication", "provider": "OWASP Foundation", "url": "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html", "type": "docs", "skill": "coding", "topics": ["authentication", "security", "password", "session", "bcrypt", "hashing"]},
    {"title": "JWT Handbook / Introduction", "provider": "jwt.io", "url": "https://jwt.io/introduction", "type": "article", "skill": "coding", "topics": ["jwt", "token", "oauth", "authorization"]},
    {"title": "Stanford CS 253 — Web Security", "provider": "Stanford University", "url": "https://web.stanford.edu/class/cs253/", "type": "course", "skill": "coding", "topics": ["security", "web security", "xss", "cors", "csrf", "firewall"]},
    # --- Systems / architecture / networking ---
    {"title": "Designing Data-Intensive Applications (Martin Kleppmann)", "provider": "O'Reilly (book)", "url": "https://dataintensive.net/", "type": "book", "skill": "coding", "topics": ["architecture", "distributed", "cache", "queue", "system design", "scaling", "pipeline"]},
    {"title": "MIT 6.824 — Distributed Systems (video lectures)", "provider": "MIT (YouTube)", "url": "https://www.youtube.com/playlist?list=PLrw6a1wE39_tb2fErI4-WkMbsvGQk9_UB", "type": "video", "skill": "coding", "topics": ["distributed", "consensus", "replication", "system design"]},
    {"title": "Computer Networking: a Top-Down Approach — free lectures", "provider": "Kurose & Ross (UMass)", "url": "https://gaia.cs.umass.edu/kurose_ross/online_lectures.htm", "type": "video", "skill": "coding", "topics": ["networking", "http", "tcp", "dns", "port", "firewall", "router"]},
    {"title": "The Twelve-Factor App", "provider": "twelve-factor.net (Heroku)", "url": "https://12factor.net/", "type": "article", "skill": "coding", "topics": ["deployment", "config", "environment", "architecture", "devops"]},
    {"title": "Docker Official Getting Started Guide", "provider": "Docker Documentation", "url": "https://docs.docker.com/get-started/", "type": "docs", "skill": "coding", "topics": ["docker", "container", "deployment", "kubernetes"]},
    # --- Code quality / craft ---
    {"title": "Clean Code (Robert C. Martin)", "provider": "Pearson (book)", "url": "https://www.oreilly.com/library/view/clean-code-a/9780136083238/", "type": "book", "skill": "coding", "topics": ["clean code", "refactoring", "naming", "code quality", "pattern"]},
    {"title": "The Pragmatic Programmer (Hunt & Thomas)", "provider": "Pearson (book)", "url": "https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/", "type": "book", "skill": "coding", "topics": ["craft", "debugging", "testing", "pattern", "career"]},
    {"title": "Google Engineering Practices — Code Review Guide", "provider": "Google", "url": "https://google.github.io/eng-practices/review/", "type": "docs", "skill": "coding", "topics": ["code review", "code quality", "collaboration"]},
    {"title": "freeCodeCamp — Full Curriculum", "provider": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/", "type": "course", "skill": "coding", "topics": ["web", "javascript", "python", "programming basics", "projects"]},
    # --- Learning how to learn ---
    {"title": "Learning How to Learn (Barbara Oakley)", "provider": "McMaster University / Coursera", "url": "https://www.coursera.org/learn/learning-how-to-learn", "type": "course", "skill": "coding", "topics": ["learning", "memory", "spaced repetition", "chunking"]},
    # --- Language / writing / communication ---
    {"title": "Purdue OWL — Online Writing Lab", "provider": "Purdue University", "url": "https://owl.purdue.edu/owl/purdue_owl.html", "type": "docs", "skill": "language", "topics": ["grammar", "punctuation", "clarity", "structure", "writing"]},
    {"title": "The Elements of Style (Strunk & White)", "provider": "Classic reference (book)", "url": "https://www.gutenberg.org/ebooks/37134", "type": "book", "skill": "language", "topics": ["conciseness", "clarity", "style", "writing"]},
    {"title": "On Writing Well (William Zinsser)", "provider": "HarperCollins (book)", "url": "https://www.harpercollins.com/products/on-writing-well-william-zinsser", "type": "book", "skill": "language", "topics": ["clarity", "simplicity", "nonfiction writing"]},
    {"title": "MIT 21W.011 — Writing and Rhetoric: Rhetoric and Contemporary Issues", "provider": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/courses/21w-011-writing-and-rhetoric-rhetoric-and-contemporary-issues-spring-2010/", "type": "course", "skill": "language", "topics": ["rhetoric", "argument", "structure", "writing"]},
    {"title": "English for Career Development", "provider": "University of Pennsylvania / Coursera", "url": "https://www.coursera.org/learn/careerdevelopment", "type": "course", "skill": "language", "topics": ["professional english", "vocabulary", "communication"]},
    {"title": "Technical Writing Courses for Engineers", "provider": "Google Developers", "url": "https://developers.google.com/tech-writing", "type": "course", "skill": "language", "topics": ["technical writing", "clarity", "documentation", "structure", "conciseness"]},
    {"title": "Yale — Introduction to Psychology (language & cognition lectures)", "provider": "Yale Open Courses", "url": "https://oyc.yale.edu/introduction-psychology/psyc-110", "type": "course", "skill": "language", "topics": ["cognition", "language", "communication"]},
    # --- Prompting ---
    {"title": "Anthropic — Prompt Engineering Overview", "provider": "Anthropic Documentation", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "type": "docs", "skill": "prompting", "topics": ["prompt engineering", "context", "examples", "chain of thought"]},
    {"title": "OpenAI — Prompt Engineering Guide", "provider": "OpenAI Documentation", "url": "https://platform.openai.com/docs/guides/prompt-engineering", "type": "docs", "skill": "prompting", "topics": ["prompt engineering", "instructions", "output format", "specificity"]},
    {"title": "ChatGPT Prompt Engineering for Developers", "provider": "DeepLearning.AI (Andrew Ng)", "url": "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/", "type": "course", "skill": "prompting", "topics": ["prompt engineering", "iteration", "summarizing", "transforming"]},
    {"title": "Prompt Engineering Guide (DAIR.AI)", "provider": "promptingguide.ai", "url": "https://www.promptingguide.ai/", "type": "docs", "skill": "prompting", "topics": ["prompt engineering", "few-shot", "chain of thought", "techniques"]},
    {"title": "Google — Prompting Essentials", "provider": "Google / Coursera", "url": "https://www.coursera.org/learn/google-prompting-essentials", "type": "course", "skill": "prompting", "topics": ["prompt engineering", "context", "iteration", "workflow"]},
]


def match_resources(keywords: list[str], skill: str | None = None, limit: int = 6) -> list[dict]:
    """Scores catalog entries by keyword-topic overlap; optionally filtered by skill."""
    lowered = [k.lower() for k in keywords if k]
    scored = []
    for entry in CATALOG:
        if skill is not None and entry["skill"] != skill:
            continue
        score = 0
        for kw in lowered:
            for topic in entry["topics"]:
                if topic in kw or kw in topic:
                    score += 2 if topic == kw else 1
        if skill is not None and not lowered:
            score = 1  # skill-level default recommendations
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda pair: -pair[0])
    return [entry for _, entry in scored[:limit]]
