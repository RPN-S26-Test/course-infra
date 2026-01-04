import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, final


@dataclass(frozen=True)
class Constraints:
    max_file_count: int = 5
    max_line_count: int = 500
    target_ext: str = ".py"


class ValidationResult(Protocol):
    def is_valid(self) -> bool: ...
    def report(self) -> str: ...


@final
@dataclass(frozen=True)
class Violation:
    msg: str

    def is_valid(self) -> bool:
        return False

    def report(self) -> str:
        return f"VIOLATION: {self.msg}"


@final
@dataclass(frozen=True)
class Success:
    def is_valid(self) -> bool:
        return True

    def report(self) -> str:
        return "SUCCESS: Structural invariants satisfied."


class RepositoryValidator:
    def __init__(self, root: Path, constraints: Constraints) -> None:
        self._root = root
        self._constraints = constraints

    def validate(self) -> ValidationResult:
        files = [
            p
            for p in self._root.rglob(f"*{self._constraints.target_ext}")
            if not any(part.startswith(".") for part in p.parts)
        ]

        if len(files) > self._constraints.max_file_count:
            return Violation(
                f"File count {len(files)} > Limit {self._constraints.max_file_count}"
            )

        for f in files:
            try:
                if (
                    count := sum(1 for _ in f.open(encoding="utf-8"))
                ) > self._constraints.max_line_count:
                    return Violation(
                        f"File '{f.name}' lines {count} > Limit {self._constraints.max_line_count}"
                    )
            except UnicodeDecodeError:
                pass
        return Success()


def main() -> None:
    target = Path("submission") if Path("submission").exists() else Path.cwd()
    result = RepositoryValidator(target, Constraints()).validate()

    if not result.is_valid():
        sys.stderr.write(result.report() + "\n")
        sys.exit(1)
    sys.stdout.write(result.report() + "\n")


if __name__ == "__main__":
    main()
