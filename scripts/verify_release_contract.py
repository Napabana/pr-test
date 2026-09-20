from label_utils import normalize_label


CASES = {
    "Agent\tRuntime": "agent-runtime",
    "Agent\nRuntime": "agent-runtime",
    "  Agent   Runtime  ": "agent-runtime",
}


def main() -> int:
    failures = []
    for raw, expected in CASES.items():
        actual = normalize_label(raw)
        if actual != expected:
            failures.append((raw, expected, actual))

    if failures:
        for raw, expected, actual in failures:
            print(f"FAIL {raw!r}: expected {expected!r}, got {actual!r}")
        return 1

    print("release contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
