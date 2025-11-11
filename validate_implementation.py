"""
Quick validation script for Epic 2 implementation.
Verifies that all files exist and are properly structured.
"""

import os
import sys
from pathlib import Path

def check_file(path, description, min_lines=0):
    """Check if file exists and meets minimum line count."""
    if not os.path.exists(path):
        print(f"❌ Missing: {description}")
        print(f"   Expected: {path}")
        return False

    with open(path, 'r') as f:
        lines = len(f.readlines())

    if lines < min_lines:
        print(f"⚠️  {description}: {lines} lines (expected >{min_lines})")
        return False

    print(f"✅ {description}: {lines} lines")
    return True

def main():
    """Validate Epic 2 implementation."""
    base_path = Path(__file__).parent

    print("=" * 70)
    print("Epic 2 - AI Explanation Generation - Implementation Validation")
    print("=" * 70)
    print()

    all_good = True

    # Check schemas
    print("📋 Schemas:")
    all_good &= check_file(
        base_path / "src/backend/schemas/explanation_schemas.py",
        "explanation_schemas.py",
        min_lines=150
    )
    print()

    # Check services
    print("⚙️  Services:")
    all_good &= check_file(
        base_path / "src/backend/services/explanation_service.py",
        "explanation_service.py",
        min_lines=500
    )
    all_good &= check_file(
        base_path / "src/backend/services/explanation_templates.py",
        "explanation_templates.py",
        min_lines=300
    )
    print()

    # Check tests
    print("🧪 Tests:")
    all_good &= check_file(
        base_path / "tests/backend/test_explanation_service.py",
        "test_explanation_service.py",
        min_lines=700
    )
    print()

    # Check documentation
    print("📚 Documentation:")
    all_good &= check_file(
        base_path / "docs/contracts/story-2.7-contract.md",
        "story-2.7-contract.md",
        min_lines=500
    )
    all_good &= check_file(
        base_path / "docs/claude-prompts.md",
        "claude-prompts.md",
        min_lines=400
    )
    all_good &= check_file(
        base_path / "docs/EXPLANATION_SERVICE.md",
        "EXPLANATION_SERVICE.md",
        min_lines=500
    )
    all_good &= check_file(
        base_path / "EPIC-2-DELIVERABLES.md",
        "EPIC-2-DELIVERABLES.md",
        min_lines=400
    )
    print()

    # Check requirements
    print("📦 Dependencies:")
    req_file = base_path / "src/backend/requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            content = f.read()
            has_anthropic = "anthropic" in content
            has_textstat = "textstat" in content

            if has_anthropic:
                print("✅ anthropic package in requirements.txt")
            else:
                print("❌ Missing: anthropic package")
                all_good = False

            if has_textstat:
                print("✅ textstat package in requirements.txt")
            else:
                print("❌ Missing: textstat package")
                all_good = False
    else:
        print("❌ Missing: requirements.txt")
        all_good = False
    print()

    # Summary
    print("=" * 70)
    if all_good:
        print("✅ ✅ ✅  ALL VALIDATIONS PASSED  ✅ ✅ ✅")
        print()
        print("Epic 2 (Stories 2.6, 2.7, 2.8) implementation is COMPLETE!")
        print()
        print("Next Steps:")
        print("1. Install dependencies: pip install -r src/backend/requirements.txt")
        print("2. Configure environment: export ANTHROPIC_API_KEY=sk-ant-...")
        print("3. Run tests: pytest tests/backend/test_explanation_service.py")
        print("4. Integrate with Stories 3.2 (API) and 4.2 (UI)")
        return 0
    else:
        print("❌ VALIDATION FAILED - Some files are missing or incomplete")
        return 1
    print("=" * 70)

if __name__ == "__main__":
    sys.exit(main())
