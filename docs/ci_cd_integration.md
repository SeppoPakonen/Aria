# CI/CD and DevOps Integration with Aria

Aria is designed to be easily integrated into automated pipelines. This guide covers the best practices for running Aria in headless and non-interactive environments.

## 1. Running with Docker

The easiest way to run Aria in CI is using the provided `Dockerfile`.

### Build the Image
```bash
docker build -t aria-cli .
```

### Run a Script
```bash
docker run -e GEMINI_API_KEY=$GEMINI_API_KEY aria-cli script run my-automated-task
```

## 2. GitHub Actions Integration

You can use Aria in GitHub Actions by using the Docker image or installing it directly in a runner.

### Example Workflow (`.github/workflows/aria-checks.yml`)
```yaml
name: Aria Web Checks

on:
  schedule:
    - cron: '0 0 * * *' # Run daily
  workflow_dispatch:

jobs:
  web-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Aria
        run: docker build -t aria-cli .
        
      - name: Run Monitoring Script
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ARIA_VAULT_MY_SITE_PASS: ${{ secrets.MY_SITE_PASS }}
        run: |
          # Register credential from env if needed, or use env: placeholder
          docker run -e GEMINI_API_KEY -e ARIA_VAULT_MY_SITE_PASS aria-cli \
            --force \
            script run monitoring-script
            
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: aria-reports
          path: ~/.aria/reports/
```

## 3. Non-Interactive Mode

When running in CI, ensure you use the `--force` flag to bypass interactive safety confirmations.

Aria also supports configuration via environment variables:
- `GEMINI_API_KEY`: API key for Gemini.
- `ARIA_LOG_LEVEL`: Set log verbosity (DEBUG, INFO, etc.).
- `ARIA_JSON_LOGS`: Set to `true` for structured logging.
- `ARIA_THROTTLE_DELAY`: Add delay between browser actions.

## 4. Secret Management in CI

Instead of using `aria settings credentials set`, which is interactive, use one of these patterns in CI:

1. **Environment Variables**: Use `{{env:VAR_NAME}}` in your scripts and set `VAR_NAME` in your CI environment.
2. **Pre-populated Vault**: You can mount a pre-populated `credentials.json` into `/root/.aria/credentials.json` in the Docker container.
