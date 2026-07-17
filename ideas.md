 # 🧠 AGENT SUITE SPECIFICATION
 # Focus: 3 Advanced Agent Systems
 
 This project contains three production-grade AI agent systems built around tool-use, planning, and self-correction.
 
 ---
 
 # =========================================
 # 1. 🔍 RESEARCH AGENT WITH CRITIC LOOP
 # =========================================
 
 ## 🎯 Goal
 Build a research agent that produces **fact-checked, structured, citation-backed reports** using a built-in critic system to detect hallucinations and inconsistencies.
 
 ---
 
 ## 🧱 Architecture
 
 USER QUERY
     ↓
 Planner (query decomposition)
     ↓
 Research Agent (web/tool execution)
     ↓
 Evidence Collector (stores sources)
     ↓
 Synthesis Agent (draft report)
     ↓
 Critic Agent (verification + contradiction check)
     ↓
 If fail → refine query loop
     ↓
 Final report
 
 ---
 
 ## 🧠 Core Components
 
 ### 1. Planner
 - Breaks question into sub-questions
 - Example:
   "Impact of AI on jobs"
   → automation trends
   → industry impact
   → stats + studies
 
 ---
 
 ### 2. Research Agent
 - Uses:
   - web search tool
   - document parsing
 - Extracts:
   - facts
   - quotes
   - structured notes
 
 ---
 
 ### 3. Evidence Store
 - stores:
   - URLs
   - extracted facts
   - confidence score per fact
 
 ---
 
 ### 4. Synthesis Agent
 - Converts evidence → structured report
 - format:
   - headings
   - bullet insights
   - citations
 
 ---
 
 ### 5. Critic Agent (KEY)
 Checks:
 - missing citations
 - contradictions
 - weak evidence claims
 - hallucinated facts
 
 Output:
 ```json
 {
   "pass": false,
   "issues": [
     "claim X not supported by sources"
   ]
 }
 ```

:repeat: Loop Logic
repeat until:
 critic passes OR max_iterations reached (3–5)

:package: Output Format
 Executive summary
 Key findings
 Evidence table
 Sources
 Confidence score

=========================================
2. :robot_face: MULTI-AGENT STARTUP SIMULATOR
=========================================
:dart: Goal
Simulate a full startup team of AI agents that collaboratively design, build, and market a product from a single idea.

:bricks: Architecture
USER IDEA
↓
CEO Agent (vision + strategy)
↓
Product Manager Agent
↓
Task decomposition
↓
Parallel agent execution:
├── Engineer Agent
├── Designer Agent
├── Marketer Agent
├── Analyst Agent
↓
Critic Agent (cross-check consistency)
↓
Final Startup Output Package

:brain: Agents
1. CEO Agent
• defines:
vision
target audience
monetization model

2. Product Manager Agent
• converts idea → roadmap
• defines:
MVP features
sprint tasks

3. Engineer Agent
• outputs:
architecture
backend/frontend structure
sample code

4. Designer Agent
• creates:
UI descriptions
layout specs
UX flow

5. Marketer Agent
• generates:
landing page copy
ads
positioning strategy

6. Analyst Agent
• evaluates:
market demand
competition
pricing model

7. Critic Agent
Checks:
 inconsistent business logic
 unrealistic assumptions
 conflicting outputs between agents

:repeat: Execution Flow
 CEO defines startup idea
 PM breaks into roadmap
 agents execute in parallel
 outputs merged
 critic validates
 final startup dossier generated

:package: Output
 Startup summary
 Product roadmap
 Architecture diagram (text-based)
 UI mock description
 Marketing plan
 Business model

# =========================================
# 3. :computer: PERSONAL AI CODING / GITHUB AGENT
# =========================================
:dart: Goal
An autonomous coding agent that can:
 understand GitHub repositories
 implement features
 fix bugs
 run tests
 iterate automatically

:bricks: Architecture
USER REQUEST
↓
Repo Loader Agent
↓
Codebase Analyzer
↓
Planner Agent
↓
Coding Agent (implementation)
↓
Test Runner Tool
↓
Debugger Agent (if failure)
↓
Critic Agent (code review)
↓
Final PR-ready output

:brain: Core Modules
1. Repo Loader
 clones GitHub repo
 builds file tree
 extracts relevant files

2. Codebase Analyzer
• summarizes:
architecture
dependencies
key modules

3. Planner Agent
• converts request into steps:
files to modify
logic required

4. Coding Agent
• writes:
functions
classes
patches
• follows repo style

5. Test Runner
• runs:
unit tests
lint checks
• returns errors

6. Debugger Loop
IF error:
→ analyze stack trace
→ patch code
→ rerun tests
(max 3–5 iterations)

7. Critic Agent
Checks:
 code quality
 redundancy
 security issues
 correctness vs requirement

:repeat: Execution Loop
plan → implement → test → debug → review → finalize

:package: Output
 modified codebase
 patch summary
 explanation of changes
 optional PR description

=========================================
:brain: SHARED INFRASTRUCTURE (ALL 3)
=========================================
:jigsaw: Common Components
1. Tool Layer
 web search
 file system
 GitHub API
 code execution sandbox

2. Memory
 session memory (current task)
 optional vector store (past runs)

3. Critic Agent Pattern
Used in all 3 systems:
 validates outputs
 enforces correctness
 triggers retry loops

4. LLM Orchestration Pattern
ALL systems follow:
PLAN → EXECUTE → VERIFY → RETRY (if needed)

=========================================
:rocket: FINAL OUTCOME
=========================================
This suite demonstrates:
 autonomous reasoning systems
 multi-agent collaboration
 real-world tool use
 self-correcting loops
 production-grade AI architecture

END OF SPEC
 
 ---
 
 If you want next step, I can turn this into:
 
 - a **clean GitHub repo structure (folders + starter code)**
 - or a **MVP build plan (7–10 days execution roadmap)**
 - or a **demo script that makes recruiters instantly understand it**
 
 Just tell me.