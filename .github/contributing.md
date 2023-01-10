# Table of Contents

- [Style Guidelines](#style-guidelines)
- [Quality](#quality)

# Style Guidelines

Install pre-commit hook once cloned from this repository.
Apart from other checks it will mainly auto-format source code, check
for trailing whitespaces and fix end of lines.

```bash
# install hook for upcoming commits
pre-commit install

# run pre-commit checks manually on all files
pre-commit run --all-file
# only on staged files
pre-commit
```

The procedure:

1. make code changes
2. stage files
3. git commit
    1. pre-commit check succeeds -> commit is done
    2. pre-commit check fails -> commit is interrupted
        1. files are changed and unstaged
        2. review changes, stage files and repeat the commit command

Do auto format and let the auto-formatter decide the style.
If auto formatting is forgotten, the pre-commit hook will finally do it.
In doubt apply the do-not-harm principle: stick to the same pattern as the majority of the code does.

# Quality

- Your changes shall not produce new warnings.
- If you can fix old warnings please do so (run `pylint *` from the root directory).
- Perform a self-review, comment code in public interface and in hard-to-understand areas.
- Write tests for new code.
- Use Python 3, write docstring and write type hinting:
  - docstring for public methods and functions
  - type hinting: at least for public methods and functions
- Update docstrings accordingly.
