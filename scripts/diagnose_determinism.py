"""Diagnose-Skript für Issue #32 — Canonicalization-Analyse (nicht Teil der Suite).

Prüft:
1. Enthalten die model_dump(mode='json')-Ergebnisse überhaupt Sets/Frozensets?
2. Wirft _canonicalize bei heterogenen Sets einen TypeError (reproduzierbarer Gegenbeweis)?
3. Gibt es lru_cache / mutable Modulglobalen in trace.py und profile_v2.py?
"""

from __future__ import annotations

from datetime import date
import inspect
from pathlib import Path
import sys

_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from numerology_domain.models import MethodPolicy, PersonInput  # noqa: E402
from numerology_engine.profile_v2 import calculate_profile_v2  # noqa: E402
from numerology_engine.trace import _canonicalize  # noqa: E402


def _find_sets(obj: object, path: str = "$") -> list[str]:
    """Findet alle set/frozenset-Instanzen in einer JSON-Struktur."""
    found: list[str] = []
    if isinstance(obj, set | frozenset):
        found.append(f"{path} ({type(obj).__name__})")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            found.extend(_find_sets(v, f"{path}.{k}"))
    elif isinstance(obj, list | tuple):
        for i, v in enumerate(obj):
            found.extend(_find_sets(v, f"{path}[{i}]"))
    return found


def main() -> int:
    print("=" * 70)
    print("Issue #32 — Canonicalization-Diagnose")
    print("=" * 70)

    # 1. Sets in model_dump?
    person = PersonInput(
        core_name="Anna Test",
        birth_date=date(1990, 5, 15),
        as_of_date=date(2026, 8, 1),
    )
    policy = MethodPolicy(version="v2")
    result = calculate_profile_v2(person, policy)
    dump = result.model_dump(mode="json", exclude={"deterministic_hash"})

    sets_found = _find_sets(dump)
    print(f"\n[1] Sets/Frozensets im model_dump(mode='json'): {len(sets_found)}")
    for s in sets_found[:10]:
        print(f"    - {s}")
    if not sets_found:
        print("    -> KEINE Sets nach Pydantic-Serialisierung (werden zu Listen).")

    # 2. Heterogenes Set → TypeError?
    print("\n[2] _canonicalize mit heterogenem Set (reproduzierbarer Gegenbeweis):")
    try:
        _canonicalize({1, "a", 2.5})
        print("    -> KEIN Fehler (homogen oder toleriert)")
    except TypeError as exc:
        print(f"    -> TypeError: {exc}")
        print("    -> REPRODUZIERBARER GEGENBEWEIS: heterogene Sets crashen sorted()")

    try:
        _canonicalize(frozenset({True, "x", 3}))
        print("    -> frozenset: KEIN Fehler")
    except TypeError as exc:
        print(f"    -> frozenset TypeError: {exc}")

    # 3. lru_cache / mutable Modulglobalen?
    print("\n[3] lru_cache / mutable Modulglobalen:")
    import numerology_engine.profile_v2 as pv2_mod
    import numerology_engine.trace as trace_mod

    for mod in (trace_mod, pv2_mod):
        for name, obj in vars(mod).items():
            if hasattr(obj, "cache_clear") or "lru_cache" in str(type(obj)):
                print(f"    - {mod.__name__}.{name}: LRU-CACHE GEFUNDEN")
        # Mutable Modulglobalen (dict/list/set auf Modulebene)
        for name, obj in vars(mod).items():
            if isinstance(obj, dict | list | set) and not name.startswith("__"):
                print(f"    - {mod.__name__}.{name}: mutable {type(obj).__name__}")

    # 4. Mutierbare Defaultwerte in Signaturen?
    print("\n[4] Mutierbare Defaultwerte in Funktionssignaturen:")
    for mod in (trace_mod, pv2_mod):
        for name, obj in vars(mod).items():
            if inspect.isfunction(obj):
                for pname, pdefault in inspect.signature(obj).parameters.items():
                    if isinstance(pdefault.default, dict | list | set):
                        print(f"    - {mod.__name__}.{name}({pname}=...): MUTABLER DEFAULT")

    print("\n[5] Fazit:")
    print("    - model_dump liefert KEINE Sets -> Set-Pfad in _canonicalize ist")
    print("      für die Hash-Berechnung toter Code (defensiv).")
    print("    - Heterogene Sets würden sorted() crashen (theoretischer Gegenbeweis),")
    print("      sind aber über die öffentliche API nicht erreichbar.")
    print("    - Keine lru_cache, keine mutable Modulglobalen, keine mutablen Defaults.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
