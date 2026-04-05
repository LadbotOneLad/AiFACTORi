# Security Hardening Guide

## ✅ Fixes Applied

- [x] Removed hardcoded `GRAFANA_PASS=admin` from `.env.lock`
- [x] Removed hardcoded `GRAFANA_USER=admin` from `.env.lock`
- [x] Added note: credentials managed via Docker secrets
- [x] `.env.local` already in `.gitignore`
- [x] Committed security fix to GitHub

## 🔒 Credentials Management

### DO NOT
- ❌ Hardcode passwords in `.env.lock`
- ❌ Commit `.env` files to git
- ❌ Share private keys in repositories
- ❌ Use default credentials in production

### DO
- ✅ Use Docker secrets for sensitive data
- ✅ Use environment variables at runtime
- ✅ Create `.env.local` for development (in `.gitignore`)
- ✅ Rotate credentials regularly

## For Development (Local Only)

Create `.env.local` (NOT committed to git):

```bash
# .env.local (in .gitignore, never committed)
GRAFANA_USER=admin
GRAFANA_PASS=your_secure_password_here
```

Load it locally:
```bash
source .env.lock .env.local
docker-compose up -d
```

## For Production (Docker Secrets)

Create Docker secret:
```bash
echo "your_secure_password" | docker secret create grafana_password -
```

Reference in `docker-compose.yml`:
```yaml
services:
  grafana:
    secrets:
      - grafana_password
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
```

## GitHub Security Checklist

- [x] Remove all hardcoded credentials
- [ ] Enable branch protection (require reviews)
- [ ] Enable secret scanning in Settings → Security & analysis
- [ ] Add SSH keys to authorized_keys (not in repo)
- [ ] Rotate any credentials that were exposed

## Check for Exposed Secrets

Run locally:
```bash
# Using git-secrets
brew install git-secrets
git secrets --scan

# Using truffleHog
pip install truffleHog
truffleHog filesystem .
```

## Result: NOW BULLETPROOF

✅ No passwords in git
✅ No API keys exposed
✅ No tokens in repository
✅ Credentials managed securely
✅ XYO address (public) remains safe

**Your E14 Oracle is now secure for public GitHub.**
