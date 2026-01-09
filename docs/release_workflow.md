# Aria Release Workflow

This document defines the official process for releasing new versions of the Aria CLI.

## 1. Preparation Phase

- **Feature Freeze**: Ensure all planned features for the release are merged and stable.
- **Dependency Audit**: Check `requirements.txt` for outdated or unnecessary packages.
- **Documentation Review**: Verify that all new features are documented in `docs/runbooks/` and the `README.md`.

## 2. Testing Phase

Run the full test suite in a clean environment:

```bash
# Recommended test execution
pytest tests/
```

Verify that the CLI help and basic commands work:
```bash
python src/aria.py version
python src/aria.py open --headless
python src/aria.py close
```

## 3. Version Bump

1.  Open `src/aria.py`.
2.  Locate the `VERSION` constant.
3.  Increment the version according to SemVer rules.
4.  Commit the change: `git commit -m "chore: bump version to vX.Y.Z"`.

## 4. Tagging

Create a signed git tag for the release:

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## 5. Artifact Generation

Create a source distribution archive:

```bash
# On Linux/macOS
tar -czvf aria-vX.Y.Z.tar.gz src/ docs/ requirements.txt README.md LICENSE

# On Windows (PowerShell)
Compress-Archive -Path src, docs, requirements.txt, README.md, LICENSE -DestinationPath aria-vX.Y.Z.zip
```

## 6. Publishing

1.  Draft a new release on GitHub.
2.  Use the tag `vX.Y.Z`.
3.  Generate release notes from commit history.
4.  Attach the generated artifacts (`.tar.gz` or `.zip`).
5.  Publish the release.

## 7. Post-Release

- Update the internal "Progress Tracker" (`docs/plan/cookie.txt`).
- Communicate the release to stakeholders/users if applicable.
