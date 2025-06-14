#!/bin/bash

# =============================================================================
# run_test.sh - Automated Webbench Test Runner
# =============================================================================
# This script runs the webbench performance comparison tool with the 
# simple-web-app test project, including dependency checks.

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
    
    # Activate venv and install dependencies
    print_status "Activating virtual environment and checking dependencies..."
    source venv/bin/activate
    
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
    print_status "Checking project dependencies..."
    
    if [ ! -d "simple-web-app/node_modules" ]; then
        print_warning "Installing project dependencies..."
        cd simple-web-app && npm install && cd ..
        print_success "Project dependencies installed"
    else
        print_success "Project dependencies are already installed"
    fi
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
    echo "  • Start the dev server"
    echo "  • Run Lighthouse audits"
    echo "  • Analyze code quality with ESLint"
    echo "  • Build and measure bundle size"
    echo ""
    
    # Run webbench with error handling (using virtual environment)
    if source venv/bin/activate && python webbench.py --config config.yaml --projects projects.yaml; then
        print_header "✅ BENCHMARK COMPLETE"
        print_success "Webbench analysis completed successfully!"
        echo ""
        echo "The table above shows the performance scores for your web application."
        echo "Each metric is scored from 0-10, with 10 being the best."
        echo ""
        echo "To add more projects for comparison:"
        echo "  1. Edit projects.yaml to add new project configurations"
        echo "  2. Run this script again: ./run_test.sh"
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