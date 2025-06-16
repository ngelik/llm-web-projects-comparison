#!/bin/bash

# =============================================================================
# run_test.sh - Automated Webbench Test Runner
# =============================================================================
# This script runs the webbench performance comparison tool with all configured
# projects, including dependency checks and setup automation.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=====================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}=====================================${NC}\n"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# List generated HTML reports
list_html_reports() {
    if [ -d "reports" ] && [ "$(ls -A reports/*_lighthouse_*.html 2>/dev/null)" ]; then
        echo ""
        print_status "Generated HTML Reports:"
        local count=0
        for report in reports/*_lighthouse_*.html; do
            if [ -f "$report" ]; then
                local filename=$(basename "$report")
                local filesize=$(ls -lh "$report" | awk '{print $5}')
                local timestamp=$(echo "$filename" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
                local project_name=$(echo "$filename" | sed 's/\(.*\)_lighthouse_[0-9]\{8\}_[0-9]\{6\}\.html/\1/')
                echo "  📄 $project_name ($timestamp) - $filesize"
                ((count++))
            fi
        done
        echo ""
        echo "📁 Total reports: $count"
        echo "📁 Reports saved in: $(pwd)/reports/"
        echo "💡 Open these HTML files in your browser for detailed Lighthouse analysis!"
        
        # Offer to open reports in browser (optional)
        if command_exists "open" && [ "$count" -gt 0 ]; then
            echo ""
            read -p "🌐 Open all reports in your default browser? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Opening HTML reports in browser..."
                for report in reports/*_lighthouse_*.html; do
                    if [ -f "$report" ]; then
                        open "$report"
                    fi
                done
                print_success "HTML reports opened in browser!"
            fi
        fi
        return 0
    else
        echo "  ⚠️  No HTML reports found in reports/ directory"
        return 1
    fi
}

# Setup and check Python virtual environment
setup_python_venv() {
    print_status "Setting up Python virtual environment..."
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        print_warning "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Check if we're already in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Already in virtual environment: $VIRTUAL_ENV"
    else
        print_status "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Check and install dependencies
    print_status "Checking Python dependencies..."
    if ! python -c "import yaml, tabulate, rich" 2>/dev/null; then
        print_warning "Installing Python dependencies from requirements.txt..."
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_success "Python dependencies are already installed"
    fi
}

# Check Node.js dependencies
check_node_deps() {
    print_status "Checking Node.js dependencies..."
    
    if ! command_exists "lighthouse"; then
        print_warning "Installing Lighthouse globally..."
        npm install -g lighthouse
    else
        print_success "Lighthouse is already installed"
    fi
    
    if ! command_exists "eslint"; then
        print_warning "Installing ESLint globally..."
        npm install -g eslint
    else
        print_success "ESLint is already installed"
    fi
}

# Check if project dependencies are installed
check_project_deps() {
    print_status "Checking project dependencies for all projects..."
    
    # List of projects to check
    local projects=(
        "apps/hot-and-cold-openai" 
        "apps/hot-and-cold-anthropic"
        "apps/hot-and-cold-google"
    )
    
    for project in "${projects[@]}"; do
        if [ -d "$project" ]; then
            if [ ! -d "$project/node_modules" ]; then
                print_warning "Installing dependencies for $project..."
                cd "$project" && npm install --legacy-peer-deps && cd - > /dev/null
                print_success "Dependencies installed for $project"
            else
                print_success "Dependencies already installed for $project"
            fi
        else
            print_warning "Project directory $project not found, skipping..."
        fi
    done
}

# Main execution
main() {
    print_header "🚀 WEBBENCH TEST RUNNER"
    
    # Check if we're in the right directory
    if [ ! -f "webbench.py" ]; then
        print_error "webbench.py not found! Please run this script from the project root directory."
        exit 1
    fi
    
    # Check if config files exist
    if [ ! -f "config.yaml" ] || [ ! -f "projects.yaml" ]; then
        print_error "Configuration files (config.yaml or projects.yaml) not found!"
        exit 1
    fi
    
    # Check system requirements
    print_header "📋 CHECKING SYSTEM REQUIREMENTS"
    
    if ! command_exists "python3"; then
        print_error "Python 3 is required but not installed"
        exit 1
    else
        print_success "Python 3 is installed"
    fi
    
    if ! command_exists "node"; then
        print_error "Node.js is required but not installed"
        exit 1
    else
        print_success "Node.js is installed"
    fi
    
    if ! command_exists "npm"; then
        print_error "npm is required but not installed"
        exit 1
    else
        print_success "npm is installed"
    fi
    
    # Install dependencies
    print_header "📦 SETTING UP DEPENDENCIES"
    setup_python_venv
    check_node_deps
    check_project_deps
    
    # Run the benchmark
    print_header "🔥 RUNNING WEBBENCH ANALYSIS"
    print_status "Starting webbench performance analysis..."
    print_status "This may take a few minutes as it will:"
    echo "  • Start the dev server for each project"
    echo "  • Run Lighthouse audits (performance, accessibility, SEO, best practices)"
    echo "  • Generate detailed HTML reports with timestamps (primary output)"
    echo "  • Extract scores for comparison table"
    echo "  • Analyze code quality with ESLint"
    echo "  • Perform comprehensive security analysis (vulnerabilities, headers, code)"
    echo "  • Build and measure bundle size"
    echo "  • Count lines of code and source files"
    echo "  • Generate comprehensive project scoring"
    echo ""
    
    # Create reports directory if it doesn't exist
    print_status "Preparing reports directory..."
    mkdir -p reports
    
    # Clean up any old reports if desired
    local old_reports_count=$(ls reports/*_lighthouse_*.html 2>/dev/null | wc -l || echo 0)
    if [ "$old_reports_count" -gt 0 ]; then
        print_warning "Found $old_reports_count existing HTML reports in reports/ directory"
        echo "💡 Previous reports will be preserved with their timestamps"
    fi
    
    print_success "Reports directory ready: $(pwd)/reports/"
    
    # Run webbench with error handling
    if python webbench.py --config config.yaml --projects projects.yaml; then
        print_header "✅ BENCHMARK COMPLETE"
        print_success "Webbench analysis completed successfully!"
        
        # Show generated HTML reports
        list_html_reports
        
        echo ""
        echo "📊 RESULTS SUMMARY:"
        echo "The table above shows comprehensive scores for your web application."
        echo "Each metric is scored from 0-10, with 10 being the best."
        echo ""
        echo "📄 HTML REPORTS CONTAIN:"
        echo "  • Detailed performance metrics (Core Web Vitals, load times)"
        echo "  • Accessibility audit results with specific fix recommendations"
        echo "  • SEO analysis with meta tags, structured data, and mobile usability"
        echo "  • Best practices violations and security recommendations"
        echo "  • Progressive Web App (PWA) compliance checklist"
        echo "  • Opportunities for performance optimization"
        echo "  • Diagnostics section with technical details"
        echo ""
        echo "🎯 METRICS EVALUATED:"
        echo "  • Performance (16%): Core Web Vitals, loading speed"
        echo "  • Accessibility (12%): WCAG compliance, screen reader support"
        echo "  • Code Quality (12%): ESLint errors/warnings count"
        echo "  • Build Time (12%): Production build duration"
        echo "  • Bundle Size (12%): Final distribution size"
        echo "  • Security (10%): Vulnerability scanning, security headers, code analysis"
        echo "  • Best Practices (8%): Modern web standards"
        echo "  • SEO (6%): Search engine optimization"
        echo "  • Package Dependencies (5%): npm dependency count (20 deps ideal)"
        echo "  • Lines of Code (5%): Source code complexity (500 lines ideal)"
        echo "  • File Count (5%): Project organization (10 files ideal)"
        echo ""
        echo "📈 NEXT STEPS:"
        echo "  1. Review the comparison results above for all projects"
        echo "  2. Open HTML reports in reports/ directory for detailed analysis"
        echo "  3. Edit projects.yaml to modify project configurations"
        echo "  4. Adjust metric weights in config.yaml if needed"
        echo "  5. Run this script again: ./run_test.sh"
        echo ""
        echo "🔍 CURRENT PROJECTS CONFIGURED:"
        echo "  • Hot & Cold (OpenAI) - React/TypeScript/Vite"
        echo "  • Hot & Cold (Anthropic) - React/TypeScript/Vite"
        echo "  • Hot & Cold (Google) - React/TypeScript/Vite"
    else
        print_header "❌ BENCHMARK FAILED"
        print_error "Webbench analysis failed. Check the error messages above."
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Script interrupted by user"; exit 1' INT

# Run main function
main "$@" 