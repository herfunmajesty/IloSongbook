from pathlib import Path
import filecmp
import difflib
import re
import sys


BASELINE = Path("out_baseline")
CURRENT = Path("out")


def get_files(folder):
    return {
        path.relative_to(folder)
        for path in folder.rglob("*")
        if path.is_file()
    }

def normalize_index_html(text):
    return re.sub(
        r"(Updated on:\s*)\d{4}-\d{2}-\d{2}",
        r"\1DATE",
        text,
    )

def files_are_equal(relative_path, baseline_path, current_path):
    if relative_path == Path( "index.html"):
        baseline = normalize_index_html(baseline_path.read_text(encoding="utf-8")
        )
        current = normalize_index_html(current_path.read_text(encoding="utf-8")
        )
        return baseline == current

    return filecmp.cmp(baseline_path, current_path, shallow=False)

def compare_text_files(relative_path, baseline_path, current_path):
    baseline = baseline_path.read_text(encoding="utf-8")
    current = current_path.read_text(encoding="utf-8")

    if relative_path== Path ("index.html"):
        baseline = normalize_index_html(baseline) 
        current = normalize_index_html(current)
        if baseline == current:
            return None

    diff = difflib.unified_diff(
        baseline.splitlines(keepends=True),
        current.splitlines(keepends=True),
        fromfile=str(baseline_path),
        tofile=str(current_path),
    )

    return "".join(diff)


def main():
    if not BASELINE.exists():
        print(f"ERROR: Baseline folder does not exist: {BASELINE}")
        sys.exit(1)

    if not CURRENT.exists():
        print(f"ERROR: Current output folder does not exist: {CURRENT}")
        sys.exit(1)

    baseline_files = get_files(BASELINE)
    current_files = get_files(CURRENT)

    missing = sorted(baseline_files - current_files)
    added = sorted(current_files - baseline_files)
    common = sorted(baseline_files & current_files)

    changed = []

    print()
    print("=== IloSongbook output comparison ===")
    print()

    print(f"Baseline: {BASELINE}")
    print(f"Current:  {CURRENT}")
    print()

    print(f"Baseline files : {len(baseline_files)}")
    print(f"Current files  : {len(current_files)}")
    print()

    total = len(common)

    for number, relative_path in enumerate(common, start=1):
        baseline_path = BASELINE / relative_path
        current_path = CURRENT / relative_path

        print(
            f"\rChecking {number}/{total}: {relative_path}",
            end="",
            flush=True,
        )

        if not files_are_equal(relative_path, baseline_path, current_path):
            changed.append(relative_path)

    print()



    if not missing and not added and not changed:
        print("RESULT: PASS")
        print("All files are identical.")
        return

    if missing:
        print("MISSING FILES:")
        for path in missing:
            print(f"  - {path}")
        print()

    if added:
        print("ADDED FILES:")
        for path in added:
            print(f"  + {path}")
        print()

    if changed:
        print("CHANGED FILES:")
        for path in changed:
            print(f"  * {path}")
        print()

        for path in changed:
            baseline_path = BASELINE / path
            current_path = CURRENT / path

            try:
                diff = compare_text_files(path, baseline_path, current_path)

                if diff:
                    print("=" * 70)
                    print(diff)

            except UnicodeDecodeError:
                print(f"  (binary file — content diff not available)")
                print()

    print("RESULT: DIFFERENCES FOUND")
    sys.exit(1)


if __name__ == "__main__":
    main()