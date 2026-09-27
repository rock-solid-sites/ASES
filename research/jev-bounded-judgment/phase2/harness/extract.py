#!/usr/bin/env python3
"""Deterministic structural extraction for Phase 2. Standard library only.

`tree-sitter`, `ast-grep`, `networkx` and `ctags` are absent from this host, so
this uses `ast` (structure) and `symtable` (scopes). No new infrastructure.

Two hard rules govern the output, both aimed at not flattering the hypothesis:

1. NO PRECOMPUTED ANSWERS. The structure emits FACTS, never a fact about a
   proposition any case asks about. There is no `calls_helper: true`, no
   `shadowed_params`, no `unused_imports`. Where an answer requires an
   intersection (params vs assigned locals; imports vs referenced names) the
   two sides are emitted separately and the model must do the intersection.
   That is what keeps a `judgment` case a judgment under R2 instead of
   collapsing it into a `lookup`.

2. DETERMINISTIC. Same input bytes -> same output bytes, no dict ordering
   surprises, no timestamps, no host paths. The digest of this output is the
   frozen extraction identity that the run asserts.

Representations produced:
  raw     the module source, verbatim
  struct  the extracted structure, rendered as deterministic text
"""
import ast
import hashlib
import json
import os

# Nodes that introduce a new nesting level for control flow.
BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With,
                ast.AsyncWith, ast.Try, ast.ExceptHandler,
                ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                ast.Match)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class ModuleFacts:
    """All extracted facts about one module. Facts only; no answers."""

    def __init__(self, path, name, source):
        self.path = path
        self.name = name
        self.source = source
        self.imports = []            # [{"module":..,"names":[..],"level":int}]
        self.module_symbols = {}     # name -> kind
        self.classes = {}            # name -> {"bases":[..],"methods":[..]}
        self.functions = {}          # qualname -> fact dict
        self.call_edges = []         # [caller_qualname, callee_name]
        self.module_level_names = [] # every name bound at module scope
        self._parse()

    # ---------------------------------------------------------------- parse
    def _parse(self):
        self.tree = ast.parse(self.source)
        module = self.tree

        for node in module.body:
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.imports.append({"module": a.name, "names": None,
                                         "level": 0})
            elif isinstance(node, ast.ImportFrom):
                self.imports.append({"module": node.module or "",
                                     "names": [a.name for a in node.names],
                                     "level": node.level or 0})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.module_symbols[node.name] = "function"
                self.module_level_names.append(node.name)
            elif isinstance(node, ast.ClassDef):
                self.module_symbols[node.name] = "class"
                self.module_level_names.append(node.name)
                self.classes[node.name] = {
                    "bases": [self._dotted(b) for b in node.bases],
                    "methods": [n.name for n in node.body
                                if isinstance(n, (ast.FunctionDef,
                                                  ast.AsyncFunctionDef))],
                    "decorators": [self._dotted(d) for d in node.decorator_list],
                }
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    for nm in self._target_names(t):
                        self.module_symbols[nm] = "variable"
                        self.module_level_names.append(nm)
            elif isinstance(node, ast.AnnAssign) and isinstance(
                    node.target, ast.Name):
                self.module_symbols[node.target.id] = "variable"
                self.module_level_names.append(node.target.id)

        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = self._function_facts(node)

        self._index_qualified()
        self._build_edges()
        self._sort_all()

    def _index_qualified(self):
        """qualname -> fact dict, so a question can target `Class.method`.

        Two functions may share a bare name; only the qualified key is
        unambiguous, and ground truth must never depend on an ambiguous key.
        """
        self.qualified_functions = {}

        def walk_body(body, prefix):
            for child in body:
                if isinstance(child, ast.ClassDef):
                    for sub in child.body:
                        if isinstance(sub, (ast.FunctionDef,
                                            ast.AsyncFunctionDef)):
                            qn = f"{prefix}{child.name}.{sub.name}"
                            self.qualified_functions[qn] = \
                                self._function_facts(sub)
                        elif isinstance(sub, ast.ClassDef):
                            walk_body([sub], f"{prefix}{child.name}.")
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qn = f"{prefix}{child.name}"
                    self.qualified_functions[qn] = self._function_facts(child)
                    walk_body(child.body, f"{qn}.")

        walk_body(self.tree.body, "")
        # Bare-name entries only where unambiguous; ambiguous bare names are
        # dropped so nothing can silently read the wrong function.
        counts = {}
        for qn in self.qualified_functions:
            counts[qn.split(".")[-1]] = counts.get(qn.split(".")[-1], 0) + 1
        self.ambiguous_bare_names = sorted(
            b for b, n in counts.items() if n > 1)

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _dotted(node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = ModuleFacts._dotted(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        if isinstance(node, ast.Call):
            return ModuleFacts._dotted(node.func)
        return ""

    @staticmethod
    def _target_names(t):
        if isinstance(t, ast.Name):
            return [t.id]
        if isinstance(t, (ast.Tuple, ast.List)):
            out = []
            for e in t.elts:
                out.extend(ModuleFacts._target_names(e))
            return out
        return []

    def _function_facts(self, fn):
        params = [a.arg for a in
                  list(fn.args.posonlyargs) + list(fn.args.args) +
                  list(fn.args.kwonlyargs)]
        if fn.args.vararg:
            params.append("*" + fn.args.vararg.arg)
        if fn.args.kwarg:
            params.append("**" + fn.args.kwarg.arg)

        assigned, loads, stores = set(), set(), set()
        max_depth = 0
        has_try = has_raise = False

        for n in ast.walk(fn):
            if isinstance(n, ast.Name):
                if isinstance(n.ctx, ast.Load):
                    loads.add(n.id)
                elif isinstance(n.ctx, ast.Store):
                    stores.add(n.id)
            elif isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                for t in ast.walk(n):
                    if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store):
                        assigned.add(t.id)
            elif isinstance(n, ast.Raise):
                has_raise = True
            elif isinstance(n, ast.ExceptHandler):
                has_try = True

        max_depth = self._max_nesting(fn)
        if any(isinstance(n, ast.Try) for n in ast.walk(fn)):
            has_try = True

        return {
            "name": fn.name,
            "params": sorted(set(params)),
            "decorators": [self._dotted(d) for d in fn.decorator_list],
            "assigned_locals": sorted(assigned | stores),
            "names_loaded": sorted(loads),
            "n_stmts": sum(1 for _ in ast.walk(fn)),
            "n_branches": sum(1 for n in ast.walk(fn)
                              if isinstance(n, BRANCH_NODES)),
            "max_nesting": max_depth,
            "has_try": has_try,
            "has_raise": has_raise,
            "is_generator": any(isinstance(n, (ast.Yield, ast.YieldFrom))
                                for n in ast.walk(fn)),
            "lineno": fn.lineno,
            "end_lineno": getattr(fn, "end_lineno", fn.lineno),
        }

    @staticmethod
    def _max_nesting(fn):
        """Max control-flow nesting inside fn, not counting fn itself."""
        best = 0

        def walk(node, depth):
            nonlocal best
            for child in ast.iter_child_nodes(node):
                d = depth + 1 if isinstance(child, BRANCH_NODES) else depth
                if d > best:
                    best = d
                walk(child, d)

        walk(fn, 0)
        return best

    def _build_edges(self):
        """Direct intra-module call edges: caller qualname -> callee NAME.

        Callers are QUALIFIED (`Class.method`) so same-named methods in
        different classes cannot collide into one bogus edge.

        Resolution against the module symbol table is deliberately left to the
        reader: emitting edges as name pairs rather than as a precomputed
        resolved call graph keeps a path question a composition for the model
        rather than a field lookup.
        """
        seen = set()

        def add(caller, node):
            # Walk for calls but STOP at nested function/class boundaries: a
            # call made inside a nested def is not a call made by `caller`.
            # Without this, "does X directly call Y" would be true whenever a
            # closure inside X calls Y, which is wrong ground truth.
            stack = list(ast.iter_child_nodes(node))
            while stack:
                n = stack.pop()
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef, ast.Lambda)):
                    continue
                if isinstance(n, ast.Call):
                    callee = self._dotted(n.func)
                    if callee:
                        key = (caller, callee)
                        if key not in seen:
                            seen.add(key)
                            self.call_edges.append([caller, callee])
                stack.extend(ast.iter_child_nodes(n))

        def walk_body(body, prefix):
            for child in body:
                if isinstance(child, ast.ClassDef):
                    walk_class(child, f"{prefix}{child.name}.")
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add(f"{prefix}{child.name}", child)
                    walk_body(child.body, f"{prefix}{child.name}.")
                elif isinstance(child, (ast.If, ast.Try, ast.With,
                                        ast.For, ast.While)):
                    walk_body(child.body, prefix)
                    for handler in getattr(child, "handlers", []) or []:
                        walk_body(handler.body, prefix)
                    walk_body(getattr(child, "orelse", []) or [], prefix)
                    walk_body(getattr(child, "finalbody", []) or [], prefix)

        def walk_class(cls, prefix):
            for child in cls.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    add(f"{prefix}{child.name}", child)
                elif isinstance(child, ast.ClassDef):
                    walk_class(child, f"{prefix}{child.name}.")

        walk_body(self.tree.body, "")

    def _sort_all(self):
        self.imports.sort(key=lambda d: (d["module"], str(d["names"])))
        self.module_level_names = sorted(set(self.module_level_names))
        self.module_symbols = dict(sorted(self.module_symbols.items()))
        self.classes = dict(sorted(self.classes.items()))
        self.functions = dict(sorted(self.functions.items()))
        self.call_edges.sort()

    # ------------------------------------------------------------ accessors
    def has_call_edge(self, caller, callee):
        return [caller, callee] in self.call_edges

    def path_exists(self, src, dst, depth):
        """Deterministic BFS bounded by depth. depth<=0 means unbounded."""
        if src == dst:
            return True
        adj = {}
        for a, b in self.call_edges:
            adj.setdefault(a, []).append(b)
        frontier = [(src, 0)]
        seen = {src}
        while frontier:
            node, d = frontier.pop(0)
            if depth and d >= depth:
                continue
            for nxt in adj.get(node, []):
                if nxt == dst:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, d + 1))
        return False

    def path_length(self, src, dst):
        """Shortest edge count src->dst, or None."""
        if src == dst:
            return 0
        adj = {}
        for a, b in self.call_edges:
            adj.setdefault(a, []).append(b)
        frontier = [(src, 0)]
        seen = {src}
        while frontier:
            node, d = frontier.pop(0)
            for nxt in adj.get(node, []):
                if nxt == dst:
                    return d + 1
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append((nxt, d + 1))
        return None

    def param_rebound(self, fn_name, param):
        f = self.qualified_functions.get(fn_name)
        if f is None:
            return None
        return param in f["assigned_locals"]

    def fn_fact(self, qualname):
        return self.qualified_functions.get(qualname)

    def unused_imports(self):
        loaded = set()
        for f in self.qualified_functions.values():
            loaded.update(f["names_loaded"])
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                loaded.add(n.id)
        out = []
        for imp in self.imports:
            if imp["names"] is None:
                root = imp["module"].split(".")[0]
                if root not in loaded:
                    out.append(imp["module"])
            else:
                for nm in imp["names"]:
                    if nm != "*" and nm not in loaded:
                        out.append(f"{imp['module']}.{nm}")
        return sorted(set(out))

    def import_keys(self):
        """Import tokens exactly as they would be written in source.

        `from collections import deque` contributes `collections` and
        `collections.deque`; `import os.path` contributes `os.path` and `os`.
        Used by the admissibility predicate so it tests the token the question
        actually names.
        """
        keys = set()
        for imp in self.imports:
            if imp["names"] is None:
                parts = imp["module"].split(".")
                for i in range(1, len(parts) + 1):
                    keys.add(".".join(parts[:i]))
            else:
                keys.add(imp["module"])
                for nm in imp["names"]:
                    if nm != "*":
                        keys.add(f"{imp['module']}.{nm}")
        return sorted(k for k in keys if k)

    def string_literals(self):
        return sorted({n.value for n in ast.walk(self.tree)
                       if isinstance(n, ast.Constant)
                       and isinstance(n.value, str)})

    # -------------------------------------------------------- representations
    def render_struct(self):
        """Deterministic text rendering of the structure. Facts only."""
        L = []
        L.append(f"MODULE {self.name}")
        L.append("")
        L.append("## module_symbols (name -> kind)")
        for k, v in self.module_symbols.items():
            L.append(f"{k}: {v}")
        L.append("")
        L.append("## imports")
        for imp in self.imports:
            if imp["names"] is None:
                L.append(f"import {imp['module']}")
            else:
                L.append(f"from {'.' * imp['level']}{imp['module']} import "
                         f"{', '.join(imp['names'])}")
        L.append("")
        if self.classes:
            L.append("## classes")
            for cname, c in self.classes.items():
                L.append(f"class {cname}"
                         f" bases=[{', '.join(c['bases'])}]"
                         f" decorators=[{', '.join(c['decorators'])}]"
                         f" methods=[{', '.join(c['methods'])}]")
            L.append("")
        L.append("## functions")
        for fname, f in sorted(self.qualified_functions.items()):
            L.append(f"def {fname}"
                     f" lines={f['lineno']}-{f['end_lineno']}"
                     f" params=[{', '.join(f['params'])}]"
                     f" decorators=[{', '.join(f['decorators'])}]")
            L.append(f"    assigned_locals=[{', '.join(f['assigned_locals'])}]")
            L.append(f"    n_stmts={f['n_stmts']} n_branches={f['n_branches']}"
                     f" max_nesting={f['max_nesting']}"
                     f" has_try={f['has_try']} has_raise={f['has_raise']}"
                     f" is_generator={f['is_generator']}")
            L.append(f"    names_loaded=[{', '.join(f['names_loaded'])}]")
        L.append("")
        L.append("## call_edges (caller -> callee_name)")
        for a, b in self.call_edges:
            L.append(f"{a} -> {b}")
        return "\n".join(L) + "\n"

    def source_of(self, fname):
        """Verbatim source text of one function by QUALIFIED name, by line range."""
        f = self.qualified_functions.get(fname)
        if not f:
            return ""
        lines = self.source.splitlines()
        return "\n".join(lines[f["lineno"] - 1:f["end_lineno"]]) + "\n"

    def as_dict(self):
        return {
            "name": self.name,
            "sha256": sha256_text(self.source),
            "imports": self.imports,
            "module_symbols": self.module_symbols,
            "classes": self.classes,
            "functions": self.qualified_functions,
            "call_edges": self.call_edges,
        }


def load_module(path, name=None):
    src = open(path, encoding="utf-8").read()
    return ModuleFacts(path, name or os.path.basename(path), src)
