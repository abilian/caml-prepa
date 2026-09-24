"""Every stage of the compiler, in one call.

`analyse(source)` parses, prints, resolves names, infers types, compiles,
and then runs the programme twice: once by walking the tree and once
through the emitted Python. It returns what each stage produced, and any
errors, so nothing has to be run twice to see two answers.

Both front doors use it. `python -m ocaml` prints one of the views, and the
browser playground shows all five. Neither repeats the sequence.

Running it twice is deliberate: two back ends over one runtime agreeing is
worth saying, and the playground says it on every run.

Every stage catches broadly and on purpose. What a compiler produces when
you make a mistake *is* the message, and a stage that let an exception
through would blank a view instead of printing it.
"""

from __future__ import annotations

import contextlib
import io
from collections.abc import Iterator
from typing import Any

from .back import compile as backend, interpret, stepper
from .front import emit
from .front.parser import parse
from .middle import analyze, grammar, infer

#: The views, and what each is, in the order the stages produce them.
#: `python -m ocaml` turns the keys into flags and the values into help.
VIEWS = {
    "run": "what the programme prints (the default)",
    "types": "the signature the checker infers",
    "names": "the scope tree astero derives, one per namespace",
    "python": "the Python the second back end emits",
    "printed": "the source, printed back out of the tree",
}


@contextlib.contextmanager
def stage(found: dict[str, Any], name: str) -> Iterator[None]:
    """Run one stage, and record what it raised instead of raising it."""
    try:
        yield
    except Exception as bad:
        found["errors"].append(f"{name}: {type(bad).__name__}: {bad}")


def scopes(tree: Any) -> str:
    """The scope tree astero derives, one per namespace the grammar declares."""
    return "\n\n".join(
        f"── {ns} ──\n{analyze.blocks(tree, ns)}" for ns in grammar.NAMESPACES
    )


def analyse(source: str) -> dict[str, Any]:
    """Every stage's output, for one programme."""
    found: dict[str, Any] = {
        "printed": "",
        "names": "",
        "types": "",
        "python": "",
        "run": "",
        "compiled": "",
        "agree": False,
        "ran": False,
        "errors": [],
    }
    try:
        tree = parse(source)
    except Exception as bad:
        found["errors"].append(f"syntax: {bad}")
        return found

    with stage(found, "printer"):
        found["printed"] = emit.unparse(tree)

    with stage(found, "names"):
        unbound = analyze.unbound(tree)
        report = "\n".join(unbound) + "\n\n" if unbound else ""
        found["names"] = report + scopes(tree)

    with stage(found, "types"):
        found["types"] = "\n".join(infer.signature(tree))

    with stage(found, "compiler"):
        found["python"] = backend.compile_structure(tree)

    with stage(found, "interpreter"):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            interpret.run(tree)
        found["run"] = buffer.getvalue()
        found["ran"] = True

    if found["python"]:
        with stage(found, "compiled"):
            buffer = io.StringIO()
            scope: dict[str, Any] = {"__name__": "__main__"}
            with contextlib.redirect_stdout(buffer):
                exec(compile(found["python"], "<playground>", "exec"), scope)
            found["compiled"] = buffer.getvalue()
            found["agree"] = found["compiled"] == found["run"]

    return found


def stepping(source: str, limit: int = stepper.LIMIT) -> dict[str, Any]:
    """Everything the Step view needs, as plain data the page can read.

    Kept apart from `analyse` because recording costs more than running, and
    nobody should pay for it until they ask to step. Plain lists and dicts
    rather than the dataclasses, because what crosses into JavaScript has to
    convert, and `Step` would not.
    """
    found: dict[str, Any] = {
        "steps": [],
        "output": "",
        "truncated": False,
        "error": None,
        "python": "",
        "pysteps": [],
        "errors": [],
    }
    with stage(found, "step"):
        trace = stepper.record(source, limit)
        found["output"] = trace.output
        found["truncated"] = trace.truncated
        found["error"] = trace.error
        found["steps"] = [
            {
                "kind": step.kind,
                "span": list(step.span) if step.span else None,
                "depth": step.depth,
                "call": step.call,
                "stack": list(step.stack),
                "env": [list(pair) for pair in step.env],
                "store": [list(pair) for pair in step.store],
                "scope": step.scope,
                "value": step.value,
                "printed": step.printed,
            }
            for step in trace.steps
        ]
    with stage(found, "step python"):
        steps, output = stepper.record_compiled(source, limit)
        found["python"] = backend.compile_source(source)
        found["pysteps"] = [
            {
                "line": step.line,
                "text": step.text,
                "names": [list(pair) for pair in step.names],
                "printed": step.printed,
            }
            for step in steps
        ]
        found["pyoutput"] = output
    return found
