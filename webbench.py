#!/usr/bin/env python3
# =============================================================================
#  webbench.py
#  ---------------------------------------------------------------------------
#  A single-file CLI (Python 3.9+) that spins up each web project, runs
#  performance / quality benchmarks, and prints a ranked comparison table.
#
#  INSTALLATION (one-time)
#  ---------------------------------------------------------------------------
#  pip install pyyaml tabulate rich        # YAML + pretty tables/colours
#  npm  i -g lighthouse eslint             # CLI tools used under the hood
#
#  EXPECTED FOLDER STRUCTURE
#  ---------------------------------------------------------------------------
#  .
#  ├── webbench.py
#  ├── config.yaml      ← metric weights (must sum to 1.0)
#  └── projects.yaml    ← list of projects with paths, serve/build commands
#
#  RUN
#  ---------------------------------------------------------------------------
#  python webbench.py --config config.yaml --projects projects.yaml
#
#  OPTIONAL FLAGS (you usually don't need them)
#  ---------------------------------------------------------------------------
#  --skip-lighthouse   # (removed—now always on. comment runner below if needed)
#  --skip-eslint       # (removed—now always on. comment runner below if needed)
#  --skip-build        # (removed—now always on. comment runner below if needed)
#
# =============================================================================
"""
YAML EXAMPLES
-------------

# config.yaml
metrics:
  performance:     {weight: 0.20}
  accessibility:   {weight: 0.15}
  best_practices:  {weight: 0.10}
  seo:             {weight: 0.05}
  pwa:             {weight: 0.05}
  code_quality:    {weight: 0.15}
  build_time:      {weight: 0.15}
  bundle_size:     {weight: 0.15}

# projects.yaml
projects:
- name: react-app
  path: ./react-app
  serve_command: "npm run dev"        # STARTS a dev server (optional)
  serve_url:    http://localhost:5173 # Waits for 200 OK before tests
  build_command: "npm run build"
  dist_folder:   dist                 # folder created by build
- name: vue-app
  path: ./vue-app
  serve_command: "npm run dev"
  serve_url:    http://localhost:3000
  build_command: "npm run build"
  dist_folder:   dist
"""

# =============================================================================
#  Standard library imports
# =============================================================================
import argparse, json, os, signal, subprocess, sys, time, uuid
from contextlib import suppress
from pathlib import Path
from urllib.request import urlopen, URLError

# =============================================================================
#  Third-party imports (optional pretty output, coloured warnings)
# =============================================================================
try:     import yaml                # Parse YAML config files
except:  sys.exit("PyYAML required → pip install pyyaml")

try:     from tabulate import tabulate   # ASCII tables
except:  tabulate = None

try:     from rich import print as rprint  # coloured console messages
except:  rprint = print                    # plain print fallback

import shutil  # stdlib – used after functions to test for lighthouse binary

# =============================================================================
#  Utility helpers
# =============================================================================
def sh(cmd: str, cwd: str | Path | None = None, *,
       capture: bool = True) -> tuple[int, str]:
    """
    Run a shell command.
      • Returns (exit_code, combined_output)
      • Redirects both stdout and stderr to the same string
      • `capture=False` streams output directly to the terminal (not used here)
    """
    p = subprocess.run(cmd, shell=True, cwd=cwd,
                       text=True, capture_output=capture)
    return p.returncode, (p.stdout + p.stderr)

def wait_url(url: str, timeout: int = 30) -> bool:
    """
    Poll `url` until HTTP < 400 is returned or `timeout` seconds pass.
    Used to wait for the dev server to finish booting.
    """
    t0 = time.time()
    while time.time() - t0 < timeout:
        with suppress(URLError):
            if urlopen(url, timeout=3).status < 400:
                return True
        time.sleep(1)
    return False

def clamp_to_score(val: float, best: float, worst: float) -> float:
    """
    Convert a raw metric where *lower is better* into a 0–10 score.
    • Anything better than `best`   → 10
    • Anything worse  than `worst` →  0
    • Linear interpolation in-between
    """
    if val <= best:  return 10.0
    if val >= worst: return 0.0
    return 10 - 10*(val-best)/(worst-best)

sec_score  = lambda s: clamp_to_score(s, best=5,  worst=60)   # build time
size_score = lambda m: clamp_to_score(m, best=1,  worst=50)   # MB

# =============================================================================
#  Metric runners (one function per group of metrics)
# =============================================================================
def run_lighthouse(url: str) -> dict[str, float]:
    """
    Execute Lighthouse CLI in headless-Chrome mode and read JSON from stdout.
    Returns scores in 0–10 scale for:
      performance • accessibility • best_practices • seo • pwa
    """
    if not shutil.which("lighthouse"):
        raise RuntimeError("lighthouse CLI is not installed (`npm i -g lighthouse`)")
    cmd = f"lighthouse {url} --output=json --output-path=stdout --quiet --chrome-flags='--headless'"
    code, out = sh(cmd)
    if code:
        raise RuntimeError("lighthouse exited with non-zero status")
    cats = json.loads(out)["categories"]
    metrics = ("performance", "accessibility", "best-practices", "seo", "pwa")
    return {k: cats[k]["score"]*10 for k in metrics if k in cats}

def run_eslint(path: Path) -> float:
    """
    Run ESLint via npx, write report to a temp JSON file, count total messages
    (errors+warnings). 0 errors → 10, 50+ errors → 0, linear in-between.
    """
    if not shutil.which("npx"):
        raise RuntimeError("Node/npm not available (`npx` missing)")
    report = path / f"eslint-{uuid.uuid4().hex}.json"
    sh(f"npx eslint . -f json -o {report}", cwd=path)
    if not report.exists():
        raise RuntimeError("ESLint did not produce JSON output")
    msgs = sum(len(f["messages"]) for f in json.loads(report.read_text()))
    report.unlink(missing_ok=True)
    return max(0.0, 10 - msgs/5)   # 0 msgs → 10, 5 msgs → 9, ... 50 msgs → 0

def run_build(path: Path, cfg: dict) -> dict[str, float]:
    """
    Time the production build and compute distribution folder size.
    Returns dict with build_time + bundle_size converted to 0–10 scores.
    """
    cmd   = cfg.get("build_command", "npm run build")
    dist  = cfg.get("dist_folder",  "dist")
    t0    = time.perf_counter()
    code, _ = sh(cmd, cwd=path)
    secs = time.perf_counter() - t0
    if code:
        raise RuntimeError("build command returned non-zero exit")
    dist_path = path / dist
    if not dist_path.exists():
        raise RuntimeError(f"folder “{dist}” not found after build")
    mb = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file())/1_048_576
    return {"build_time": sec_score(secs),
            "bundle_size": size_score(mb)}

# =============================================================================
#  Evaluate a single project
# =============================================================================
def evaluate(prj: dict, weights: dict[str, float]) -> dict[str, float]:
    """
    1. Launch dev server (if `serve_command` provided)
    2. Wait until the URL responds (up to 30 s)
    3. Run Lighthouse, ESLint, production build
    4. Kill the dev server
    5. Return dict of metric_name → 0-10 score
    Each step is wrapped in try/except to keep the run alive even on failure.
    """
    path = Path(prj["path"]).expanduser().resolve()
    url  = prj["serve_url"]
    # ── start dev server (optional) ───────────────────────────────────────────
    server = None
    if cmd := prj.get("serve_command"):
        server = subprocess.Popen(
            cmd, shell=True, cwd=path,
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
            preexec_fn=os.setsid  # so we can kill the whole proc-group
        )
        if not wait_url(url):
            rprint(f"[red]⚠  {prj['name']} – dev server never became reachable ({url})[/red]")
            if server: os.killpg(server.pid, signal.SIGKILL)
            return {}
    # ── collect metrics ──────────────────────────────────────────────────────
    scores: dict[str, float] = {}
    try:   scores |= run_lighthouse(url)
    except Exception as e: rprint(f"[yellow]Lighthouse ⤵  {e}[/yellow]")
    try:   scores["code_quality"] = run_eslint(path)
    except Exception as e: rprint(f"[yellow]ESLint ⤵  {e}[/yellow]")
    try:   scores |= run_build(path, prj)
    except Exception as e: rprint(f"[yellow]Build ⤵  {e}[/yellow]")
    # ── stop dev server (if started) ─────────────────────────────────────────
    if server:
        with suppress(ProcessLookupError):
            os.killpg(server.pid, signal.SIGINT)
    return scores

# =============================================================================
#  Weighted total helper – denominator uses only metrics that exist
# =============================================================================
def weighted_total(scores: dict[str,float], weights: dict[str,float]) -> float:
    relevant = {k:w for k,w in weights.items() if k in scores}
    return 0.0 if not relevant \
         else sum(scores[k]*w for k,w in relevant.items()) / sum(relevant.values())

# =============================================================================
#  Main CLI
# =============================================================================
def main() -> None:
    ap = argparse.ArgumentParser(description="Compare multiple web projects.")
    ap.add_argument("--config",   required=True, help="metric weights YAML")
    ap.add_argument("--projects", required=True, help="projects YAML")
    args = ap.parse_args()

    weights  = {k:v["weight"]
                for k,v in yaml.safe_load(Path(args.config).read_text())["metrics"].items()}
    projects = yaml.safe_load(Path(args.projects).read_text())["projects"]

    cols  = ["name"] + list(weights) + ["TOTAL"]
    table = []

    for pr in projects:
        sc = evaluate(pr, weights)
        table.append([pr["name"],
                      *["{:.2f}".format(sc[k]) if k in sc else "-" for k in weights],
                      f"{weighted_total(sc, weights):.2f}"])

    table.sort(key=lambda r: float(r[-1]), reverse=True)

    if tabulate:
        print(tabulate(table, headers=cols, floatfmt=".2f"))
    else:
        print(cols, *table, sep="\n")

# =============================================================================
#  Entry point
# =============================================================================
if __name__ == "__main__":
    main()
