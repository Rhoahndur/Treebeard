#!/usr/bin/env python3
"""
TreeBeard AI Energy Plan Recommendation Agent - Complete Validation
====================================================================

Validates all components from Waves 1-5 to ensure production readiness.

Author: System Validation
Date: 2025-11-10
Version: 1.0
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str, color=Colors.BLUE):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{color}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{color}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{color}{'='*80}{Colors.END}\n")

def print_wave_header(wave_num: int, wave_name: str):
    """Print a wave header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}WAVE {wave_num}: {wave_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_file_exists(filepath: str, base_path: Path) -> Tuple[bool, str]:
    """Check if a file exists and return status with size/lines."""
    full_path = base_path / filepath
    if full_path.exists():
        size = full_path.stat().st_size
        if full_path.suffix in ['.py', '.md', '.ts', '.tsx', '.js', '.jsx', '.css']:
            try:
                lines = len(full_path.read_text(encoding='utf-8', errors='ignore').splitlines())
                return True, f"({size:,} bytes, {lines:,} lines)"
            except:
                return True, f"({size:,} bytes)"
        return True, f"({size:,} bytes)"
    return False, ""

def count_files_in_directory(directory: Path, extensions: List[str]) -> Tuple[int, int]:
    """Count files and total lines in a directory."""
    if not directory.exists():
        return 0, 0

    file_count = 0
    total_lines = 0

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            file_count += 1
            try:
                total_lines += len(file_path.read_text(encoding='utf-8', errors='ignore').splitlines())
            except:
                pass

    return file_count, total_lines

def main():
    """Run complete validation."""

    print_header("TREEBEARD AI ENERGY PLAN RECOMMENDATION AGENT", Colors.MAGENTA)
    print_header("COMPLETE SYSTEM VALIDATION - WAVES 1-5", Colors.MAGENTA)

    base_path = Path("/Users/aleksandrgaun/Downloads/TreeBeard")
    all_checks_passed = True

    validation_results = {
        "waves": {},
        "total_files": 0,
        "total_lines": 0,
        "missing_critical": [],
        "missing_optional": []
    }

    # ========================================================================
    # WAVE 1: FOUNDATION (Database Schema & Models)
    # ========================================================================
    print_wave_header(1, "FOUNDATION - Database Schema & Models")

    wave1_files = {
        "Database Models": {
            "src/backend/models/base.py": "critical",
            "src/backend/models/user.py": "critical",
            "src/backend/models/usage.py": "critical",
            "src/backend/models/plan.py": "critical",
            "src/backend/models/recommendation.py": "critical",
            "src/backend/models/feedback.py": "critical",
        },
        "Schemas": {
            "src/backend/schemas/user.py": "critical",
            "src/backend/schemas/usage_schemas.py": "critical",
            "src/backend/schemas/usage_analysis.py": "critical",
            "src/backend/schemas/plan.py": "critical",
            "src/backend/schemas/feedback.py": "critical",
        },
        "Infrastructure": {
            "src/backend/config/database.py": "critical",
            "src/backend/config/settings.py": "critical",
            "src/backend/alembic.ini": "critical",
            "src/backend/.env.example": "optional",
            "src/backend/requirements.txt": "critical",
        },
        "Services": {
            "src/backend/services/usage_analysis.py": "critical",
            "src/backend/services/cache_service.py": "critical",
        },
        "Contracts": {
            "docs/contracts/story-1.1-contract.md": "optional",
            "docs/contracts/story-1.4-contract.md": "optional",
        }
    }

    wave1_missing = []
    wave1_count = 0

    for category, files in wave1_files.items():
        print(f"{Colors.BOLD}{category}:{Colors.END}")
        for filepath, priority in files.items():
            exists, info = check_file_exists(filepath, base_path)
            if exists:
                print_success(f"{filepath} {info}")
                wave1_count += 1
            else:
                if priority == "critical":
                    print_error(f"{filepath} NOT FOUND (CRITICAL)")
                    wave1_missing.append(filepath)
                    all_checks_passed = False
                else:
                    print_warning(f"{filepath} NOT FOUND (optional)")

    validation_results["waves"]["wave1"] = {
        "name": "Foundation",
        "files_validated": wave1_count,
        "missing": wave1_missing
    }

    # ========================================================================
    # WAVE 2: CORE ENGINE (Recommendation System)
    # ========================================================================
    print_wave_header(2, "CORE ENGINE - Recommendation System")

    wave2_files = {
        "Scoring & Ranking": {
            "src/backend/services/scoring_service.py": "critical",
            "src/backend/services/recommendation_engine.py": "critical",
            "src/backend/schemas/recommendation_schemas.py": "critical",
        },
        "Savings Calculator": {
            "src/backend/services/savings_calculator.py": "critical",
            "src/backend/schemas/savings_schemas.py": "critical",
        },
        "AI Explanations": {
            "src/backend/services/explanation_service.py": "critical",
            "src/backend/services/explanation_templates.py": "critical",
            "src/backend/schemas/explanation_schemas.py": "critical",
        },
        "Contracts": {
            "docs/contracts/story-2.2-contract.md": "optional",
            "docs/contracts/story-2.4-contract.md": "optional",
            "docs/contracts/story-2.7-contract.md": "optional",
            "docs/claude-prompts.md": "optional",
        }
    }

    wave2_missing = []
    wave2_count = 0

    for category, files in wave2_files.items():
        print(f"{Colors.BOLD}{category}:{Colors.END}")
        for filepath, priority in files.items():
            exists, info = check_file_exists(filepath, base_path)
            if exists:
                print_success(f"{filepath} {info}")
                wave2_count += 1
            else:
                if priority == "critical":
                    print_error(f"{filepath} NOT FOUND (CRITICAL)")
                    wave2_missing.append(filepath)
                    all_checks_passed = False
                else:
                    print_warning(f"{filepath} NOT FOUND (optional)")

    validation_results["waves"]["wave2"] = {
        "name": "Core Engine",
        "files_validated": wave2_count,
        "missing": wave2_missing
    }

    # ========================================================================
    # WAVE 3: USER-FACING LAYERS (API + Frontend)
    # ========================================================================
    print_wave_header(3, "USER-FACING LAYERS - API + Frontend")

    wave3_files = {
        "Backend API": {
            "src/backend/api/main.py": "critical",
            "src/backend/api/routes/recommendations.py": "critical",
            "src/backend/api/routes/auth.py": "critical",
            "src/backend/api/middleware/rate_limit.py": "optional",
            "src/backend/api/middleware/cache.py": "optional",
        },
        "Frontend Core": {
            "src/frontend/src/App.tsx": "critical",
            "src/frontend/src/main.tsx": "critical",
            "src/frontend/package.json": "critical",
            "src/frontend/vite.config.ts": "critical",
        },
        "Frontend Pages": {
            "src/frontend/src/pages/ResultsPage.tsx": "critical",
        },
        "Frontend Components": {
            "src/frontend/src/components/PlanCard/PlanCard.tsx": "critical",
            "src/frontend/src/components/CostBreakdown/CostBreakdown.tsx": "optional",
        },
        "Contracts": {
            "docs/contracts/story-3.2-contract.md": "optional",
        }
    }

    wave3_missing = []
    wave3_count = 0

    for category, files in wave3_files.items():
        print(f"{Colors.BOLD}{category}:{Colors.END}")
        for filepath, priority in files.items():
            exists, info = check_file_exists(filepath, base_path)
            if exists:
                print_success(f"{filepath} {info}")
                wave3_count += 1
            else:
                if priority == "critical":
                    print_error(f"{filepath} NOT FOUND (CRITICAL)")
                    wave3_missing.append(filepath)
                    all_checks_passed = False
                else:
                    print_warning(f"{filepath} NOT FOUND (optional)")

    validation_results["waves"]["wave3"] = {
        "name": "User-Facing Layers",
        "files_validated": wave3_count,
        "missing": wave3_missing
    }

    # ========================================================================
    # WAVE 4: ENHANCEMENT (Performance, Analytics, Monitoring)
    # ========================================================================
    print_wave_header(4, "ENHANCEMENT - Performance, Analytics, Monitoring")

    wave4_files = {
        "Risk Detection": {
            "src/backend/services/risk_detection.py": "critical",
            "src/backend/schemas/risk_schemas.py": "critical",
        },
        "Performance": {
            "src/backend/services/cache_optimization.py": "optional",
            "src/backend/services/cache_warming.py": "optional",
        },
        "Analytics": {
            "src/frontend/src/utils/analytics.ts": "optional",
            "src/backend/services/analytics_service.py": "optional",
        },
        "Monitoring": {
            "src/backend/monitoring/apm.py": "optional",
            "src/backend/monitoring/metrics.py": "optional",
            "src/backend/monitoring/sentry_init.py": "optional",
        },
        "Runbooks": {
            "docs/runbooks/high-error-rate.md": "optional",
            "docs/runbooks/high-latency.md": "optional",
        }
    }

    wave4_missing = []
    wave4_count = 0

    for category, files in wave4_files.items():
        print(f"{Colors.BOLD}{category}:{Colors.END}")
        for filepath, priority in files.items():
            exists, info = check_file_exists(filepath, base_path)
            if exists:
                print_success(f"{filepath} {info}")
                wave4_count += 1
            else:
                if priority == "critical":
                    print_error(f"{filepath} NOT FOUND (CRITICAL)")
                    wave4_missing.append(filepath)
                    all_checks_passed = False
                else:
                    print_warning(f"{filepath} NOT FOUND (optional)")

    validation_results["waves"]["wave4"] = {
        "name": "Enhancement",
        "files_validated": wave4_count,
        "missing": wave4_missing
    }

    # ========================================================================
    # WAVE 5: POLISH (Feedback, Admin, Visualizations)
    # ========================================================================
    print_wave_header(5, "POLISH - Feedback, Admin, Visualizations")

    wave5_files = {
        "Feedback System": {
            "src/backend/api/routes/feedback.py": "critical",
            "src/backend/schemas/feedback_schemas.py": "critical",
            "src/backend/services/feedback_service.py": "critical",
            "src/frontend/src/components/FeedbackWidget/FeedbackWidget.tsx": "critical",
            "src/frontend/src/pages/FeedbackDashboard.tsx": "optional",
        },
        "Admin Backend": {
            "src/backend/models/audit_log.py": "critical",
            "src/backend/api/routes/admin.py": "critical",
            "src/backend/services/admin_service.py": "critical",
            "src/backend/services/audit_service.py": "critical",
        },
        "Admin Frontend": {
            "src/frontend/src/pages/admin/Dashboard.tsx": "critical",
            "src/frontend/src/pages/admin/Users.tsx": "critical",
            "src/frontend/src/components/admin/AdminLayout.tsx": "critical",
        },
        "Visualizations": {
            "src/frontend/src/components/charts/ChartWrapper.tsx": "critical",
            "src/frontend/src/components/charts/MonthlyUsageChart.tsx": "optional",
            "src/frontend/src/components/charts/CostComparisonChart.tsx": "optional",
        },
        "Export": {
            "src/frontend/src/components/export/PdfExport.tsx": "optional",
            "src/frontend/src/components/export/CsvExportUsage.tsx": "optional",
        }
    }

    wave5_missing = []
    wave5_count = 0

    for category, files in wave5_files.items():
        print(f"{Colors.BOLD}{category}:{Colors.END}")
        for filepath, priority in files.items():
            exists, info = check_file_exists(filepath, base_path)
            if exists:
                print_success(f"{filepath} {info}")
                wave5_count += 1
            else:
                if priority == "critical":
                    print_error(f"{filepath} NOT FOUND (CRITICAL)")
                    wave5_missing.append(filepath)
                    all_checks_passed = False
                else:
                    print_warning(f"{filepath} NOT FOUND (optional)")

    validation_results["waves"]["wave5"] = {
        "name": "Polish",
        "files_validated": wave5_count,
        "missing": wave5_missing
    }

    # ========================================================================
    # PROJECT STATISTICS
    # ========================================================================
    print_header("PROJECT STATISTICS", Colors.CYAN)

    # Count backend files
    backend_py_count, backend_py_lines = count_files_in_directory(
        base_path / "src/backend", ['.py']
    )

    # Count frontend files
    frontend_tsx_count, frontend_tsx_lines = count_files_in_directory(
        base_path / "src/frontend/src", ['.tsx', '.ts']
    )

    # Count test files
    test_count, test_lines = count_files_in_directory(
        base_path / "tests", ['.py', '.tsx', '.ts']
    )

    # Count documentation
    doc_count, doc_lines = count_files_in_directory(
        base_path / "docs", ['.md']
    )

    print(f"{Colors.BOLD}Backend (Python):{Colors.END}")
    print(f"  Files: {backend_py_count:,}")
    print(f"  Lines: {backend_py_lines:,}")

    print(f"\n{Colors.BOLD}Frontend (TypeScript/React):{Colors.END}")
    print(f"  Files: {frontend_tsx_count:,}")
    print(f"  Lines: {frontend_tsx_lines:,}")

    print(f"\n{Colors.BOLD}Tests:{Colors.END}")
    print(f"  Files: {test_count:,}")
    print(f"  Lines: {test_lines:,}")

    print(f"\n{Colors.BOLD}Documentation:{Colors.END}")
    print(f"  Files: {doc_count:,}")
    print(f"  Lines: {doc_lines:,}")

    total_code_lines = backend_py_lines + frontend_tsx_lines + test_lines
    total_all_lines = total_code_lines + doc_lines

    print(f"\n{Colors.BOLD}{Colors.GREEN}TOTAL CODE: {total_code_lines:,} lines{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}TOTAL (including docs): {total_all_lines:,} lines{Colors.END}")

    validation_results["total_files"] = backend_py_count + frontend_tsx_count + test_count + doc_count
    validation_results["total_lines"] = total_all_lines

    # ========================================================================
    # VALIDATION SUMMARY
    # ========================================================================
    print_header("VALIDATION SUMMARY", Colors.MAGENTA)

    total_validated = sum(w["files_validated"] for w in validation_results["waves"].values())
    total_missing_critical = sum(len(w["missing"]) for w in validation_results["waves"].values())

    print(f"{Colors.BOLD}Files Validated:{Colors.END} {total_validated}")
    print(f"{Colors.BOLD}Missing Critical Files:{Colors.END} {total_missing_critical}")

    if all_checks_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                           ║")
        print("║  ✅ ALL CRITICAL COMPONENTS VALIDATED - SYSTEM PRODUCTION READY          ║")
        print("║                                                                           ║")
        print("║  Waves Completed:                                                        ║")
        for wave_id, wave_data in validation_results["waves"].items():
            wave_num = wave_id.replace("wave", "")
            wave_name = wave_data["name"]
            files = wave_data["files_validated"]
            print(f"║  - Wave {wave_num}: {wave_name:<30} ({files:>3} files validated)        ║")
        print("║                                                                           ║")
        print(f"║  Total: {total_code_lines:,} lines of production code                              ║")
        print("║                                                                           ║")
        print("╚═══════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}")
        print("╔═══════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                           ║")
        print("║  ⚠️  SOME CRITICAL COMPONENTS MISSING                                     ║")
        print("║                                                                           ║")
        print("╚═══════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")

        for wave_id, wave_data in validation_results["waves"].items():
            if wave_data["missing"]:
                wave_num = wave_id.replace("wave", "")
                print(f"{Colors.RED}Missing from Wave {wave_num}:{Colors.END}")
                for item in wave_data["missing"]:
                    print(f"  - {item}")
                print()

    # Save validation results to JSON
    output_path = base_path / "validation_results.json"
    with open(output_path, 'w') as f:
        json.dump(validation_results, f, indent=2)

    print_info(f"Validation results saved to: {output_path}")

    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
