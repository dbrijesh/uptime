# 🔍 Cartographer vs Standalone Analyzer: Comprehensive Comparison

**Date:** 2026-01-26  
**Purpose:** Ensure standalone analyzer replicates Cartographer plugin functionality

---

## 📋 Executive Summary

### Cartographer Plugin (Claude Code)
- **Purpose:** Maps and documents codebases using parallel AI subagents in Claude Code environment
- **Architecture:** Opus orchestrates, Sonnet subagents read and analyze
- **Integration:** Native Claude Code plugin with skill system
- **Output:** `docs/CODEBASE_MAP.md` + updates to `CLAUDE.md`

### Standalone Analyzer
- **Purpose:** Independent multi-agent codebase analysis without Claude Code dependency
- **Architecture:** Python-based multi-agent system using LangGraph/AsyncIO
- **Integration:** Standalone CLI tool, works with any LLM provider
- **Output:** Configurable markdown reports

---

## 🎯 Core Workflow Comparison

### Cartographer Workflow (5 Steps)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCAN CODEBASE                                            │
│    - Run scan-codebase.py script                           │
│    - Generate file tree with token counts                  │
│    - Respect .gitignore                                     │
│    - Skip binary files, large files (>1MB, >50k tokens)    │
├─────────────────────────────────────────────────────────────┤
│ 2. PLAN SUBAGENT ASSIGNMENTS                               │
│    - Analyze scan output                                    │
│    - Group files by module/directory                       │
│    - Target ~150k tokens per Sonnet subagent               │
│    - Balance token counts across groups                    │
├─────────────────────────────────────────────────────────────┤
│ 3. SPAWN SONNET SUBAGENTS IN PARALLEL                      │
│    - Use Task tool with subagent_type: "Explore"          │
│    - Each subagent analyzes assigned files                 │
│    - Extract: purpose, exports, imports, patterns          │
│    - Return structured markdown                            │
├─────────────────────────────────────────────────────────────┤
│ 4. SYNTHESIZE REPORTS                                       │
│    - Merge all subagent outputs                            │
│    - Deduplicate overlapping analysis                      │
│    - Build architecture diagram                            │
│    - Extract navigation paths                              │
├─────────────────────────────────────────────────────────────┤
│ 5. WRITE CODEBASE_MAP.md                                    │
│    - Generate docs/CODEBASE_MAP.md                         │
│    - Update CLAUDE.md with summary                         │
│    - Include frontmatter with timestamp                    │
└─────────────────────────────────────────────────────────────┘
```

### Standalone Analyzer Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCANNER AGENT                                            │
│    - Scan directory recursively                            │
│    - Count tokens using tiktoken                           │
│    - Detect languages and tech stack                       │
│    - Exclude predefined directories                        │
├─────────────────────────────────────────────────────────────┤
│ 2. PLANNER AGENT (if using LangGraph)                      │
│    - Analyze scan results                                   │
│    - Distribute work to specialized agents                 │
│    - Create analysis plan                                  │
│                                                             │
│ OR: ORCHESTRATOR (if using main.py)                        │
│    - Partition files into chunks (~100k tokens each)       │
│    - Launch multiple agent instances per chunk             │
├─────────────────────────────────────────────────────────────┤
│ 3. PARALLEL ANALYSIS AGENTS                                │
│    - Entity Analysis Agent (extracts domain models)        │
│    - API Analysis Agent (extracts endpoints)               │
│    - Business Logic Agent (extracts commands/queries)      │
│    - Architecture Agent (identifies patterns)              │
│    - Integration Agent (maps dependencies)                 │
│    - Run concurrently via asyncio.gather()                 │
├─────────────────────────────────────────────────────────────┤
│ 4. SYNTHESIS AGENT                                          │
│    - Combine all agent results                             │
│    - Deduplicate entities and components                   │
│    - Generate ER diagrams                                  │
│    - Create comprehensive report                           │
├─────────────────────────────────────────────────────────────┤
│ 5. REPORT GENERATION                                        │
│    - Write to specified output file                        │
│    - Include mermaid diagrams                              │
│    - Structured markdown format                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 Detailed Feature Analysis

### 1. File Scanning & Discovery

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Recursive file scanning** | ✅ Yes | ✅ Yes | ✅ **MATCH** |
| **Gitignore support** | ✅ Yes (parses .gitignore) | ⚠️ Partial (hardcoded excludes) | ⚠️ **GAP** |
| **Default excludes** | ✅ node_modules, dist, build, etc. | ✅ Same defaults | ✅ **MATCH** |
| **Binary file detection** | ✅ Content sniffing + extension | ✅ Extension-based | ⚠️ **MINOR GAP** |
| **Token counting** | ✅ tiktoken (cl100k_base) | ✅ tiktoken (gpt-4 encoding) | ✅ **MATCH** |
| **File size limits** | ✅ 1MB, 50k tokens | ✅ Configurable (default 150k bytes) | ⚠️ **DIFFERENT** |
| **Text file detection** | ✅ 100+ extensions + content check | ✅ 80+ extensions | ⚠️ **MINOR GAP** |
| **Output format** | ✅ JSON with metadata | ✅ Dict with metadata | ✅ **MATCH** |

**Key Differences:**
- Cartographer: More sophisticated .gitignore parsing with pattern matching
- Standalone: Uses hardcoded exclude list, less flexible
- **Recommendation:** Enhance standalone scanner to parse .gitignore

---

### 2. Work Distribution & Load Balancing

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Chunking strategy** | ✅ By module/directory | ✅ By token count (greedy) | ⚠️ **DIFFERENT** |
| **Token budget per agent** | ✅ 150k tokens (Sonnet safe) | ✅ 100-120k tokens | ✅ **SIMILAR** |
| **Load balancing** | ⚠️ Manual grouping | ✅ Greedy algorithm | ✅ **BETTER** |
| **Subagent model** | ✅ Sonnet (200k context) | ✅ gpt-4-turbo (128k context) | ⚠️ **DIFFERENT** |
| **Orchestrator model** | ✅ Opus plans | ✅ Same model for all | ⚠️ **DIFFERENT** |
| **Small codebase handling** | ✅ Still uses 1 Sonnet subagent | ⚠️ Can use 0 agents (direct) | ⚠️ **DIFFERENT** |

**Key Differences:**
- Cartographer: Groups by semantic units (modules), preserves related code together
- Standalone: Groups by token balance, may split modules
- **Recommendation:** Add module-aware grouping to standalone analyzer

---

### 3. Parallel Agent Analysis

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Parallelization** | ✅ Task tool (parallel) | ✅ asyncio.gather() | ✅ **MATCH** |
| **Agent types** | ⚠️ Single type (generic analysis) | ✅ 5+ specialized agents | ✅ **BETTER** |
| **Analysis depth** | ✅ Purpose, exports, imports, patterns | ✅ Same + entities, APIs, validators | ✅ **BETTER** |
| **Language support** | ✅ Language-agnostic (LLM) | ✅ Language-agnostic (LLM) | ✅ **MATCH** |
| **Prompt engineering** | ✅ Detailed per-subagent prompts | ✅ Specialized per agent type | ✅ **MATCH** |
| **Error handling** | ⚠️ Not documented | ✅ Try-catch with fallbacks | ✅ **BETTER** |

**Key Differences:**
- Cartographer: Simpler agent model (all analyze same way)
- Standalone: More specialized agents (entity, API, business logic)
- **Recommendation:** Cartographer's approach is simpler, standalone's is more thorough

---

### 4. Analysis Capabilities

#### 4.1 What Cartographer Extracts

```markdown
Per file/module:
1. **Purpose**: One-line description
2. **Exports**: Key functions, classes, types exported
3. **Imports**: Notable dependencies
4. **Patterns**: Design patterns or conventions
5. **Gotchas**: Non-obvious behavior, edge cases, warnings

Cross-cutting:
- Module relationships
- Entry points and data flow
- Configuration dependencies
```

#### 4.2 What Standalone Extracts

```markdown
Entities:
- name, properties, type, inheritance, relationships

API Endpoints:
- method, route, handler, return_type, language

Commands/Queries (CQRS):
- name, type, return_type, dependencies

Validators:
- name, validates, rules

Tech Stack:
- languages, frameworks, packages, databases
```

| Analysis Type | Cartographer | Standalone | Status |
|--------------|-------------|------------|--------|
| **Domain Entities** | ⚠️ As part of exports | ✅ Dedicated extraction | ✅ **BETTER** |
| **API Endpoints** | ⚠️ Generic analysis | ✅ Structured extraction | ✅ **BETTER** |
| **Dependencies** | ✅ Imports documented | ✅ Package managers parsed | ✅ **MATCH** |
| **Design Patterns** | ✅ Identified | ⚠️ Inferred from structure | ⚠️ **GAP** |
| **Data Flow** | ✅ Documented | ⚠️ Basic | ⚠️ **GAP** |
| **Entry Points** | ✅ Identified | ⚠️ Basic | ⚠️ **GAP** |
| **Gotchas/Warnings** | ✅ Yes | ❌ No | ❌ **GAP** |

**Key Differences:**
- Cartographer: More holistic, contextual analysis
- Standalone: More structured, categorized extraction
- **Recommendation:** Add "gotchas" and "entry points" analysis to standalone

---

### 5. Synthesis & Report Generation

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Deduplication** | ✅ Yes | ✅ Yes (by name) | ✅ **MATCH** |
| **Architecture diagram** | ✅ Mermaid (high-level) | ✅ Mermaid (layered) | ✅ **MATCH** |
| **Directory structure** | ✅ Annotated tree | ⚠️ Basic list | ⚠️ **GAP** |
| **Module guide** | ✅ Per-module sections | ⚠️ Component tables | ⚠️ **DIFFERENT** |
| **Data flow diagrams** | ✅ Sequence diagrams | ⚠️ Basic | ⚠️ **GAP** |
| **Navigation guide** | ✅ "How to add feature" | ❌ No | ❌ **GAP** |
| **Conventions** | ✅ Naming, patterns, style | ❌ No | ❌ **GAP** |
| **ER Diagrams** | ⚠️ Not mentioned | ✅ Yes (from entities) | ✅ **BETTER** |
| **API Documentation** | ⚠️ Generic | ✅ Complete tables | ✅ **BETTER** |

**Key Differences:**
- Cartographer: More developer-friendly (how to navigate, conventions)
- Standalone: More analytical (complete catalogs, diagrams)
- **Recommendation:** Merge approaches - add navigation guide to standalone

---

### 6. Output Format & Documentation

#### Cartographer Output Structure

```markdown
---
last_mapped: YYYY-MM-DDTHH:MM:SSZ
total_files: N
total_tokens: N
---

# Codebase Map

> Auto-generated by Cartographer. Last mapped: [date]

## System Overview
[Mermaid diagram showing high-level architecture]

## Directory Structure
[Tree with purpose annotations]

## Module Guide
### [Module Name]
**Purpose**: [description]
**Entry point**: [file]
**Key files**: | File | Purpose | Tokens |
**Exports**: [key APIs]
**Dependencies**: [what it needs]
**Dependents**: [what needs it]

## Data Flow
[Mermaid sequence diagrams for key flows]

## Conventions
[Naming, patterns, style]

## Gotchas
[Non-obvious behaviors, warnings]

## Navigation Guide
**To add a new API endpoint**: [files to touch]
**To add a new component**: [files to touch]
**To modify auth**: [files to touch]
```

#### Standalone Output Structure

```markdown
# Multi-Agent Ultra-Comprehensive Codebase Map

**Generated:** YYYY-MM-DD HH:MM:SS
**Analyzer:** Multi-Agent Ultra-Comprehensive Analyzer

## Table of Contents
1. Executive Summary
2. Architecture Overview
3. Technology Stack
4. Component Catalog
5. API Specifications
6. Data Models
7. Business Logic
8. Development Guide

## Executive Summary
### Key Statistics
| Metric | Value |
| Total Files | N |
| Domain Entities | N |
| API Endpoints | N |

## Architecture Overview
### High-Level System Architecture
[Mermaid diagram - layered architecture]

## Technology Stack
### Complete Package List
[Tables grouped by ecosystem]

## Component Catalog
### Domain Entities
[ER Diagram]
[Entity Details Table]

## API Specifications
### API Endpoints
[Tables grouped by controller]

## Data Models
### Entity Relationships
[Per-entity details with properties]

## Business Logic
### Architecture Patterns Detected
- CQRS Pattern
- Validation Pattern

## Development Guide
[Basic instructions]
```

| Output Section | Cartographer | Standalone | Status |
|----------------|-------------|------------|--------|
| **Frontmatter metadata** | ✅ Yes (timestamps) | ❌ No | ❌ **GAP** |
| **System overview** | ✅ ASCII/Mermaid | ✅ Mermaid (layered) | ✅ **MATCH** |
| **Directory structure** | ✅ Annotated tree | ⚠️ List only | ⚠️ **GAP** |
| **Module documentation** | ✅ Per-module | ⚠️ Component tables | ⚠️ **DIFFERENT** |
| **Data flows** | ✅ Sequence diagrams | ❌ No | ❌ **GAP** |
| **Conventions** | ✅ Yes | ❌ No | ❌ **GAP** |
| **Gotchas** | ✅ Yes | ❌ No | ❌ **GAP** |
| **Navigation guide** | ✅ Task-based | ❌ No | ❌ **GAP** |
| **Statistics table** | ⚠️ In frontmatter | ✅ Dedicated section | ✅ **MATCH** |
| **ER diagrams** | ❌ No | ✅ Yes | ✅ **BETTER** |
| **Complete API tables** | ⚠️ Generic | ✅ Yes | ✅ **BETTER** |

---

### 7. Update Mode & Incremental Analysis

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Detect existing map** | ✅ Check for docs/CODEBASE_MAP.md | ❌ No | ❌ **GAP** |
| **Git change detection** | ✅ `git log --since` | ❌ No | ❌ **GAP** |
| **Incremental update** | ✅ Only re-analyze changed modules | ❌ No | ❌ **GAP** |
| **Merge with existing** | ✅ Preserve unchanged sections | ❌ No | ❌ **GAP** |
| **Timestamp tracking** | ✅ last_mapped in frontmatter | ❌ No | ❌ **GAP** |

**Key Differences:**
- Cartographer: Full incremental update support
- Standalone: Always performs full analysis
- **Recommendation:** Critical feature to add for large codebases

---

### 8. Configuration & Customization

| Feature | Cartographer | Standalone | Status |
|---------|-------------|------------|--------|
| **Default ignores** | ✅ Hardcoded + .gitignore | ✅ Hardcoded in exclude_dirs | ✅ **MATCH** |
| **Token limits** | ✅ Configurable via CLI | ✅ In .env or CLI args | ✅ **MATCH** |
| **Agent count** | ⚠️ Auto-calculated | ✅ CLI argument | ✅ **BETTER** |
| **Model selection** | ✅ Sonnet (default), Haiku option | ✅ Any OpenAI/Anthropic model | ✅ **BETTER** |
| **LLM provider** | ✅ Claude only | ✅ OpenAI, Anthropic, custom | ✅ **BETTER** |
| **Output path** | ✅ Fixed: docs/CODEBASE_MAP.md | ✅ Configurable | ✅ **BETTER** |

---

## 🎯 Critical Gaps to Address

### 🔴 HIGH PRIORITY (Missing Core Features)

1. **Incremental Update Mode**
   - **Cartographer:** Detects changes, only re-analyzes modified modules
   - **Standalone:** No incremental support
   - **Impact:** Wastes time/money on large codebases
   - **Fix:** Implement git diff tracking + selective re-analysis

2. **Navigation Guide**
   - **Cartographer:** "To add feature X, modify files Y, Z"
   - **Standalone:** No navigation guidance
   - **Impact:** Map is less actionable for developers
   - **Fix:** Add LLM-generated navigation section

3. **Gotchas & Non-Obvious Behaviors**
   - **Cartographer:** Captures warnings, edge cases
   - **Standalone:** No gotcha detection
   - **Impact:** Missing critical context
   - **Fix:** Add dedicated gotcha extraction prompt

4. **.gitignore Parsing**
   - **Cartographer:** Full .gitignore pattern support
   - **Standalone:** Hardcoded excludes only
   - **Impact:** May analyze irrelevant files
   - **Fix:** Implement fnmatch-based gitignore parser

---

### 🟡 MEDIUM PRIORITY (Quality Enhancements)

5. **Data Flow Diagrams**
   - **Cartographer:** Mermaid sequence diagrams for key flows
   - **Standalone:** No data flow visualization
   - **Fix:** Generate sequence diagrams for API flows

6. **Conventions Documentation**
   - **Cartographer:** Documents naming, patterns, style
   - **Standalone:** No convention analysis
   - **Fix:** Add LLM prompt to identify patterns

7. **Module-Aware Grouping**
   - **Cartographer:** Groups by semantic modules
   - **Standalone:** Groups by token count only
   - **Fix:** Add directory-based grouping option

8. **Frontmatter Metadata**
   - **Cartographer:** YAML frontmatter with timestamps
   - **Standalone:** No frontmatter
   - **Fix:** Add frontmatter to output

---

### 🟢 LOW PRIORITY (Nice to Have)

9. **CLAUDE.md Integration**
   - **Cartographer:** Updates CLAUDE.md automatically
   - **Standalone:** No context file integration
   - **Fix:** Optional CLAUDE.md update mode

10. **Annotated Directory Tree**
    - **Cartographer:** Tree with purpose annotations
    - **Standalone:** Flat directory list
    - **Fix:** Generate tree with descriptions

---

## 💪 Standalone Analyzer Advantages

| Feature | Advantage Over Cartographer |
|---------|----------------------------|
| **LLM Provider Flexibility** | Works with OpenAI, Anthropic, local models |
| **Specialized Agents** | 5+ agent types vs 1 generic type |
| **ER Diagrams** | Automatic entity relationship diagrams |
| **Structured Extraction** | Categories: entities, APIs, commands, queries |
| **Load Balancing** | Greedy algorithm vs manual grouping |
| **CLI Flexibility** | Configurable output path, agent count |
| **No IDE Dependency** | Runs anywhere Python runs |
| **Cost Control** | Direct API usage, no platform markup |
| **Customizable Workflow** | LangGraph for custom agent workflows |

---

## 📊 Analysis Quality Comparison

### Cartographer Strengths
✅ More contextual (purpose, gotchas, conventions)  
✅ More actionable (navigation guide)  
✅ Better for onboarding new developers  
✅ Incremental updates save time/cost  
✅ Native Claude Code integration  

### Standalone Strengths
✅ More structured (complete tables)  
✅ More analytical (ER diagrams, statistics)  
✅ Better for architecture review  
✅ More flexible (any LLM, any output)  
✅ Better parallelization (greedy balancing)  

---

## 🛠️ Recommended Improvements for Standalone

### Phase 1: Feature Parity (Must-Have)

```python
# File: utils/gitignore_parser.py
class GitignoreParser:
    """Parse .gitignore and match patterns."""
    def __init__(self, root_path):
        self.patterns = self._parse_gitignore(root_path)
    
    def should_ignore(self, file_path):
        # Implement fnmatch-based pattern matching
        pass

# File: agents/gotcha_agent.py
class GotchaAgent(BaseAgent):
    """Extract non-obvious behaviors and warnings."""
    async def analyze(self, files):
        prompt = """
        Identify gotchas, edge cases, and non-obvious behaviors:
        - State mutations
        - Race conditions
        - Edge cases
        - Performance gotchas
        - Security concerns
        """
        pass

# File: agents/navigation_agent.py
class NavigationAgent(BaseAgent):
    """Generate task-based navigation guide."""
    async def analyze(self, scan_results, entities, apis):
        prompt = """
        Based on the codebase structure, create a navigation guide:
        - To add a new API endpoint: [steps]
        - To add a new entity: [steps]
        - To modify authentication: [steps]
        """
        pass

# File: orchestrator/incremental_analyzer.py
class IncrementalAnalyzer:
    """Support incremental updates."""
    def detect_changes(self, last_mapped_timestamp):
        # Run git log --since
        pass
    
    def merge_results(self, existing_map, new_results):
        # Update only changed sections
        pass
```

### Phase 2: Quality Enhancements

```python
# File: agents/dataflow_agent.py
class DataFlowAgent(BaseAgent):
    """Generate data flow diagrams."""
    async def analyze(self, apis, entities):
        # Create sequence diagrams for key flows
        pass

# File: agents/convention_agent.py
class ConventionAgent(BaseAgent):
    """Document coding conventions."""
    async def analyze(self, files):
        prompt = """
        Identify conventions:
        - Naming patterns
        - File organization
        - Code style
        - Architecture patterns
        """
        pass

# File: utils/tree_generator.py
class AnnotatedTreeGenerator:
    """Generate directory tree with annotations."""
    def generate(self, directories, file_purposes):
        # ASCII tree with purpose descriptions
        pass

# File: synthesis_agent.py
def generate_with_frontmatter(self, report_content):
    frontmatter = f"""---
last_mapped: {datetime.now().isoformat()}
total_files: {self.total_files}
total_tokens: {self.total_tokens}
---

"""
    return frontmatter + report_content
```

---

## 📈 Scaling Comparison

| Codebase Size | Cartographer | Standalone | Winner |
|---------------|-------------|------------|--------|
| **Small (100-500 files)** | 1 Sonnet subagent | 1-2 agents (may be overkill) | 🏆 **Cartographer** (simpler) |
| **Medium (500-2k files)** | 3-5 Sonnet subagents | 3-5 specialized agents | 🤝 **Tie** |
| **Large (2k-5k files)** | 5-10 Sonnet subagents | 5-10 specialized agents | 🏆 **Standalone** (better balancing) |
| **Very Large (5k+ files)** | 10-20 Sonnet subagents | 10-30 specialized agents | 🏆 **Standalone** (more flexible) |

**Incremental Updates:**
- Cartographer: 🏆 **Massive advantage** - only re-analyze changes
- Standalone: ❌ Always full re-analysis

---

## ✅ Conclusion & Action Items

### Current State
- **Standalone analyzer:** 70% functional parity with Cartographer
- **Strengths:** More structured extraction, better diagrams, flexible LLM
- **Gaps:** No incremental updates, missing navigation/gotchas/conventions

### Recommended Actions

#### Immediate (Week 1)
1. ✅ Implement GitignoreParser
2. ✅ Add GotchaAgent
3. ✅ Add NavigationAgent
4. ✅ Add frontmatter to output

#### Short-term (Week 2-3)
5. ✅ Implement incremental update mode
6. ✅ Add data flow diagram generation
7. ✅ Add convention analysis
8. ✅ Generate annotated directory tree

#### Long-term (Month 2)
9. ⚠️ Add CLAUDE.md integration (optional)
10. ⚠️ Add module-aware grouping (optional enhancement)

### Final Assessment

| Criteria | Cartographer | Standalone (Current) | Standalone (After Fixes) |
|----------|-------------|---------------------|-------------------------|
| **Feature Completeness** | 100% | 70% | 95% |
| **Analysis Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐ (Claude only) | ⭐⭐⭐⭐⭐ (any LLM) | ⭐⭐⭐⭐⭐ |
| **Developer Experience** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cost Efficiency** | ⭐⭐⭐⭐⭐ (incremental) | ⭐⭐⭐ (full scans) | ⭐⭐⭐⭐⭐ |

**With the recommended improvements, the standalone analyzer will achieve feature parity with Cartographer while offering additional advantages in flexibility, structured analysis, and LLM choice.**

---

## 📚 References

- **Cartographer Plugin:** https://github.com/kingbootoshi/cartographer
- **Cartographer Documentation:** `e:\analyser\cartographer-main\plugins\cartographer\skills\cartographer\SKILL.md`
- **Standalone Analyzer:** `e:\analyser\standalone-analyzer`
- **Comparison Document:** `e:\analyser\standalone-analyzer\FINAL_COMPARISON.md`
