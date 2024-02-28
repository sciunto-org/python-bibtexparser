==========
Contribute
==========

Contributions to this open-source project are strongly encouraged.
If you would like to contribute to the project, please fork the repository and submit a pull request.
A few guidelines to keep in mind:

*   Please make sure that your code is well-documented by adding comprehensive docstrings.
    Indicate the purpose of the function, the input parameters, and the expected output.

*   Please add unit tests to the ``tests`` directory (in existing or new files)
    to ensure that the code is functioning as expected.
    Run the tests using the command ``pytest`` in the root directory of the project
    (we refer to the [pytest documentation](https://docs.pytest.org) for more information,
    e.g. about verbose output).

    If you need to install:
    ```bash
    python -m pip install pytest
    ```

*   Respect the coding conventions by running the linters
    (i.e. you don't have to worry during coding, formatting is automatically applied by the linters).
    Run:
    ```bash
    pre-commit run --all-files
    ```

    If you need to install:
    ```bash
    python -m pip install pre-commit
    ```
    (and if you don't want to, you can either run the linters manually,
    with settings in ``.pre-commit-config.yaml``,
    or apply modifications based on the CI output),
