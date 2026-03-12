# ljg-explain-concept

A Claude Code skill that deconstructs any concept through **8 exploration dimensions**, then compresses all insights into a single epiphany.

## What it does

Given any concept (e.g. "entropy", "recursion", "freedom"), the skill performs:

1. **Preprocessing** — clarify definition, identify core morphemes
2. **8-Dimensional Exploration**:
   - Historical tracing
   - Dialectical analysis
   - Phenomenological reduction
   - Linguistic deconstruction
   - Mathematical formalization
   - Existentialist examination
   - Aesthetic dimension
   - Meta-philosophical reflection
3. **Introspection** — first-person view from inside the concept
4. **Epiphany Compression** — The One formula + Feynman-style sentence + ASCII topology
5. **Output** — writes org-mode file to `~/Documents/notes/`

## Install

```bash
/plugin marketplace add lijigang/ljg-explain-concept
/plugin install ljg-explain-concept
```

## Usage

```
/ljg-explain-concept entropy
/ljg-explain-concept recursion
/ljg-explain-concept self-reference
```

## License

MIT
