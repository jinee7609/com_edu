import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT.parents[1] / "2022개정_정보과_인출연습_100제.md"
CONTENT = PROJECT / "content" / "questions.md"
OUTPUT = PROJECT / "data" / "questions.ts"

text = SOURCE.read_text(encoding="utf-8")
problem_text, answer_text = text.split("# 정답·해설 및 채점 핵심어", 1)

questions = []
section = ""
current = None
for line in problem_text.splitlines():
    if line.startswith("## "):
        section = line[3:].strip()
    match = re.match(r"^(\d+)\.\s+(.+)$", line)
    if match:
        if current:
            questions.append(current)
        current = {
            "id": int(match.group(1)),
            "section": section,
            "prompt": match.group(2).strip(),
            "standard": "",
            "answer": "",
            "keywords": "",
        }
    elif current and line.startswith("   ") and not line.strip().startswith("답:"):
        current["prompt"] += " " + line.strip()
if current:
    questions.append(current)

answers = {}
current_id = None
for line in answer_text.splitlines():
    match = re.match(r"^###\s+(\d+)번$", line)
    if match:
        current_id = int(match.group(1))
        answers[current_id] = {}
    elif current_id and line.startswith("- 관련 내용/성취기준:"):
        answers[current_id]["standard"] = line.split(":", 1)[1].strip()
    elif current_id and line.startswith("- 예시 답안:"):
        answers[current_id]["answer"] = line.split(":", 1)[1].strip()
    elif current_id and line.startswith("- 채점 핵심어:"):
        answers[current_id]["keywords"] = line.split(":", 1)[1].strip()

for question in questions:
    question.update(answers.get(question["id"], {}))

assert len(questions) == 100
assert all(q["answer"] for q in questions)

CONTENT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
CONTENT.write_text(text, encoding="utf-8")
OUTPUT.write_text(
    "export type Question = { id: number; section: string; prompt: string; standard: string; answer: string; keywords: string };\n\n"
    + "export const questions: Question[] = "
    + json.dumps(questions, ensure_ascii=False, indent=2)
    + ";\n",
    encoding="utf-8",
)
