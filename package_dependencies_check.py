#!/usr/bin/env python3
"""
Diagnostic script to verify package_dependencies calculation specifically
"""

import json
import yaml
from pathlib import Path

def test_package_dependencies_directly():
    """Test package dependencies counting directly on one of the projects"""
    print("🔍 PACKAGE DEPENDENCIES TEST")
    print("=" * 50)
    
    # Test on hot-cold-google
    app_path = Path("./apps/hot-and-cold-google")
    package_json_path = app_path / "package.json"
    
    print(f"Testing package dependencies on: {app_path}")
    print(f"Package.json path: {package_json_path}")
    
    if not package_json_path.exists():
        print("❌ package.json not found")
        return None
    
    try:
        # Read and parse package.json exactly as webbench does
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        print("✅ package.json loaded successfully")
        
        # Count dependencies and devDependencies
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        
        deps_count = len(dependencies)
        dev_deps_count = len(dev_dependencies)
        total_deps = deps_count + dev_deps_count
        
        print(f"\nDependency Analysis:")
        print(f"  Production dependencies: {deps_count}")
        print(f"  Development dependencies: {dev_deps_count}")
        print(f"  Total dependencies: {total_deps}")
        
        # Show some examples
        if dependencies:
            print(f"\nProduction dependencies (first 5):")
            for i, (name, version) in enumerate(list(dependencies.items())[:5], 1):
                print(f"  {i}. {name}: {version}")
            if len(dependencies) > 5:
                print(f"  ... and {len(dependencies) - 5} more")
        
        if dev_dependencies:
            print(f"\nDevelopment dependencies (first 5):")
            for i, (name, version) in enumerate(list(dev_dependencies.items())[:5], 1):
                print(f"  {i}. {name}: {version}")
            if len(dev_dependencies) > 5:
                print(f"  ... and {len(dev_dependencies) - 5} more")
        
        # Calculate score using webbench formula
        # 20 deps = 10.0, 100+ deps = 0.0, linear scale
        score = max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))
        
        print(f"\nScore calculation:")
        print(f"  Formula: max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))")
        print(f"  Score: max(0.0, min(10.0, 10.0 - ({total_deps} - 20) * 10.0 / 80.0))")
        print(f"  Score: {score:.2f}/10")
        
        return {
            "deps_count": deps_count,
            "dev_deps_count": dev_deps_count,
            "total_deps": total_deps,
            "score": score,
            "dependencies": dependencies,
            "dev_dependencies": dev_dependencies
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing package.json: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return None

def verify_package_dependencies_scoring():
    """Verify how package_dependencies is scored in webbench"""
    print("\n📊 PACKAGE DEPENDENCIES SCORING VERIFICATION")
    print("=" * 50)
    
    # Simulate the webbench logic for package_dependencies
    test_dep_counts = [10, 20, 30, 50, 70, 100, 120]  # Sample dependency counts
    
    print("Dependency Count → Webbench Score:")
    for dep_count in test_dep_counts:
        score = max(0.0, min(10.0, 10.0 - (dep_count - 20) * 10.0 / 80.0))
        print(f"  {dep_count:3d} deps → {score:4.1f}/10")
    
    print(f"\nScoring Formula: max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))")
    print(f"• ≤20 dependencies = 10.0 (perfect)")
    print(f"• 60 dependencies = 5.0 (average)")
    print(f"• ≥100 dependencies = 0.0 (worst)")
    print(f"• Linear interpolation between 20 and 100 deps")

def check_package_dependencies_weight():
    """Check package_dependencies weight in final calculation"""
    print("\n⚖️ PACKAGE DEPENDENCIES WEIGHT VERIFICATION")
    print("=" * 50)
    
    config = yaml.safe_load(Path("config.yaml").read_text())
    package_deps_weight = config["metrics"]["package_dependencies"]["weight"]
    
    print(f"Package dependencies weight: {package_deps_weight} ({package_deps_weight * 100:.0f}%)")
    
    # Sample calculation
    sample_score = 3.5  # Average dependency score  
    contribution = sample_score * package_deps_weight
    
    print(f"Sample: {sample_score}/10 × {package_deps_weight} = {contribution:.3f} contribution to total")
    print(f"This represents {contribution/10*100:.1f}% of the maximum possible total score")
    
    # Compare with current project scores (estimated from recent output)
    print("\nCurrent Project Package Dependencies Analysis:")
    project_deps = {
        "hot-cold-google": 72,   # 72 deps from recent output
        "hot-cold-anthropic": 69, # 69 deps from recent output
        "hot-cold-openai": 69     # 69 deps from recent output
    }
    
    for project, dep_count in project_deps.items():
        score = max(0.0, min(10.0, 10.0 - (dep_count - 20) * 10.0 / 80.0))
        contribution = score * package_deps_weight
        print(f"  {project:20}: {dep_count:3d} deps → {score:4.1f} × {package_deps_weight:.3f} = {contribution:.3f}")

def analyze_dependency_categories():
    """Analyze what types of dependencies are present"""
    print("\n📦 DEPENDENCY CATEGORIES ANALYSIS")
    print("=" * 50)
    
    app_path = Path("./apps/hot-and-cold-google")
    package_json_path = app_path / "package.json"
    
    if not package_json_path.exists():
        print("❌ package.json not found")
        return
    
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        
        # Categorize dependencies by type
        categories = {
            "React/UI": ["react", "react-dom", "@types/react", "react-router", "react-query"],
            "Build Tools": ["vite", "webpack", "rollup", "parcel", "esbuild"],
            "TypeScript": ["typescript", "@types/", "ts-", "tsx"],
            "Linting/Formatting": ["eslint", "prettier", "@eslint/", "eslint-plugin"],
            "Testing": ["jest", "vitest", "testing-library", "@testing-library", "cypress"],
            "Styling": ["tailwind", "styled-components", "emotion", "@emotion", "sass"],
            "Utilities": ["lodash", "axios", "date-fns", "uuid", "clsx"],
            "Development": ["@vitejs/", "vite-plugin", "nodemon", "concurrently"]
        }
        
        categorized = {cat: [] for cat in categories.keys()}
        uncategorized = []
        
        all_deps = {**dependencies, **dev_dependencies}
        
        for dep_name, version in all_deps.items():
            categorized_flag = False
            for category, keywords in categories.items():
                if any(keyword in dep_name.lower() for keyword in keywords):
                    categorized[category].append((dep_name, version))
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                uncategorized.append((dep_name, version))
        
        print("Dependencies by category:")
        for category, deps in categorized.items():
            if deps:
                print(f"\n{category} ({len(deps)} packages):")
                for dep_name, version in sorted(deps)[:3]:  # Show first 3
                    print(f"  • {dep_name}: {version}")
                if len(deps) > 3:
                    print(f"  ... and {len(deps) - 3} more")
        
        if uncategorized:
            print(f"\nOther ({len(uncategorized)} packages):")
            for dep_name, version in sorted(uncategorized)[:3]:
                print(f"  • {dep_name}: {version}")
            if len(uncategorized) > 3:
                print(f"  ... and {len(uncategorized) - 3} more")
                
    except Exception as e:
        print(f"Error analyzing dependencies: {e}")

def package_dependencies_scoring_guide():
    """Explain package_dependencies scoring methodology"""
    print("\n📋 PACKAGE DEPENDENCIES SCORING GUIDE")
    print("=" * 50)
    
    print("Package Dependencies Scoring:")
    print("• Counts total dependencies from package.json")
    print("• Includes both dependencies and devDependencies")
    print("• Fewer dependencies = higher score (less complexity)")
    print("• Formula: max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))")
    
    print("\nWhat Affects Dependency Count:")
    factors = [
        "Framework choice (React, Vue, Angular)",
        "Build tooling complexity", 
        "UI component libraries",
        "Utility libraries (lodash, date-fns)",
        "Development tools (linting, testing)",
        "TypeScript type definitions",
        "Styling solutions (CSS frameworks)",
        "State management libraries",
        "HTTP clients and data fetching",
        "Testing frameworks and tools"
    ]
    
    for factor in factors:
        print(f"  • {factor}")
    
    print("\nDependency Count Categories:")
    print("  10.0: Excellent - ≤20 dependencies (minimal, focused)")
    print("   8.0: Very Good - 21-35 dependencies")
    print("   6.0: Good - 36-50 dependencies")  
    print("   4.0: Average - 51-70 dependencies")
    print("   2.0: Below Average - 71-85 dependencies")
    print("   1.0: Poor - 86-95 dependencies")
    print("   0.0: Very Poor - ≥100 dependencies")
    
    print("\nOptimization Tips:")
    tips = [
        "Remove unused dependencies regularly",
        "Use built-in browser APIs instead of libraries",
        "Choose lightweight alternatives",
        "Avoid duplicate functionality",
        "Use peer dependencies when possible",
        "Consider bundling related packages",
        "Audit dependencies with npm audit",
        "Use tools like depcheck to find unused deps",
        "Prefer dependencies over devDependencies for runtime",
        "Consider the dependency tree depth"
    ]
    
    for tip in tips:
        print(f"  • {tip}")

def compare_all_projects():
    """Compare package dependencies across all three projects"""
    print("\n🔄 ALL PROJECTS COMPARISON")
    print("=" * 50)
    
    projects = ["hot-and-cold-google", "hot-and-cold-anthropic", "hot-and-cold-openai"]
    
    for project in projects:
        app_path = Path(f"./apps/{project}")
        package_json_path = app_path / "package.json"
        
        print(f"\n{project}:")
        
        if not package_json_path.exists():
            print("  ❌ package.json not found")
            continue
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            
            deps_count = len(dependencies)
            dev_deps_count = len(dev_dependencies)
            total_deps = deps_count + dev_deps_count
            
            score = max(0.0, min(10.0, 10.0 - (total_deps - 20) * 10.0 / 80.0))
            
            print(f"  Production: {deps_count}, Dev: {dev_deps_count}, Total: {total_deps}")
            print(f"  Score: {score:.1f}/10")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("📦 PACKAGE DEPENDENCIES CALCULATION VERIFICATION")
    print("=" * 60)
    
    verify_package_dependencies_scoring()
    check_package_dependencies_weight()
    package_dependencies_scoring_guide()
    
    # Ask user if they want to run the live test
    response = input("\nRun live package dependencies test? (y/n): ").lower().strip()
    if response == 'y':
        live_result = test_package_dependencies_directly()
        if live_result:
            print(f"\n🎯 VERIFICATION RESULT:")
            print(f"Total dependencies: {live_result['total_deps']}")
            print(f"Production: {live_result['deps_count']}, Development: {live_result['dev_deps_count']}")
            print(f"Calculated score: {live_result['score']:.2f}/10")
            print(f"Expected in webbench: {live_result['score']:.1f}")
            
            # Show dependency analysis
            analyze_dependency_categories()
            
            # Compare all projects
            compare_all_projects()
    else:
        print("Skipping live test.")
        # Still show analysis if possible
        analyze_dependency_categories()
        compare_all_projects() 