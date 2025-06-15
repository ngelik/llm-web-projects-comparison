# Webbench Test Project

This project contains a web framework benchmarking tool (`webbench.py`) and a simple test web application to demonstrate its functionality.

## What's Included

- **`webbench.py`**: The main benchmarking tool that evaluates web applications across multiple metrics
- **`config.yaml`**: Configuration file defining metric weights
- **`projects.yaml`**: Configuration file listing projects to test
- **`simple-web-app/`**: A sample web application for testing

## Prerequisites

### System Requirements
- Python 3.9+ 
- Node.js and npm
- Git (optional, for version control)

### Automated Setup (Recommended)

```bash
# Run the setup script to configure everything
./setup.sh
```

### Manual Setup (Alternative)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install global Node.js tools
npm install -g lighthouse eslint

# Install test project dependencies
cd simple-web-app && npm install && cd ..
```

### Manual Installation (Alternative)
If you prefer not to use a virtual environment:

```bash
# Python dependencies
pip install pyyaml tabulate rich

# Global Node.js tools
npm install -g lighthouse eslint
```

## Quick Test

### Option 1: Automated Script (Recommended)
Run the automated test script that handles all dependencies including virtual environment setup:

```bash
./run_test.sh
```

### Option 2: Manual Run (with Virtual Environment)
To test the webbench tool manually with the included simple web app:

```bash
# Activate virtual environment
source venv/bin/activate

# Run webbench
python webbench.py --config config.yaml --projects projects.yaml
```

### Option 3: Manual Run (without Virtual Environment)
If you're not using a virtual environment:

```bash
python3 webbench.py --config config.yaml --projects projects.yaml
```

## What the Test Will Evaluate

The webbench tool will automatically:

1. **Start the dev server** for the simple-web-app
2. **Wait for it to be ready** (polls http://localhost:3000)
3. **Run Lighthouse audit** - measures performance, accessibility, SEO, PWA, best practices
4. **Run ESLint analysis** - evaluates code quality
5. **Run production build** - measures build time and bundle size
6. **Calculate weighted scores** and rank the results

## Metrics Evaluated

- **Performance** (18%): Core Web Vitals, loading speed
- **Accessibility** (13%): WCAG compliance, screen reader support
- **Best Practices** (9%): Security, modern web standards
- **Code Quality** (13%): ESLint errors/warnings count
- **Build Time** (13%): Production build duration
- **Bundle Size** (13%): Final distribution size
- **Lines of Code** (6%): Source code complexity (500 lines ideal, 10k+ lines poor)
- **File Count** (5%): Project organization (10 files ideal, 100+ files poor)
- **SEO** (5%): Search engine optimization
- **PWA** (5%): Progressive Web App features

## Expected Output

You should see a table ranking the projects by their weighted total scores:

```
name             performance  accessibility  best-practices  code_quality  build_time  bundle_size  lines_of_code  file_count  seo   pwa   TOTAL
---------------  -----------  -------------  --------------  ------------  ----------  -----------  -------------  ----------  ----  ----  -------
simple-web-app   10.00        9.60           9.60           10.00         10.00       10.00        8.50           8.00        10.00 -     9.65
```

## Adding More Projects

To test additional web projects:

1. Add them to `projects.yaml`
2. Ensure each project has the required commands:
   - `serve_command`: Command to start dev server
   - `serve_url`: URL where the dev server runs
   - `build_command`: Command to build for production
   - `dist_folder`: Name of the output directory

## Customizing Metrics

Edit `config.yaml` to adjust metric weights. All weights must sum to 1.0.

## Troubleshooting

- **"lighthouse CLI is not installed"**: Run `npm i -g lighthouse`
- **"Node/npm not available"**: Install Node.js
- **Dev server timeout**: Check if the serve_url is correct and reachable
- **Build command fails**: Ensure the project has a valid build configuration 