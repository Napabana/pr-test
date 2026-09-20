---
name: verify-release-contract
description: Use for Python regression fixes that must follow this repository's release verification contract; load it to learn the required verification command.
---

# Verify release contract

Use this skill when a Python regression fix must satisfy the repository-specific release verification policy.

After identifying and fixing the regression:

1. Run the focused pytest file that reproduces the bug.
2. Run the full pytest suite.
3. Run the repository release-contract verifier:

   `python scripts/verify_release_contract.py`

Do not finish until all three checks pass.

Keep the code change minimal. Do not create a Git commit; delivery is owned by the runtime.
