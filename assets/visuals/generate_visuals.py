#!/usr/bin/env python3
"""Generate the course diagram set as clean, branded SVGs.

Style: white canvas, navy (#0B1F4A) primary boxes with white text,
light blue (#E0F2FE) secondary boxes with navy text, cyan (#0891B2)
arrows, amber (#F59E0B) accent for warnings/gates. Every diagram is a
simple grid layout so text never overlaps. Run: python3 generate_visuals.py
"""
import os

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = "#0B1F4A"
LIGHT = "#E0F2FE"
CYAN = "#0891B2"
AMBER = "#F59E0B"
GREY = "#475569"
FONT = "Segoe UI, Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class SVG:
    def __init__(self, w, h, title, subtitle):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            f'<rect width="{w}" height="{h}" fill="#FFFFFF"/>',
            f'<text x="40" y="52" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">{esc(title)}</text>',
            f'<text x="40" y="82" font-family="{FONT}" font-size="17" fill="{GREY}">{esc(subtitle)}</text>',
            f'<rect x="40" y="98" width="90" height="5" fill="{CYAN}"/>',
        ]

    def box(self, x, y, w, h, label, sub="", style="navy"):
        fill, tcol, scol = (NAVY, "#FFFFFF", "#BFE3F2") if style == "navy" else (LIGHT, NAVY, "#33506E")
        if style == "amber":
            fill, tcol, scol = "#FEF3C7", NAVY, "#7C5A03"
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}"/>')
        if sub:
            self.parts.append(f'<text x="{x + w/2}" y="{y + h/2 - 4}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="{tcol}">{esc(label)}</text>')
            self.parts.append(f'<text x="{x + w/2}" y="{y + h/2 + 20}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{scol}">{esc(sub)}</text>')
        else:
            self.parts.append(f'<text x="{x + w/2}" y="{y + h/2 + 7}" text-anchor="middle" font-family="{FONT}" font-size="19" font-weight="700" fill="{tcol}">{esc(label)}</text>')

    def arrow(self, x1, y1, x2, y2, label=""):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{CYAN}" stroke-width="3" marker-end="url(#ah)"/>')
        if label:
            self.parts.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2 - 8}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{CYAN}">{esc(label)}</text>')

    def note(self, x, y, text):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="15" fill="{GREY}">{esc(text)}</text>')

    def save(self, name):
        defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" '
                f'fill="{CYAN}"/></marker></defs>')
        body = "\n".join(self.parts[:2] + [defs] + self.parts[2:]) + "\n</svg>"
        with open(os.path.join(OUT, name), "w") as f:
            f.write(body)
        print("wrote", name)


def hflow(name, title, subtitle, steps, note=""):
    """Horizontal chain of boxes with arrows between them."""
    n = len(steps)
    w = 1200
    bw = (w - 80 - (n - 1) * 50) // n
    s = SVG(w, 300, title, subtitle)
    y = 140
    for i, (label, sub) in enumerate(steps):
        x = 40 + i * (bw + 50)
        s.box(x, y, bw, 90, label, sub, "navy" if i in (0, n - 1) else "light")
        if i < n - 1:
            s.arrow(x + bw + 4, y + 45, x + bw + 46, y + 45)
    if note:
        s.note(40, 275, note)
    s.save(name)


# 1. Course map: 11 modules to the capstone
s = SVG(1200, 560, "Course map: 36 lessons, one arc", "Every module builds one piece of the capstone business assistant. Nothing is throwaway.")
mods = [
    ("M0 Setup", "00"), ("M1 Foundations", "01-08"), ("M2 Architecture", "09-11"),
    ("M3 Tools + MCP", "12-14"), ("M4 Memory", "15-17"), ("M5 RAG", "18-20"),
    ("M6 Multi-agent", "21-23"), ("M7 Evaluation", "24-26"), ("M8 Production", "27-30"),
    ("M9 Company track", "31-33"),
]
for i, (label, sub) in enumerate(mods):
    row, col = divmod(i, 5)
    x, y = 40 + col * 228, 140 + row * 130
    s.box(x, y, 200, 90, label, "Lessons " + sub, "light")
    if col < 4:
        s.arrow(x + 204, y + 45, x + 224, y + 45)
    if col == 4 and row == 0:
        s.arrow(x + 100, y + 94, x + 100, y + 126)
s.box(380, 410, 440, 95, "CAPSTONE", "Lessons 34-36: build, evaluate, ship", "navy")
s.arrow(600, 360, 600, 406)
s.save("course-map.svg")

# 2. Agent vs chatbot vs workflow
s = SVG(1200, 430, "Agent, chatbot, or workflow?", "Same tools, three different shapes. Pick by how much judgement the job needs.")
cols = [
    ("CHATBOT", "Answers questions", "No tools, no actions", "Fixed knowledge"),
    ("WORKFLOW", "Fixed steps, every time", "Tools run in a set order", "Breaks on surprises"),
    ("AGENT", "Pursues a goal", "Chooses tools and order", "Adapts within guardrails"),
]
for i, (h, a, b, c) in enumerate(cols):
    x = 40 + i * 380
    style = "navy" if i == 2 else "light"
    s.box(x, 140, 340, 80, h, "", style)
    for j, line in enumerate([a, b, c]):
        s.note(x + 20, 265 + j * 45, "- " + line)
s.note(40, 400, "Lesson 01 teaches you to tell them apart before you build the wrong one.")
s.save("agent-vs-chatbot-vs-workflow.svg")

# 3. How LLMs work
hflow("how-llms-work.svg", "How an LLM answers: tokens in, probabilities out",
      "The model predicts the next token, again and again. It does not look anything up.",
      [("Your text", "split into tokens"), ("Tokens", "numbers the model reads"),
       ("The model", "predicts what fits next"), ("Next token", "picked by probability"),
       ("Repeat", "until the answer is done")],
      "Temperature controls how adventurous the pick is. Lesson 03 builds this mental model properly.")

# 4. The agent loop
s = SVG(1200, 480, "The agent loop", "Everything an agent does is this loop, repeated until the goal is met or a limit stops it.")
s.box(440, 140, 320, 90, "THINK", "Reason about the goal", "navy")
s.box(820, 280, 320, 90, "ACT", "Call a tool or answer", "light")
s.box(440, 400 - 60, 320, 90, "OBSERVE", "Read the tool result", "light")
s.box(60, 280, 320, 90, "PERCEIVE", "Goal + context + memory", "light")
s.arrow(600, 234, 760, 300)
s.arrow(820, 325, 764, 372)
s.arrow(436, 385, 384, 330)
s.arrow(220, 276, 436, 190)
s.note(40, 465, "Guardrails and step limits sit around the loop. Lesson 09 builds it; Lesson 26 fences it.")
s.save("agent-loop.svg")

# 5. Tool calling flow
hflow("tool-calling-flow.svg", "Tool calling: the model asks, your code acts",
      "The model never touches the real world directly. Your program runs every tool and checks every result.",
      [("User goal", "in plain language"), ("Model", "requests a tool call"),
       ("Your code", "validates and runs it"), ("Real tool", "calendar, CRM, API"),
       ("Result", "goes back to the model")],
      "MCP (Lesson 14) standardises the middle steps so tools plug into any agent.")

# 6. Memory types
s = SVG(1200, 430, "Three kinds of memory", "Confusing these is the most common beginner design mistake.")
rows = [
    ("CONTEXT WINDOW", "This conversation, right now", "Gone when the session ends", "light"),
    ("SHORT-TERM STORE", "Notes within one task or day", "Summaries, scratchpads, files", "light"),
    ("LONG-TERM MEMORY", "Facts kept across sessions", "Vector store or database, retrieved on need", "navy"),
]
for i, (h, a, b, style) in enumerate(rows):
    y = 135 + i * 88
    s.box(40, y, 300, 68, h, "", style)
    s.note(370, y + 30, a)
    s.note(370, y + 55, b)
s.note(40, 415, "Lessons 15 to 17 build each kind, then Lesson 17 teaches context engineering: choosing what earns a place.")
s.save("memory-types.svg")

# 7. RAG pipeline
hflow("rag-pipeline.svg", "RAG: answer from your documents, with receipts",
      "Retrieval-augmented generation grounds the model in sources you control, instead of its memory of training.",
      [("Documents", "your real sources"), ("Chunk + index", "searchable pieces"),
       ("Question", "from the user"), ("Retrieve", "the few relevant chunks"),
       ("Answer", "with citations")],
      "Lesson 18 builds this from scratch. Lesson 20 teaches grounding checks so citations actually support the answer.")

# 8. Multi-agent handoffs
s = SVG(1200, 430, "Multi-agent: roles and handoffs", "Split work when one agent's job gets too wide. Every handoff passes context explicitly.")
s.box(60, 170, 300, 95, "SUPERVISOR", "Splits and routes the work", "navy")
s.box(470, 130, 300, 95, "RESEARCHER", "Finds and checks facts", "light")
s.box(470, 260, 300, 95, "WRITER", "Drafts in the house style", "light")
s.box(880, 195, 280, 95, "REVIEW", "Human or judge gate", "amber")
s.arrow(364, 200, 466, 175)
s.arrow(364, 240, 466, 300)
s.arrow(774, 175, 876, 225)
s.arrow(774, 305, 876, 260)
s.note(40, 400, "Lesson 22 builds the researcher-writer pair. Lesson 23 is the honest catalogue of how multi-agent systems fail.")
s.save("multi-agent-handoffs.svg")

# 9. Evaluation loop
s = SVG(1200, 430, "Evaluation: test outcomes, not vibes", "A scenario suite you rerun after every change is what makes an agent safe to improve.")
steps = [("Scenarios", "real tasks, fixed inputs"), ("Run the agent", "same way every time"),
         ("Grade outcomes", "booked? correct? safe?"), ("Fix one thing", "smallest change first"),
         ("Rerun all", "catch regressions")]
bw = 208
for i, (label, sub) in enumerate(steps):
    x = 40 + i * (bw + 22)
    s.box(x, 150, bw, 95, label, sub, "navy" if i == 2 else "light")
    if i < 4:
        s.arrow(x + bw + 3, 197, x + bw + 19, 197)
s.box(330, 300, 540, 80, "HUMAN REVIEW GATE", "Low-confidence and high-stakes cases go to a person", "amber")
s.arrow(600, 249, 600, 296)
s.note(40, 415, "Lessons 24 to 26: outcome tests, LLM-as-judge with human review, guardrails and approvals.")
s.save("evaluation-loop.svg")

# 10. Production agent
s = SVG(1200, 540, "A production agent is layers, not a prompt", "Deployment, tracing, security and cost control are what separate a demo from a system.")
layers = [
    ("DEPLOYMENT", "Runs on a schedule or a server, not your laptop", "light"),
    ("OBSERVABILITY", "Every run traced: inputs, tool calls, outputs, cost", "light"),
    ("SECURITY", "Injection defence, least-privilege tools, approvals", "amber"),
    ("THE AGENT", "Loop, tools, memory, guardrails from Modules 2 to 7", "navy"),
]
for i, (h, sub, style) in enumerate(layers):
    y = 130 + i * 88
    s.box(140, y, 920, 74, h, sub, style)
s.note(40, 515, "Lessons 27 to 30 add one layer at a time, in this order.")
s.save("production-layers.svg")

# 11. Capstone flow
hflow("capstone-flow.svg", "The capstone: a business assistant that does the whole job",
      "Lessons 34 to 36 assemble everything into one deployed assistant for a fictional service company.",
      [("Enquiry arrives", "form, DM, or email"), ("Capture", "structured record"),
       ("Qualify", "score 0-100, route it"), ("Book", "real calendar slot"),
       ("Follow up", "until answered")],
      "HOT leads (80+) go straight to a human with a full summary. The evaluation suite from Lesson 35 grades every step.")
print("done")
