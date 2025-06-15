#!/bin/bash

# =============================================================================
# setup.sh - Project Setup Script
# =============================================================================
# This script sets up the complete development environment for the webbench
# project including virtual environment and all dependencies.

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

main() {
    print_header "🔧 WEBBENCH PROJECT SETUP"
    
    # Check system requirements
    print_status "Checking system requirements..."
    
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
    
    # Create virtual environment
    print_header "🐍 SETTING UP PYTHON ENVIRONMENT"
    
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Install global Node.js tools
    print_header "📦 INSTALLING GLOBAL TOOLS"
    
    if ! command_exists "lighthouse"; then
        print_status "Installing Lighthouse globally..."
        npm install -g lighthouse
        print_success "Lighthouse installed"
    else
        print_success "Lighthouse is already installed"
    fi
    
    if ! command_exists "eslint"; then
        print_status "Installing ESLint globally..."
        npm install -g eslint
        print_success "ESLint installed"
    else
        print_success "ESLint is already installed"
    fi
    
    # Install project dependencies
    print_header "🏗️ SETTING UP TEST PROJECT"
    
    if [ ! -d "simple-web-app/node_modules" ]; then
        print_status "Installing test project dependencies..."
        cd simple-web-app && npm install && cd ..
        print_success "Test project dependencies installed"
    else
        print_success "Test project dependencies already installed"
    fi
    
    # Make scripts executable
    print_status "Making scripts executable..."
    chmod +x run_test.sh
    chmod +x setup.sh
    print_success "Scripts are now executable"
    
    # Final success message
    print_header "✅ SETUP COMPLETE"
    print_success "Webbench project is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Run the test: ./run_test.sh"
    echo "  2. Or activate venv manually: source venv/bin/activate"
    echo "  3. Add more projects to projects.yaml for comparison"
    echo ""
    echo "📊 Webbench now evaluates 10 comprehensive metrics:"
    echo "  Performance • Accessibility • Code Quality • Build Time • Bundle Size"
    echo "  Best Practices • Lines of Code • File Count • SEO • PWA"
    echo ""
    echo "Happy benchmarking! 🚀"
}

# Handle script interruption
trap 'print_error "Setup interrupted by user"; exit 1' INT

# Run main function
main "$@" 