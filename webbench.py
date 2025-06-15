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
  security:        {weight: 0.10}

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
import argparse, json, os, signal, subprocess, sys, time, uuid, re
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
lines_score = lambda l: clamp_to_score(l, best=500, worst=10000)  # lines of code
files_score = lambda f: clamp_to_score(f, best=10, worst=100)     # number of files

# =============================================================================
#  Metric runners (one function per group of metrics)
# =============================================================================
def run_lighthouse(url: str) -> dict[str, float]:
    """
    Execute Lighthouse CLI in headless-Chrome mode and read JSON from stdout.
    Returns scores in 0–10 scale for:
      performance • accessibility • best_practices • seo
    Plus raw performance score for display purposes.
    """
    if not shutil.which("lighthouse"):
        raise RuntimeError("lighthouse CLI is not installed (`npm i -g lighthouse`)")
    cmd = f"lighthouse {url} --output=json --output-path=stdout --quiet --chrome-flags='--headless'"
    code, out = sh(cmd)
    if code:
        raise RuntimeError("lighthouse exited with non-zero status")
    cats = json.loads(out)["categories"]
    metrics = ("performance", "accessibility", "best-practices", "seo")
    results = {k: cats[k]["score"]*10 for k in metrics if k in cats}
    
    # Add raw performance score for display (as percentage)
    if "performance" in cats:
        results["performance_raw"] = cats["performance"]["score"]
    
    return results

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
    Returns dict with build_time + bundle_size converted to 0–10 scores,
    plus raw values for display purposes.
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
        raise RuntimeError(f"folder '{dist}' not found after build")
    mb = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file())/1_048_576
    return {"build_time": sec_score(secs),
            "bundle_size": size_score(mb),
            "build_time_raw": secs,
            "bundle_size_raw": mb}

def run_code_analysis(path: Path) -> dict[str, float]:
    """
    Count lines of code and number of files in source directories.
    Excludes common build/dependency folders like node_modules, dist, etc.
    Returns dict with lines_of_code + file_count converted to 0–10 scores,
    plus raw counts for display purposes.
    """
    # Directories to exclude from counting
    exclude_dirs = {
        'node_modules', 'dist', 'build', '.git', 'venv', '__pycache__',
        '.next', '.nuxt', 'coverage', '.nyc_output', 'tmp', 'temp'
    }
    
    # File extensions to count as source code
    source_extensions = {
        '.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.html', '.htm', 
        '.css', '.scss', '.sass', '.less', '.json', '.yaml', '.yml',
        '.md', '.mdx', '.php', '.rb', '.go', '.rs', '.java', '.kt'
    }
    
    total_lines = 0
    file_count = 0
    
    for file_path in path.rglob('*'):
        # Skip if file is in excluded directory
        if any(exc_dir in file_path.parts for exc_dir in exclude_dirs):
            continue
            
        # Skip if not a file or doesn't have source extension
        if not file_path.is_file() or file_path.suffix not in source_extensions:
            continue
            
        try:
            # Count lines in file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = sum(1 for line in f if line.strip())  # Count non-empty lines
                total_lines += lines
                file_count += 1
        except (OSError, UnicodeDecodeError):
            # Skip files that can't be read
            continue
    
    return {
        "lines_of_code": lines_score(total_lines),
        "file_count": files_score(file_count),
        "lines_of_code_raw": total_lines,
        "file_count_raw": file_count
    }

def count_package_dependencies(path: Path) -> dict[str, float]:
    """
    Count total package dependencies from package.json files.
    Returns both the raw count and a score based on dependency complexity.
    """
    package_json_path = path / "package.json"
    
    if not package_json_path.exists():
        return {
            "package_dependencies": 0.0,
            "package_dependencies_raw": 0
        }
    
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # Count dependencies and devDependencies
        deps = len(package_data.get("dependencies", {}))
        dev_deps = len(package_data.get("devDependencies", {}))
        total_deps = deps + dev_deps
        
        # Score: fewer dependencies = better score
        # 20 deps = 10.0, 100+ deps = 0.0, linear scale
        score = max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))
        
        return {
            "package_dependencies": score,
            "package_dependencies_raw": total_deps
        }
        
    except (json.JSONDecodeError, OSError):
        return {
            "package_dependencies": 0.0,
            "package_dependencies_raw": 0
        }

def run_security_analysis(path: Path, url: str) -> dict[str, float]:
    """
    Comprehensive security analysis including:
    1. npm audit for dependency vulnerabilities
    2. Security headers analysis 
    3. Source code security scan for exposed secrets
    """
    security_score = 10.0
    issues_found = []
    
    # 1. NPM Audit - Check for dependency vulnerabilities
    try:
        code, output = sh("npm audit --json", cwd=path)
        if code == 0:
            audit_data = json.loads(output)
            vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", {})
            
            # Count high and critical vulnerabilities
            high_vulns = vulnerabilities.get("high", 0)
            critical_vulns = vulnerabilities.get("critical", 0)
            moderate_vulns = vulnerabilities.get("moderate", 0)
            
            # Deduct points based on severity
            vulnerability_penalty = (critical_vulns * 3.0) + (high_vulns * 2.0) + (moderate_vulns * 0.5)
            security_score -= min(vulnerability_penalty, 4.0)  # Max 4 points deduction
            
            if critical_vulns > 0 or high_vulns > 0:
                issues_found.append(f"{critical_vulns} critical, {high_vulns} high vulns")
                
    except (json.JSONDecodeError, subprocess.SubprocessError):
        # If npm audit fails, assume some risk
        security_score -= 1.0
        issues_found.append("npm audit failed")
    
    # 2. Security Headers Analysis
    try:
        import urllib.request
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            headers = response.headers
            
            # Check for important security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Any value is good
                'Content-Security-Policy': None,    # Any value is good
                'Referrer-Policy': None,           # Any value is good
            }
            
            missing_headers = []
            for header, expected in security_headers.items():
                header_value = headers.get(header, '').lower()
                if not header_value:
                    missing_headers.append(header)
                elif expected and isinstance(expected, list):
                    if not any(exp.lower() in header_value for exp in expected):
                        missing_headers.append(header)
                elif expected and isinstance(expected, str):
                    if expected.lower() not in header_value:
                        missing_headers.append(header)
            
            # Deduct points for missing security headers (max 2 points)
            header_penalty = min(len(missing_headers) * 0.3, 2.0)
            security_score -= header_penalty
            
            if missing_headers:
                issues_found.append(f"{len(missing_headers)} missing sec headers")
                
    except Exception:
        # If we can't check headers, assume some risk
        security_score -= 1.0
        issues_found.append("security headers check failed")
    
    # 3. Source Code Security Scan
    try:
        # Patterns for common security issues
        security_patterns = [
            (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']{10,}["\']', 'API keys'),
            (r'(?i)(secret|password)\s*[:=]\s*["\'][^"\']{8,}["\']', 'Hardcoded secrets'),
            (r'(?i)(access[_-]?token|accesstoken)\s*[:=]\s*["\'][^"\']{15,}["\']', 'Access tokens'),
            (r'(?i)\.innerHTML\s*[+]?=\s*[^;]+', 'Potential XSS via innerHTML'),
            (r'(?i)eval\s*\(', 'Dangerous eval() usage'),
            (r'(?i)document\.write\s*\(', 'Dangerous document.write()'),
        ]
        
        # Scan source files
        security_issues = 0
        scanned_files = 0
        
        for file_path in path.rglob('*'):
            # Skip non-source files and excluded directories
            if (any(exc_dir in file_path.parts for exc_dir in {'node_modules', 'dist', 'build', '.git'}) or
                file_path.suffix not in {'.js', '.jsx', '.ts', '.tsx', '.vue', '.html'}):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    scanned_files += 1
                    
                    for pattern, description in security_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            security_issues += len(matches)
                            
            except (OSError, UnicodeDecodeError):
                continue
        
        # Deduct points for security issues found in code (max 3 points)
        code_penalty = min(security_issues * 0.5, 3.0)
        security_score -= code_penalty
        
        if security_issues > 0:
            issues_found.append(f"{security_issues} code security issues")
            
    except Exception:
        # If code scan fails, minimal penalty
        security_score -= 0.5
        issues_found.append("code security scan failed")
    
    # Ensure score is within bounds
    security_score = max(0.0, min(10.0, security_score))
    
    return {
        "security": security_score,
        "security_issues": "; ".join(issues_found) if issues_found else "none"
    }

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
    try:   scores |= run_code_analysis(path)
    except Exception as e: rprint(f"[yellow]Code Analysis ⤵  {e}[/yellow]")
    try:   scores |= count_package_dependencies(path)
    except Exception as e: rprint(f"[yellow]Package Dependencies ⤵  {e}[/yellow]")
    try:   scores |= run_security_analysis(path, url)
    except Exception as e: rprint(f"[yellow]Security Analysis ⤵  {e}[/yellow]")
    # ── stop dev server (if started) ─────────────────────────────────────────
    if server:
        with suppress(ProcessLookupError, PermissionError, OSError):
            try:
                os.killpg(server.pid, signal.SIGINT)
            except:
                # Fallback: try to terminate the process directly
                server.terminate()
                time.sleep(1)
                if server.poll() is None:
                    server.kill()
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
        # Format the row with special handling for raw values
        row = [pr["name"]]
        for k in weights:
            if k in sc:
                if k == "performance" and "performance_raw" in sc:
                    row.append(f"{sc['performance_raw']*100:.0f}%")
                elif k == "build_time" and "build_time_raw" in sc:
                    row.append(f"{sc['build_time_raw']:.1f}s")
                elif k == "bundle_size" and "bundle_size_raw" in sc:
                    row.append(f"{sc['bundle_size_raw']:.1f}MB")
                elif k == "lines_of_code" and "lines_of_code_raw" in sc:
                    row.append(f"{int(sc['lines_of_code_raw'])} lines")
                elif k == "file_count" and "file_count_raw" in sc:
                    row.append(f"{int(sc['file_count_raw'])} files")
                elif k == "package_dependencies" and "package_dependencies_raw" in sc:
                    row.append(f"{int(sc['package_dependencies_raw'])} deps")
                else:
                    row.append(f"{sc[k]:.2f}")
            else:
                row.append("-")
        row.append(f"{weighted_total(sc, weights):.2f}")
        table.append(row)

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
