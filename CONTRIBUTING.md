## Contributing

Thanks heaps for being interested in contributing to python-bibtexparser.

We are always looking for people to improve the library. Contributions include, but are not limited to:

1. Opening well described issues for bugs or feature requests.
2. Providing bugfixing PRs
3. Implementing any of the issues or continuing any of the PRs labelled with `needs help` or `good first issue`.

### Some guidelines

1. Be nice! We're all doing this in our free time; no one is obligated to do anything.
2. Add sufficient tests to your PRs.
3. Document your code.
4. Don't hesitate to ask questions.
5. For bug reports, a minimal reproduction example plus a short note on real-world impact goes a long way.
6. If an issue was found by an LLM rather than something you actually hit, and isn't security-critical, please only submit it if you can clearly justify a real practical impact — theoretical issues with no real-world relevance add review burden without much benefit.
7. For anything beyond a small fix, open an issue to discuss scope and approach before investing time in an implementation.

### A note on AI-generated PRs

Using AI tools is fine, and encouraged — including to self-review your PR before opening it. What doesn't work well is large, auto-generated PRs or issues with no clear human benefit behind them: they're inefficient to review. We reserve the right to close these without merging, even when technically valid, since at that point it's faster for us to just generate a fix ourselves.

### Version 1 vs version 2

Also note that there are currently two independent "default" branches:
First, `main`, where we maintain the `v2` of bibtexparser, which is a complete re-write and the current, recommended version.
Second, `v1` where we maintain the legacy `v1` version of bibtexparser. Note that `v1` is in maintenance mode: we accept only small, non-breaking changes there.
The two branches are never going to be merged anymore, thus if you want to change something for both versions, you will have to open two PRs.

Issues are labelled `v1` and `v2`, correspondingly.

### Dev-Dependencies, testing and linting on v2.

To install the dev dependencies, run `pip install -e .[test,docs]` from within the cloned repository. Then:

- To test your code, run `pytest .`
- To lint your code (enforces code style), run: `pre-commit run --all-files` (if you need to install pre-commit, run `pip install pre-commit`).
- To build and preview the docs, navigate into `docs` and run `make html`. Then open the `index.html` file in the `docs/build/html` folder.
