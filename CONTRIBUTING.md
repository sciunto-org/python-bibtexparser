## Contributing

Thanks heaps for being interested in contributing to python-bibtexparser.

We are always looking for people to improve the library. Contributions include, but are not limited to:

1. Opening well described issues for bugs or feature requests.
2. Providing bugfixing PRs
3. Implementing any of the issues or continuing any of the PRs labelled with `needs help` or `good first issue`.

### Some guidelines:

1. Be nice! Were all doing this in our free time; no one is obligated to do anything.
2. Add sufficient tests to your PRs
3. Document your code.
4. Don't hesitate to ask questions.

### Version 1 vs version 2
Also note that there are currently two independent "default" branches:
First, `main`, where we maintain the `v2` of bibtexparser, which is a complete re-write and currently still in beta and not feature complete.
Second, `v1` where we maintain the stable `v1` version of bibtexparser. Note that on `v1` we accept only small, non-breaking changes and are planning to stop support as soon as `v2` reaches reasonable stability.
The two branches are never going to be merged anymore, thus if you want to change something for both versions, you will have to open two PRs.

Issues are labelled `v1` and `v2`, correspondingly.

### Dev-Dependencies, testing and linting on v2.

To install the dev dependencies, run `pip install -e .[test,lint,docs]` from within the cloned repository. Then:

- To test your code, run `pytest .`
- To lint your code (required for CI/CD to pass), run: `black bibtexparser tests docs && isort bibtexparser tests docs --profile black`
- To build and preview the docs, navigate into `docs` and run `make html`. Then open the `index.html` file in the `docs/build/html` folder.
