# Deep Research Skill for Claude Code

A comprehensive research engine that brings Claude Desktop's Advanced Research capabilities (and more) to Claude Code terminal.

## Features

- **8-Phase Research Pipeline**: Scope → Plan → Retrieve → Triangulate → Synthesize → Critique → Refine → Package
- **Multiple Research Modes**: Quick, Standard, Deep, and UltraDeep
- **Graph-of-Thoughts Reasoning**: Non-linear exploration with branching thought paths
- **Citation Management**: Automatic source tracking and bibliography generation
- **Source Credibility Assessment**: Evaluates source quality and potential biases
- **Structured Reports**: Professional markdown reports with executive summaries
- **Verification & Triangulation**: Cross-references claims across multiple sources

## Installation

The skill is already installed globally in `~/.claude/skills/deep-research/`

No additional dependencies required for basic usage.

## Usage

### In Claude Code

Simply invoke the skill:

```
Use deep research to analyze the state of quantum computing in 2025
```

Or specify a mode:

```
Use deep research in ultradeep mode to compare PostgreSQL vs Supabase
```

### Direct CLI Usage

```bash
# Standard research
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode standard

# Deep research (all 8 phases)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode deep

# Quick research (3 phases only)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode quick

# Ultra-deep research (extended iterations)
python ~/.claude/skills/deep-research/research_engine.py --query "Your research question" --mode ultradeep
```

## Research Modes

| Mode | Phases | Duration | Best For |
|------|--------|----------|----------|
| **Quick** | 3 phases | 2-5 min | Simple topics, initial exploration |
| **Standard** | 6 phases | 5-10 min | Most research questions |
| **Deep** | 8 phases | 10-20 min | Complex topics requiring thorough analysis |
| **UltraDeep** | 8+ phases | 20-45 min | Critical decisions, comprehensive reports |

## Output

Research reports are saved to: `~/.claude/research_output/`

Each report includes:
- Executive Summary
- Detailed Analysis with Citations
- Synthesis & Insights
- Limitations & Caveats
- Recommendations
- Full Bibliography
- Methodology Appendix

## Examples

### Technology Analysis
```
Use deep research to evaluate whether we should adopt Next.js 15 for our project
```

### Market Research
```
Use deep research to analyze longevity biotech funding trends 2023-2025
```

### Technical Decision
```
Use deep research to compare authentication solutions: Auth0 vs Clerk vs Supabase Auth
```

### Scientific Review
```
Use deep research in ultradeep mode to summarize recent advances in senolytic therapies
```

## Quality Standards

Every research output:
- ✅ Minimum 10+ distinct sources
- ✅ Citations for all major claims
- ✅ Cross-verified facts (3+ sources)
- ✅ Executive summary under 250 words
- ✅ Limitations section
- ✅ Full bibliography
- ✅ Methodology documentation

## Architecture

```
deep-research/
├── SKILL.md                    # Main skill definition
├── research_engine.py          # Core orchestration engine
├── utils/
│   ├── citation_manager.py    # Citation tracking & bibliography
│   └── source_evaluator.py    # Source credibility assessment
├── requirements.txt
└── README.md
```

## Tips for Best Results

1. **Be Specific**: Frame questions clearly with context
2. **Set Expectations**: Specify if you need comparisons, recommendations, or pure analysis
3. **Choose Appropriate Mode**: Use Quick for exploration, Deep for decisions
4. **Review Scope**: Check Phase 1 output to ensure research is on track
5. **Leverage Citations**: Use citation numbers to drill deeper into specific sources

## Comparison with Claude Desktop Research

| Feature | Claude Desktop | Deep Research Skill |
|---------|---------------|---------------------|
| Multi-source synthesis | ✅ | ✅ |
| Citation tracking | ✅ | ✅ |
| Iterative refinement | ✅ | ✅ |
| Source verification | ✅ | ✅ Enhanced |
| Credibility scoring | ❌ | ✅ |
| 8-phase methodology | ❌ | ✅ |
| Graph-of-Thoughts | ❌ | ✅ |
| Multiple modes | ❌ | ✅ |
| Local file integration | ❌ | ✅ |
| Code execution | ❌ | ✅ |

## Version

1.0 (2025-11-04)

## License

User skill - modify as needed for your workflow
