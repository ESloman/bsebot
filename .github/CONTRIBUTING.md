# Contributing to BSEBot

Contributors are welcome!

BSEBot was first created as a bot for the **BSE** Discord server and as an excuse to play around with Discord and Python code. It's best to dive in and have a play with the codebase - there are some setup requirements below.

# Getting started

There is some additional information in the repository [Wiki](https://github.com/ESloman/bsebot/wiki) but it is far from complete.

## Want to ask questions?
- Drop me a message on Discord: _ESloman#6969_
- [Join my bot testing server](https://discord.gg/R39Kw7gXSa)
- To see the BSEBot in action: [join the BSE server.](https://discord.gg/dGMPswqf49)

## Code formatting
I try to adhere to `PEP8` standards as much as possible but with a line length of **120**. Every commit will trigger a `ruff` GitHub action that will parse the code and fail that commit if it finds any flaws. 

You can run `ruff` in the root directory `bsebot`. The configuration file already exists so it should pick that up. Additionally, we have a `ruff` pre-commit hook setup. You can install `pre-commit` and that should also lint your code before commit; it'll also attempt to fix any issues it's found.

## Testing

We use `pytest` for testing with the `pytest-asnycio` and `pytest-cov` plugins.

We have a suite of tests in the `tests/` directory that can be run to verify some changes. The test suite(s) are far from complete
and may not catch everything. The requirements for testing are defined in [test-requirements.txt](../test-requirements.txt).

To actually run unittests we use a host of mocks and dummy data to replicate various scenarios to actually run tests. This allows us to not rely on a MongoDB server or the Discord API for testing.

Aiming for 80% coverage of any new code and eventually getting the entire repository up to `80+%` coverage.

## What to contribute

There are lots of areas of the project that need attention; and therefore a variety of different areas that need contributions. This inclues things like:
- doc string updates
- type hint updates
- adding tests to increase coverage
- refactoring to reduce code complexity (breaking down functions, etc)
- working on any open issues ([good first issues here](https://github.com/ESloman/bsebot/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22))
- fixing other [SonarCloud issues](https://sonarcloud.io/project/issues?resolved=false&id=ESloman_bsebot)
- adding a new feature/something that interests you


## Requirements

1. python 3.12+ installed
2. install `requirements.txt`
3. install `test-requirements.txt`
