# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`).
4. Test your contribution (see below).
5. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [ruff](https://docs.astral.sh/ruff/) (`scripts/lint`) to make sure the code follows the style.

## Test your code modification

Run the test suite with Python **3.14** after `scripts/setup` (installs all dependencies from `requirements.txt`):

```bash
scripts/test
```

Coverage is enforced at 95% for `custom_components/mawaqeet` (same flags as CI).

- **Pinned Home Assistant** (default): uses `homeassistant==…` from [`requirements-test.txt`](requirements-test.txt), matching the supported release.
- **Latest Home Assistant** (same as CI “latest” leg; upgrades `homeassistant` and `pytest-homeassistant-custom-component` together):

```bash
HA_TEST_LATEST=1 scripts/test
```

On Windows, host Python often fails with Home Assistant (`fcntl`). Prefer Docker:

```bash
docker run --rm -v "/c/Projects/HomeAssistant/ha-mawaqeet:/repo" -w /repo \
  -e PIP_DISABLE_PIP_VERSION_CHECK=1 -e PIP_PREFER_BINARY=1 \
  python:3.14-bookworm bash scripts/test
```

When changing the Lovelace card under `custom_components/mawaqeet/frontend/`, rebuild the committed bundle:

```bash
python scripts/build_frontend.py
```

CI (Test, Lint, Validate, Frontend) runs on every push and pull request to **`main`** and **`dev`** (see [`.github/workflows/`](.github/workflows/)).

This custom component is based on [integration_blueprint](https://github.com/ludeeus/integration_blueprint). A dev container (`.devcontainer.json`) provides a standalone Home Assistant instance with [`config/configuration.yaml`](./config/configuration.yaml).

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
