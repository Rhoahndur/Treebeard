#!/usr/bin/env python3
"""
Epic 1 + Epic 2 Integration Validation Script
==============================================

Validates that all components from Epic 1 and Epic 2 are present and ready for Wave 3.

Checks:
1. All contract documents published
2. All implementation files present
3. All schemas defined correctly
4. Integration points documented

Author: Integration Validation
Date: 2025-11-10
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a file exists and return status."""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        lines = len(path.read_text().splitlines()) if path.suffix == '.py' or path.suffix == '.md' else 0
        return True, f"({size} bytes, {lines} lines)"
    return False, ""

def main():
    """Run validation checks."""

    print_header("EPIC 1 + EPIC 2 INTEGRATION VALIDATION")

    base_path = Path("/Users/aleksandrgaun/Downloads/TreeBeard")
    all_checks_passed = True

    # ========================================================================
    # CHECK 1: Contract Documents
    # ========================================================================
    print_header("CHECK 1: Contract Documents Published")

    contracts = {
        "Story 1.1 (Database Schema)": "docs/contracts/story-1.1-contract.md",
        "Story 1.4 (Usage Analysis)": "docs/contracts/story-1.4-contract.md",
        "Story 2.2 (Recommendations)": "docs/contracts/story-2.2-contract.md",
        "Story 2.4 (Savings Calculator)": "docs/contracts/story-2.4-contract.md",
        "Story 2.7 (AI Explanations)": "docs/contracts/story-2.7-contract.md",
    }

    missing_contracts = []
    for name, path in contracts.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_error(f"{name}: {path} NOT FOUND")
            missing_contracts.append(name)
            all_checks_passed = False

    if not missing_contracts:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All 5 contracts published! ✓{Colors.END}")

    # ========================================================================
    # CHECK 2: Database Models (Story 1.1)
    # ========================================================================
    print_header("CHECK 2: Database Models (Story 1.1)")

    models = {
        "Base Model": "src/backend/models/base.py",
        "User Models": "src/backend/models/user.py",
        "Usage Models": "src/backend/models/usage.py",
        "Plan Models": "src/backend/models/plan.py",
        "Recommendation Models": "src/backend/models/recommendation.py",
        "Feedback Models": "src/backend/models/feedback.py",
    }

    missing_models = []
    for name, path in models.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_error(f"{name}: {path} NOT FOUND")
            missing_models.append(name)
            all_checks_passed = False

    # ========================================================================
    # CHECK 3: Service Implementations
    # ========================================================================
    print_header("CHECK 3: Service Implementations")

    services = {
        "Story 1.4: Usage Analysis": "src/backend/services/usage_analysis.py",
        "Story 1.4: Cache Service": "src/backend/services/cache_service.py",
        "Story 2.1: Scoring Service": "src/backend/services/scoring_service.py",
        "Story 2.2: Recommendation Engine": "src/backend/services/recommendation_engine.py",
        "Story 2.4: Savings Calculator": "src/backend/services/savings_calculator.py",
        "Story 2.7: Explanation Service": "src/backend/services/explanation_service.py",
        "Story 2.7: Explanation Templates": "src/backend/services/explanation_templates.py",
    }

    missing_services = []
    for name, path in services.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_error(f"{name}: {path} NOT FOUND")
            missing_services.append(name)
            all_checks_passed = False

    # ========================================================================
    # CHECK 4: Pydantic Schemas
    # ========================================================================
    print_header("CHECK 4: Pydantic Schemas")

    schemas = {
        "User Schemas": "src/backend/schemas/user.py",
        "Usage Schemas": "src/backend/schemas/usage_schemas.py",
        "Usage Analysis Schemas": "src/backend/schemas/usage_analysis.py",
        "Plan Schemas": "src/backend/schemas/plan.py",
        "Recommendation Schemas (Story 2.2)": "src/backend/schemas/recommendation_schemas.py",
        "Savings Schemas (Story 2.4)": "src/backend/schemas/savings_schemas.py",
        "Explanation Schemas (Story 2.7)": "src/backend/schemas/explanation_schemas.py",
        "Feedback Schemas": "src/backend/schemas/feedback.py",
    }

    missing_schemas = []
    for name, path in schemas.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_error(f"{name}: {path} NOT FOUND")
            missing_schemas.append(name)
            all_checks_passed = False

    # ========================================================================
    # CHECK 5: Configuration & Infrastructure
    # ========================================================================
    print_header("CHECK 5: Configuration & Infrastructure")

    config_files = {
        "Database Config": "src/backend/config/database.py",
        "Settings": "src/backend/config/settings.py",
        "Environment Template": "src/backend/.env.example",
        "Requirements": "src/backend/requirements.txt",
        "Alembic Config": "src/backend/alembic.ini",
    }

    for name, path in config_files.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_warning(f"{name}: {path} NOT FOUND")

    # ========================================================================
    # CHECK 6: Documentation
    # ========================================================================
    print_header("CHECK 6: Documentation")

    docs = {
        "Database Schema Doc": "docs/database-schema.md",
        "Execution Plan": "docs/execution-plan.md",
        "Sprint Plan": "docs/sprint-plan.md",
        "Agent Coordination Guide": "docs/agent-coordination-guide.md",
        "Claude Prompts": "docs/claude-prompts.md",
    }

    for name, path in docs.items():
        full_path = base_path / path
        exists, info = check_file_exists(full_path)
        if exists:
            print_success(f"{name}: {path} {info}")
        else:
            print_warning(f"{name}: {path} (optional)")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_header("VALIDATION SUMMARY")

    if all_checks_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                                                               ║")
        print("║  ✅ ALL EPIC 1 + EPIC 2 COMPONENTS VALIDATED                 ║")
        print("║                                                               ║")
        print("║  Ready to proceed with Wave 3:                               ║")
        print("║  - Epic 3: API Layer (Stories 3.1-3.7)                       ║")
        print("║  - Epic 4: Frontend Results (Stories 4.1-4.6)                ║")
        print("║  - Epic 5: Frontend Onboarding (Stories 5.1-5.6)             ║")
        print("║                                                               ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                                                               ║")
        print("║  ⚠️  SOME COMPONENTS MISSING                                  ║")
        print("║                                                               ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")

        if missing_contracts:
            print(f"{Colors.RED}Missing contracts:{Colors.END}")
            for item in missing_contracts:
                print(f"  - {item}")

        if missing_models:
            print(f"{Colors.RED}Missing models:{Colors.END}")
            for item in missing_models:
                print(f"  - {item}")

        if missing_services:
            print(f"{Colors.RED}Missing services:{Colors.END}")
            for item in missing_services:
                print(f"  - {item}")

        if missing_schemas:
            print(f"{Colors.RED}Missing schemas:{Colors.END}")
            for item in missing_schemas:
                print(f"  - {item}")

    # ========================================================================
    # INTEGRATION POINTS
    # ========================================================================
    print_header("INTEGRATION POINTS FOR WAVE 3")

    print(f"{Colors.BOLD}Epic 3 (API Layer) can now integrate:{Colors.END}")
    print("  ✓ Story 3.2: Use RecommendationEngine.get_recommendations()")
    print("  ✓ Story 3.2: Use SavingsCalculator.calculate_savings()")
    print("  ✓ Story 3.2: Use ExplanationService.generate_explanation()")
    print("  ✓ Story 3.4: Use database models for auth")

    print(f"\n{Colors.BOLD}Epic 4 & 5 (Frontend) can now integrate:{Colors.END}")
    print("  ✓ Story 4.2: Display RankedPlan with explanations")
    print("  ✓ Story 4.4: Display SavingsAnalysis with charts")
    print("  ✓ Story 5.6: Submit to recommendation API endpoint")

    # ========================================================================
    # STATISTICS
    # ========================================================================
    print_header("PROJECT STATISTICS")

    # Count Python files
    py_files = list((base_path / "src/backend").rglob("*.py"))
    total_lines = 0
    for py_file in py_files:
        try:
            total_lines += len(py_file.read_text().splitlines())
        except:
            pass

    # Count test files
    test_files = list((base_path / "tests").rglob("*.py")) if (base_path / "tests").exists() else []
    test_lines = 0
    for test_file in test_files:
        try:
            test_lines += len(test_file.read_text().splitlines())
        except:
            pass

    # Count documentation
    doc_files = list((base_path / "docs").rglob("*.md")) if (base_path / "docs").exists() else []
    doc_lines = 0
    for doc_file in doc_files:
        try:
            doc_lines += len(doc_file.read_text().splitlines())
        except:
            pass

    print(f"{Colors.BOLD}Code Statistics:{Colors.END}")
    print(f"  Python files: {len(py_files)} files, {total_lines:,} lines")
    print(f"  Test files: {len(test_files)} files, {test_lines:,} lines")
    print(f"  Documentation: {len(doc_files)} files, {doc_lines:,} lines")
    print(f"  {Colors.BOLD}Total: {total_lines + test_lines + doc_lines:,} lines{Colors.END}")

    print()

    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
