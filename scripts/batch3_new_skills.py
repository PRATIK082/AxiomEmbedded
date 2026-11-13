"""Batch 3: scaffold missing high-value skills."""
from __future__ import annotations
import subprocess, sys, pathlib
ROOT = pathlib.Path(r"E:\My_Project\My_Github\AxiomEmbedded")
candidates = [
 ("axiom-cloud-architecture","Cloud Architecture","platform"),
 ("axiom-kubernetes-edge","Kubernetes Edge","platform"),
 ("axiom-terraform-infra","Terraform Infrastructure","platform"),
 ("axiom-monitoring-observability","Monitoring Observability","platform"),
 ("axiom-sre-reliability","SRE Reliability","platform"),
 ("axiom-chaos-engineering","Chaos Engineering","all"),
 ("axiom-cli-developer","CLI Developer","all"),
 ("axiom-prompt-engineering","Prompt Engineering","generic-embedded"),
 ("axiom-rag-architect","RAG Architect","generic-embedded"),
 ("axiom-data-pipeline","Data Pipeline","generic-embedded"),
 ("axiom-database-optimization","Database Optimization","all"),
 ("axiom-graphql-architect","GraphQL Architect","all"),
 ("axiom-microservices-architect","Microservices Architect","all"),
 ("axiom-websocket-engineer","WebSocket Engineer","all"),
 ("axiom-mcp-developer","MCP Developer","platform"),
 ("axiom-test-master","Test Master","all"),
 ("axiom-playwright-e2e","Playwright E2E","all"),
 ("axiom-debugging-wizard","Debugging Wizard","all"),
 ("axiom-legacy-modernizer","Legacy Modernizer","all"),
 ("axiom-secure-code-guardian","Secure Code Guardian","all"),
 ("axiom-security-reviewer","Security Reviewer","all"),
 ("axiom-skill-evolution","Skill Evolution","all"),
]
for sid,title,domain in candidates:
    r = subprocess.run([sys.executable, str(ROOT/"scripts"/"create_skill.py"), "--id", sid, "--title", title, "--domain", domain, "--apply"], capture_output=True, text=True, cwd=str(ROOT))
    print(sid, "->", r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[:120])