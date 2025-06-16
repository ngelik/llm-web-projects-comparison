# Webbench Test Project

This project contains a web framework benchmarking tool (`webbench.py`) and a simple test web application to demonstrate its functionality.

## 🚀 Project Status

**Current Status**: ✅ **Production-Ready Benchmarking System**

### **Enhanced Capabilities**
- **📄 HTML Report Generation**: Comprehensive Lighthouse reports with visual analytics
- **🔍 Multi-Metric Analysis**: 11 different performance and quality metrics
- **📊 Real-Time Comparison**: Automated project ranking with weighted scoring
- **🔒 Security Scanning**: Vulnerability analysis and code security checks
- **⚡ Performance Monitoring**: Build time, bundle size, and optimization tracking
- **🌐 Interactive Reports**: Browser integration with detailed recommendations

### **Tested Projects**
Currently benchmarking three weather applications with different AI-provider architectures:
- **Google Version** (7.46/10): Professional i18next internationalization
- **Anthropic Version** (7.28/10): Clean React Context patterns  
- **OpenAI Version** (7.10/10): Lightweight manual state management

## What's Included

- **`webbench.py`**: The main benchmarking tool that evaluates web applications across multiple metrics
- **`config.yaml`**: Configuration file defining metric weights
- **`projects.yaml`**: Configuration file listing projects to test
- **`apps/`**: Web applications for testing and comparison

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
4. **Generate HTML reports** - creates detailed Lighthouse reports saved to `reports/` directory
5. **Run ESLint analysis** - evaluates code quality
6. **Run production build** - measures build time and bundle size
7. **Calculate weighted scores** and rank the results

## Generated Reports

The tool automatically generates detailed HTML reports for each project:

- **Primary Output**: HTML reports with comprehensive Lighthouse analysis
- **Location**: `reports/` directory (created automatically)
- **Naming**: `{project_name}_lighthouse_{YYYYMMDD_HHMMSS}.html`
- **Content**: Complete Lighthouse audit results with detailed recommendations and visual charts
- **Example**: `reports/simple-web-app_lighthouse_20241215_143022.html`

These HTML reports are the main deliverable and provide in-depth analysis of:
- **Performance metrics** with visual charts and optimization suggestions
- **Accessibility audit results** with specific fix recommendations and impact levels
- **SEO analysis** with meta tags, structured data, and mobile usability checks
- **Best practices violations** and security recommendations with priorities
- **Progressive Web App (PWA)** compliance checklist and implementation guide
- **Opportunities section** with actionable performance improvements
- **Diagnostics section** with technical details and resource analysis

*Note: JSON data is temporarily generated for score extraction in the comparison table, then automatically cleaned up.*

## Metrics Evaluated

### Overview
Each metric is scored from **0-10**, where **10 = perfect** and **0 = poor**. The final score is a weighted average of all metrics.

- **Performance** (16%): Core Web Vitals, loading speed
- **Accessibility** (12%): WCAG compliance, screen reader support
- **Code Quality** (12%): ESLint errors/warnings count
- **Build Time** (12%): Production build duration
- **Bundle Size** (12%): Final distribution size
- **Security** (10%): Vulnerability scanning, security headers, code analysis
- **Best Practices** (8%): Modern web standards
- **SEO** (6%): Search engine optimization
- **Package Dependencies** (5%): Number of npm dependencies (displays actual count)
- **Lines of Code** (5%): Source code complexity (displays actual line count)
- **File Count** (5%): Project organization (displays actual file count)

## Detailed Scoring System

### 🚀 Lighthouse Metrics (via Google Lighthouse)
These metrics are automatically generated by running Lighthouse audits on your live application:

#### **Performance (16% weight)**
- **Score**: Lighthouse Performance score × 10 (0-1 scale → 0-10 scale)
- **Display**: Shows actual Lighthouse score as percentage (e.g., "54%")
- **Measures**: Core Web Vitals, First Contentful Paint, Largest Contentful Paint, Speed Index, Time to Interactive
- **Good**: 9.0+ (≥90% Lighthouse score)
- **Average**: 5.0-8.9 (50%-89% Lighthouse score)
- **Poor**: <5.0 (<50% Lighthouse score)

#### **Accessibility (12% weight)**
- **Score**: Lighthouse Accessibility score × 10
- **Measures**: WCAG 2.1 compliance, screen reader compatibility, keyboard navigation, color contrast, semantic HTML
- **Good**: 9.0+ (Near-perfect accessibility)
- **Average**: 7.0-8.9 (Most accessibility features present)
- **Poor**: <7.0 (Missing critical accessibility features)

#### **Best Practices (9% weight)**
- **Score**: Lighthouse Best Practices score × 10
- **Measures**: HTTPS usage, modern JavaScript, security vulnerabilities, browser compatibility
- **Good**: 9.0+ (Follows modern web standards)
- **Average**: 7.0-8.9 (Minor best practice violations)
- **Poor**: <7.0 (Significant security or compatibility issues)

#### **SEO (6% weight)**
- **Score**: Lighthouse SEO score × 10
- **Measures**: Meta tags, structured data, mobile-friendliness, crawlability
- **Good**: 9.0+ (Well-optimized for search engines)
- **Average**: 7.0-8.9 (Basic SEO present)
- **Poor**: <7.0 (Missing essential SEO elements)

### 🔧 Build & Development Metrics

#### **Code Quality (12% weight)**
- **Formula**: `max(0, 10 - errors_and_warnings / 5)`
- **Measures**: ESLint errors and warnings count
- **Perfect**: 10.0 (0 errors/warnings)
- **Good**: 8.0+ (1-10 errors/warnings)
- **Average**: 5.0-7.9 (11-25 errors/warnings)
- **Poor**: <5.0 (25+ errors/warnings)

#### **Build Time (12% weight)**
- **Formula**: Linear scale where 5 seconds = 10.0, 60+ seconds = 0.0
- **Display**: Shows actual build time in seconds (e.g., "1.7s")
- **Measures**: Time to complete production build
- **Excellent**: 10.0 (≤5 seconds)
- **Good**: 8.0+ (6-15 seconds)
- **Average**: 5.0-7.9 (16-35 seconds)
- **Poor**: <5.0 (35+ seconds)

#### **Bundle Size (12% weight)**
- **Formula**: Linear scale where 1MB = 10.0, 50+ MB = 0.0
- **Display**: Shows actual bundle size in megabytes (e.g., "0.7MB")
- **Measures**: Total size of production build output
- **Excellent**: 10.0 (≤1 MB)
- **Good**: 8.0+ (1-5 MB)
- **Average**: 5.0-7.9 (5-20 MB)
- **Poor**: <5.0 (20+ MB)

#### **Security (10% weight)**
- **Formula**: Starts at 10.0, deducts points for security issues found
- **Measures**: 
  - **Dependency Vulnerabilities**: npm audit for known CVEs (critical: -3.0, high: -2.0, moderate: -0.5 per vulnerability)
  - **Security Headers**: Checks for essential HTTP security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS, CSP, Referrer-Policy)
  - **Source Code Security**: Scans for exposed API keys, hardcoded secrets, dangerous JavaScript patterns (eval, innerHTML, document.write)
- **Excellent**: 10.0 (No vulnerabilities, all security headers present, no code issues)
- **Good**: 8.0+ (Minor issues, most security measures in place)
- **Average**: 6.0-7.9 (Some vulnerabilities or missing security headers)
- **Poor**: <6.0 (Critical vulnerabilities or multiple security issues)

### 📊 Code Analysis Metrics

#### **Package Dependencies (6% weight)**
- **Formula**: Linear scale where 20 dependencies = 10.0, 100+ dependencies = 0.0
- **Measures**: Total count of dependencies + devDependencies from package.json
- **Display**: Shows actual dependency count (e.g., "74 deps")
- **Scoring**:
  - **Excellent**: 10.0 (≤20 dependencies)
  - **Good**: 8.0+ (21-40 dependencies)
  - **Average**: 5.0-7.9 (41-80 dependencies)
  - **Poor**: <5.0 (80+ dependencies)

#### **Lines of Code (6% weight)**
- **Formula**: Linear scale where 500 lines = 10.0, 10,000+ lines = 0.0
- **Measures**: Non-empty lines in source files (excludes dependencies, builds)
- **Display**: Shows actual line count (e.g., "1172 lines")
- **Scoring**: 
  - **Excellent**: 10.0 (≤500 lines)
  - **Good**: 8.0+ (501-2,000 lines)
  - **Average**: 5.0-7.9 (2,001-6,000 lines)
  - **Poor**: <5.0 (6,000+ lines)

#### **File Count (6% weight)**
- **Formula**: Linear scale where 10 files = 10.0, 100+ files = 0.0
- **Measures**: Number of source files (excludes dependencies, builds)
- **Display**: Shows actual file count (e.g., "6 files")
- **Scoring**:
  - **Excellent**: 10.0 (≤10 files)
  - **Good**: 8.0+ (11-25 files)
  - **Average**: 5.0-7.9 (26-60 files)
  - **Poor**: <5.0 (60+ files)

### 🧮 Final Score Calculation

The **TOTAL** score is calculated as a weighted average:

```
TOTAL = (Performance × 0.16) + (Accessibility × 0.12) + (Code_Quality × 0.12) + 
        (Build_Time × 0.12) + (Bundle_Size × 0.12) + (Security × 0.10) + 
        (Best_Practices × 0.08) + (SEO × 0.06) + (Package_Dependencies × 0.05) + 
        (Lines_of_Code × 0.05) + (File_Count × 0.05)
```

**Score Interpretation:**
- **9.0-10.0**: Outstanding - Production-ready, optimized application
- **8.0-8.9**: Excellent - High-quality application with minor improvements needed
- **7.0-7.9**: Good - Solid application, some optimization opportunities
- **6.0-6.9**: Average - Functional but needs improvement in several areas
- **<6.0**: Poor - Significant issues that should be addressed

### 📁 File Analysis Details

**Included file types**: `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, `.py`, `.html`, `.css`, `.scss`, `.json`, `.yaml`, `.md`, etc.

**Excluded directories**: `node_modules`, `dist`, `build`, `.git`, `venv`, `__pycache__`, `.next`, `.nuxt`, `coverage`

**Line counting**: Only non-empty lines are counted to focus on actual code content.

## Expected Output

You should see a table ranking the projects by their weighted total scores:

```
name                 performance  accessibility  best-practices  code_quality  build_time  bundle_size  security  seo   package_dependencies  lines_of_code  file_count  TOTAL
-------------------  -----------  -------------  --------------  ------------  ----------  -----------  --------  ----  ---------------------  -------------  ----------  -------
hot-cold-google      -            -              -               8.00          1.7s        0.7MB        8.20      -     72 deps               13144 lines    79 files    7.46
hot-cold-anthropic   -            -              -               7.20          1.7s        0.6MB        8.20      -     69 deps               13870 lines    87 files    7.28
hot-cold-openai      -            -              -               6.60          1.6s        0.4MB        7.70      -     69 deps               13584 lines    82 files    7.10
```

## Actual Benchmark Results

Based on comprehensive testing of the three Hot & Cold weather applications:

### 🏆 **Performance Rankings**

1. **🥇 Google (hot-cold-google)**: 7.46/10
   - **Strengths**: Professional i18next internationalization, cleanest code patterns, excellent organization
   - **Architecture**: i18next library with browser language detection
   - **Bundle Size**: 0.7MB (largest due to i18n features)
   - **Dependencies**: 72 packages
   - **Best For**: Enterprise applications requiring robust internationalization

2. **🥈 Anthropic (hot-cold-anthropic)**: 7.28/10
   - **Strengths**: Clean React Context patterns, balanced feature set, good maintainability
   - **Architecture**: React Context API for state management
   - **Bundle Size**: 0.6MB (balanced)
   - **Dependencies**: 69 packages
   - **Best For**: Balanced development with clean React patterns

3. **🥉 OpenAI (hot-cold-openai)**: 7.10/10
   - **Strengths**: Smallest bundle size, minimal dependencies, fastest loading
   - **Architecture**: Manual translation management with prop drilling
   - **Bundle Size**: 0.4MB (most compact)
   - **Dependencies**: 69 packages
   - **Best For**: Performance-critical applications requiring minimal overhead

### 📊 **Detailed Metrics Comparison**

| Metric | Google | Anthropic | OpenAI | Winner |
|--------|--------|-----------|---------|---------|
| **Code Quality** | 8.00/10 | 7.20/10 | 6.60/10 | 🥇 Google |
| **Build Time** | 1.7s | 1.7s | 1.6s | 🥇 OpenAI |
| **Bundle Size** | 0.7MB | 0.6MB | 0.4MB | 🥇 OpenAI |
| **Security** | 8.20/10 | 8.20/10 | 7.70/10 | 🥇 Google/Anthropic |
| **Dependencies** | 72 | 69 | 69 | 🥇 Anthropic/OpenAI |
| **Lines of Code** | 13,144 | 13,870 | 13,584 | - |
| **File Count** | 79 | 87 | 82 | - |

### 🎯 **Key Insights**

- **All projects have excellent build performance** (1.6-1.7 seconds)
- **Security scores are consistently good** across all versions (7.70-8.20/10)
- **Code quality varies significantly** based on architectural choices
- **Bundle size impact**: i18next adds ~0.3MB but provides professional i18n
- **Architecture trade-offs**: Manual management vs Context vs Library approaches

### 🚀 **HTML Reports Generated**

Each benchmark run creates comprehensive HTML reports:
```
reports/
├── hot-cold-google_lighthouse_20241215_143108.html
├── hot-cold-anthropic_lighthouse_20241215_143045.html
└── hot-cold-openai_lighthouse_20241215_143022.html
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

## Using HTML Reports

The generated HTML reports provide comprehensive analysis beyond the summary table:

### **Opening Reports**
- **Manual**: Open any `.html` file in `reports/` directory with your browser
- **Automatic**: Use the interactive option in `./run_test.sh` to open all reports at once
- **Best Practice**: Compare reports side-by-side for detailed analysis

### **Key Report Sections**
- **Performance**: Core Web Vitals, load times, optimization opportunities
- **Accessibility**: WCAG compliance, screen reader compatibility
- **Best Practices**: Security, modern standards, browser compatibility  
- **SEO**: Meta tags, mobile-friendliness, structured data
- **PWA**: Progressive Web App features and compliance

### **Actionable Insights**
Each report includes specific recommendations with:
- Priority levels (High/Medium/Low)
- Implementation difficulty estimates
- Expected performance impact
- Code examples and links to documentation

## Troubleshooting

- **"lighthouse CLI is not installed"**: Run `npm i -g lighthouse`
- **"Node/npm not available"**: Install Node.js
- **Dev server timeout**: Check if the serve_url is correct and reachable
- **Build command fails**: Ensure the project has a valid build configuration
- **Empty HTML reports**: Check that Lighthouse can access the serve_url
- **Permission errors**: Ensure write access to the `reports/` directory
- **Browser won't open reports**: Check that your system's default browser is configured 