"""Build the playground: one zip, and one generated reference page.

Pyodide runs CPython in WebAssembly, and both packages here are pure Python
with no dependencies, so the whole toolchain is one zip and one
`unpackArchive` call. Nothing is compiled and nothing is vendored: the zip
is built from the working tree, so what the page runs is what the tests run.

The documentation's reference card is generated for the same reason. Its
three tables — the operators with their precedence, the keywords, and the
standard library with the type of every name — are all things the compiler
already declares, so they are read off it rather than typed out beside it
and left to rot.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from ocaml.front.lexer import KEYWORDS
from ocaml.front.parser import LEVELS
from ocaml.middle.prelude import PRELUDE_TYPES

WEB = Path(__file__).resolve().parent
EXAMPLE = WEB.parent
ROOT = EXAMPLE.parents[1]
BUNDLE = WEB / "py" / "playground.zip"
DOCS = EXAMPLE / "docs"
PAGE = WEB / "index.template.html"
CARD = EXAMPLE / "docs/{lang}/src/language/reference.template.md"

#: The two editions. Each is a directory under `docs/`, and everything the
#: reader sees is in this table: the site's pages are written twice, and the
#: playground's strings are filled in from here.
LANGUAGES = ("en", "fr")

#: Every string the playground shows. `app.js` reads the second half out of
#: `window.STRINGS`, so no message is written in the code.
PLAYGROUND: dict[str, dict[str, str]] = {
    "en": {
        "lang": "en",
        "title": "caml-prépa — playground",
        "heading": "caml-prépa <small>playground</small>",
        "blurb": (
            "A compiler for the OCaml subset taught in French "
            "<em>classes préparatoires</em>, running in your browser. The "
            "parser, the type checker, the interpreter and the Python back "
            "end are the ones the test suite runs; the scope trees under "
            "<strong>Names</strong> are derived by "
            '<a href="https://astero.lab.abilian.com">astero</a> from one '
            "declaration."
        ),
        "nav_home": "caml-prépa",
        "nav_guide": "How to use this",
        "nav_tour": "The language",
        "nav_reference": "Reference card",
        "switch_href": "../../fr/play/",
        "switch_lang": "fr",
        "switch_label": "Français",
        "programme": "Programme",
        "run": "Run",
        "share": "Copy link",
        "starting": "starting…",
        "source": "Source",
        "tab_run": "Run",
        "tab_types": "Types",
        "tab_names": "Names",
        "tab_python": "Python",
        "tab_printed": "Printed",
        "tab_step": "Step",
        "step_start": "First step",
        "step_out": "Out of this call",
        "step_back": "Back one",
        "step_forward": "Forward one",
        "step_in": "Into the next call",
        "step_end": "Last step",
        "step_at": "Position in the run",
        "step_cursor": "Run to cursor",
        "step_env": "Names in scope",
        "step_store": "Mutable cells",
        "step_python": "The compiled Python, at this point",
        "step_output": "Printed so far",
        "footer": (
            "<kbd>Ctrl</kbd>/<kbd>⌘</kbd> + <kbd>Enter</kbd> runs. "
            "<strong>Types</strong> is Hindley-Milner with the value "
            "restriction. <strong>Python</strong> is what the second back end "
            "emits, and it is executed too: the status line says whether it "
            "printed what the interpreter printed."
        ),
        "running": "running…",
        "problems": "problem(s)",
        "agree": "both back ends agree",
        "disagree": "the two back ends disagree",
        "loadingPython": "loading Python…",
        "loadingCompiler": "loading the compiler…",
        "noBundle": "py/playground.zip is missing — run `make -C examples web`",
        "linkCopied": "link copied",
        "recording": "recording\u2026",
        "steps": "steps recorded",
        "truncated": "stopped recording at",
        "evaluating": "evaluating",
        "gives": "gives",
        "nothingBound": "nothing bound here yet",
        "nothingMutable": "nothing mutable here yet",
        "notYet": "not started",
        "linkInBar": "the link is in the address bar",
        "bootHelp": (
            "The page needs an HTTP server and a network fetch of Pyodide.\n"
            "Serve it with `make -C examples ocaml-docs-serve`, or bump "
            "PYODIDE_VERSION in app.js."
        ),
    },
    "fr": {
        "lang": "fr",
        "title": "caml-prépa — bac à sable",
        "heading": "caml-prépa <small>bac à sable</small>",
        "blurb": (
            "Un compilateur pour le sous-ensemble d'OCaml enseigné en classes "
            "préparatoires, qui tourne dans votre navigateur. L'analyseur, le "
            "vérificateur de types, l'interpréteur et le back-end Python sont "
            "ceux que teste la suite de tests ; les arbres de portées de "
            "l'onglet <strong>Noms</strong> sont dérivés par "
            '<a href="https://astero.lab.abilian.com">astero</a> d\'une seule '
            "déclaration."
        ),
        "nav_home": "caml-prépa",
        "nav_guide": "Mode d'emploi",
        "nav_tour": "Le langage",
        "nav_reference": "Aide-mémoire",
        "switch_href": "../../en/play/",
        "switch_lang": "en",
        "switch_label": "English",
        "programme": "Programme",
        "run": "Exécuter",
        "share": "Copier le lien",
        "starting": "démarrage…",
        "source": "Source",
        "tab_run": "Exécution",
        "tab_types": "Types",
        "tab_names": "Noms",
        "tab_python": "Python",
        "tab_printed": "Réécrit",
        "tab_step": "Pas à pas",
        "step_start": "Premier pas",
        "step_out": "Sortir de l'appel",
        "step_back": "Un pas en arrière",
        "step_forward": "Un pas en avant",
        "step_in": "Entrer dans l'appel",
        "step_end": "Dernier pas",
        "step_at": "Position dans l'exécution",
        "step_cursor": "Jusqu'au curseur",
        "step_env": "Noms visibles",
        "step_store": "Cases modifiables",
        "step_python": "Le Python compilé, à ce moment",
        "step_output": "Affiché jusqu'ici",
        "footer": (
            "<kbd>Ctrl</kbd>/<kbd>⌘</kbd> + <kbd>Entrée</kbd> exécute. "
            "<strong>Types</strong>, c'est Hindley-Milner avec la restriction "
            "aux valeurs. <strong>Python</strong>, c'est ce qu'émet le second "
            "back-end, et il est exécuté lui aussi : la ligne d'état dit s'il "
            "a affiché la même chose que l'interpréteur."
        ),
        "running": "exécution…",
        "problems": "problème(s)",
        "agree": "les deux exécutions concordent",
        "disagree": "les deux exécutions divergent",
        "loadingPython": "chargement de Python…",
        "loadingCompiler": "chargement du compilateur…",
        "noBundle": "py/playground.zip est absent — lancez `make -C examples web`",
        "linkCopied": "lien copié",
        "recording": "enregistrement\u2026",
        "steps": "pas enregistrés",
        "truncated": "enregistrement arrêté à",
        "evaluating": "évalue",
        "gives": "donne",
        "nothingBound": "rien de lié ici pour l'instant",
        "nothingMutable": "rien de modifiable ici pour l'instant",
        "notYet": "pas encore commencé",
        "linkInBar": "le lien est dans la barre d'adresse",
        "bootHelp": (
            "La page a besoin d'un serveur HTTP et d'un accès réseau pour "
            "charger Pyodide.\nLancez `make -C examples ocaml-docs-serve`, ou "
            "changez PYODIDE_VERSION dans app.js."
        ),
    },
}

#: What `app.js` reads out of `window.STRINGS`. The rest fills the page.
RUNTIME_STRINGS = (
    "running", "problems", "agree", "disagree", "loadingPython",
    "loadingCompiler", "noBundle", "linkCopied", "linkInBar", "bootHelp",
    "recording", "steps", "truncated", "evaluating", "gives",
    "nothingBound", "nothingMutable", "notYet",
)  # fmt: skip


def add_tree(bundle: zipfile.ZipFile, source: Path, prefix: str) -> int:
    written = 0
    for path in sorted(source.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        bundle.write(path, f"{prefix}/{path.relative_to(source)}")
        written += 1
    return written


def code(text: str) -> str:
    """A markdown code span. A `|` inside one would end a table cell."""
    return f"`{text}`".replace("|", "\\|")


def operators() -> str:
    """The precedence table, from the one the parser cascades over."""
    rows = [
        f"| {place} | {' '.join(code(op) for op in ops)} | {assoc} |"
        for place, (ops, assoc) in enumerate(reversed(LEVELS), start=1)
    ]
    header = ["| level | operators | associates |", "| --- | --- | --- |"]
    return "\n".join(header + rows)


def keywords() -> str:
    """Every reserved word, from the lexer's own set."""
    return " ".join(code(word) for word in sorted(KEYWORDS))


def stdlib() -> str:
    """Every prelude name with its type, from the checker's own table."""
    groups: dict[str, list[tuple[str, str]]] = {"": []}
    for name, written in PRELUDE_TYPES.items():
        module, _, rest = name.partition(".")
        where = module if rest else ""
        groups.setdefault(where, []).append((rest or name, written))
    out = []
    for where, entries in groups.items():
        heading = where or "Always in scope"
        out += [f"### {heading}\n", "| name | type |", "| --- | --- |"]
        out += [
            f"| {code(f'{where}.{name}' if where else name)} | {code(written)} |"
            for name, written in entries
        ]
        out.append("")
    return "\n".join(out)


def reference(lang: str) -> Path:
    """One edition's reference card, with its derived tables filled in."""
    template = Path(str(CARD).format(lang=lang))
    page = template.read_text(encoding="utf-8")
    for marker, made in (
        ("<!--OPERATORS-->", operators()),
        ("<!--KEYWORDS-->", keywords()),
        ("<!--STDLIB-->", stdlib()),
    ):
        if marker not in page:
            raise ValueError(f"{template} has no {marker}")
        page = page.replace(marker, made)
    written = template.with_name("reference.md")
    written.write_text(page, encoding="utf-8")
    return written


def playground(lang: str, into: Path) -> Path:
    """The playground, with one edition's strings, copied into `into`.

    `app.js` and `style.css` are the same for both; only the page differs,
    and every string it shows comes from `PLAYGROUND` rather than from the
    markup or the code.
    """
    words = PLAYGROUND[lang]
    page = PAGE.read_text(encoding="utf-8")
    runtime = {name: words[name] for name in RUNTIME_STRINGS}
    page = page.replace("{{strings}}", json.dumps(runtime, ensure_ascii=False))
    for key, value in words.items():
        page = page.replace(f"{{{{{key}}}}}", value)
    if "{{" in page:
        left = page[page.index("{{") : page.index("{{") + 30]
        raise ValueError(f"{PAGE.name}: no string for {left}")
    into.mkdir(parents=True, exist_ok=True)
    (into / "index.html").write_text(page, encoding="utf-8")
    if into.resolve() == WEB.resolve():
        return into / "index.html"
    for name in ("app.js", "style.css"):
        shutil.copy2(WEB / name, into / name)
    if (WEB / "py").is_dir():
        shutil.copytree(WEB / "py", into / "py", dirs_exist_ok=True)
    return into / "index.html"


def main(target: Path = BUNDLE) -> Path:
    """Write the bundle, and say what went into it."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as bundle:
        modules = add_tree(bundle, ROOT / "src" / "astero", "astero")
        modules += add_tree(bundle, EXAMPLE / "src" / "ocaml", "ocaml")
        # Flat in the zip, whatever the tree looks like: the page lists
        # what it finds in one directory, and the names are unique.
        programmes = sorted((EXAMPLE / "corpus").rglob("*.ml"))
        for path in programmes:
            bundle.write(path, f"corpus/{path.name}")
        # `grimaud/` is copied under the GPL-3.0, which travels with the
        # copies. Not a `.ml`, so the page does not list it.
        bundle.write(EXAMPLE / "corpus/grimaud/LICENSE", "corpus/LICENSE.grimaud")
    for lang in LANGUAGES:
        reference(lang)
        playground(lang, DOCS / lang / "src" / "play")
    # The standalone `make -C examples web-serve` serves `web/` itself, so
    # the English page is written there too.
    playground("en", WEB)
    size = target.stat().st_size // 1024
    # `relative_to` only where it applies: a test builds into a temporary
    # directory, which is not under the repository at all.
    where = target.relative_to(ROOT) if target.is_relative_to(ROOT) else target
    print(f"{where}: {modules + 1} modules, {len(programmes)} programmes, {size} KB")
    return target


if __name__ == "__main__":
    main()
