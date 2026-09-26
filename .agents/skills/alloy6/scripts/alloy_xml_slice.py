#!/usr/bin/env python3
"""Extract a deterministic, raw-identifier slice from an Alloy XML instance."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


DEFAULT_MAX_XML_BYTES = 32 * 1024 * 1024


def atom_labels(tuple_element: ET.Element) -> list[str]:
    return [atom.attrib["label"] for atom in tuple_element.findall("atom")]


def selected_skolems(instance: ET.Element, prefixes: list[str]) -> list[dict[str, Any]]:
    selected = []
    for skolem in instance.findall("skolem"):
        label = skolem.attrib.get("label", "")
        if prefixes and not any(label.startswith(prefix) for prefix in prefixes):
            continue
        tuples = sorted(atom_labels(item) for item in skolem.findall("tuple"))
        selected.append({"label": label, "tuples": tuples})
    return sorted(selected, key=lambda item: item["label"])


def relevant_fields(
    instance: ET.Element,
    seeds: set[str],
    field_names: set[str],
    expand_depth: int,
) -> tuple[list[dict[str, Any]], set[str]]:
    fields = []
    for field in instance.findall("field"):
        label = field.attrib.get("label", "")
        if field_names and label not in field_names:
            continue
        fields.append(
            {
                "label": label,
                "id": field.attrib.get("ID"),
                "parent_id": field.attrib.get("parentID"),
                "attributes": dict(sorted(field.attrib.items())),
                "tuples": sorted(atom_labels(item) for item in field.findall("tuple")),
            }
        )

    connected = set(seeds)
    frontier = set(seeds)
    selected_tuples: dict[int, set[tuple[str, ...]]] = {}
    for _ in range(expand_depth + 1):
        additions: set[str] = set()
        for index, field in enumerate(fields):
            for item in field["tuples"]:
                if frontier.intersection(item):
                    selected_tuples.setdefault(index, set()).add(tuple(item))
                    additions.update(item)
        frontier = additions - connected
        connected.update(additions)
        if not frontier:
            break

    sliced = []
    for index, field in enumerate(fields):
        tuples = [list(item) for item in sorted(selected_tuples.get(index, set()))]
        if tuples or field_names:
            sliced.append(
                {
                    **field,
                    "total_tuple_count": len(field["tuples"]),
                    "selected_tuple_count": len(tuples),
                    "tuples": tuples,
                }
            )
    sliced.sort(key=lambda item: (item["label"], item["parent_id"] or "", item["id"] or ""))
    return sliced, connected


def signature_memberships(instance: ET.Element, atoms: set[str]) -> list[dict[str, Any]]:
    memberships = []
    for signature in instance.findall("sig"):
        members = sorted(
            atom.attrib["label"]
            for atom in signature.findall("atom")
            if atom.attrib.get("label") in atoms
        )
        if members:
            memberships.append(
                {
                    "label": signature.attrib.get("label", ""),
                    "id": signature.attrib.get("ID"),
                    "attributes": dict(sorted(signature.attrib.items())),
                    "atoms": members,
                }
            )
    return sorted(memberships, key=lambda item: (item["label"], item["id"] or ""))


def slice_document(
    xml_path: Path,
    prefixes: list[str],
    field_names: set[str],
    expand_depth: int,
) -> dict[str, Any]:
    root = ET.parse(xml_path).getroot()
    if root.tag != "alloy":
        raise ValueError(f"expected <alloy> root, found <{root.tag}>")
    instance_elements = root.findall("instance")
    if not instance_elements:
        raise ValueError("Alloy XML contains no <instance> elements")
    all_skolem_labels = {
        skolem.attrib.get("label", "")
        for instance in instance_elements
        for skolem in instance.findall("skolem")
        if skolem.attrib.get("label")
    }
    if not all_skolem_labels:
        raise ValueError("Alloy XML contains no labeled skolems to slice")
    all_field_labels = {
        field.attrib.get("label", "")
        for instance in instance_elements
        for field in instance.findall("field")
    }
    instances = []
    for index, instance in enumerate(instance_elements):
        skolems = selected_skolems(instance, prefixes)
        seeds = {
            atom
            for skolem in skolems
            for item in skolem["tuples"]
            for atom in item
        }
        fields, connected = relevant_fields(instance, seeds, field_names, expand_depth)
        instances.append(
            {
                "index": index,
                "attributes": dict(sorted(instance.attrib.items())),
                "command": instance.attrib.get("command"),
                "filename": instance.attrib.get("filename"),
                "skolems": skolems,
                "signatures": signature_memberships(instance, connected),
                "fields": fields,
            }
        )
    return {
        "source": str(xml_path),
        "identifier_layer": "raw Alloy XML labels; no application normalization applied",
        "skolem_prefixes": prefixes,
        "field_filter": sorted(field_names),
        "unmatched_skolem_prefixes": sorted(
            prefix for prefix in prefixes
            if not any(label.startswith(prefix) for label in all_skolem_labels)
        ),
        "unmatched_field_labels": sorted(field_names - all_field_labels),
        "expand_depth": expand_depth,
        "instances": instances,
    }


def selection_errors(result: dict[str, Any]) -> list[str]:
    errors = []
    if result["unmatched_skolem_prefixes"]:
        errors.append(
            "unmatched skolem prefixes: " + ", ".join(result["unmatched_skolem_prefixes"])
        )
    if result["unmatched_field_labels"]:
        errors.append(
            "unmatched field labels: " + ", ".join(result["unmatched_field_labels"])
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", type=Path)
    parser.add_argument("--skolem-prefix", action="append", default=[])
    parser.add_argument(
        "--all-skolems",
        action="store_true",
        help="Select every skolem explicitly instead of filtering by prefix",
    )
    parser.add_argument("--field", action="append", default=[])
    parser.add_argument("--expand-depth", type=int, default=0)
    parser.add_argument(
        "--allow-large-file",
        action="store_true",
        help=f"Allow XML larger than {DEFAULT_MAX_XML_BYTES} bytes",
    )
    args = parser.parse_args()
    if args.all_skolems and args.skolem_prefix:
        parser.error("use --all-skolems or --skolem-prefix, not both")
    if not args.all_skolems and not args.skolem_prefix:
        parser.error("select skolems with --skolem-prefix or explicit --all-skolems")
    if any(not prefix for prefix in args.skolem_prefix):
        parser.error("--skolem-prefix cannot be empty")
    if args.expand_depth < 0:
        parser.error("--expand-depth must be non-negative")
    if not args.xml.is_file():
        parser.error(f"XML file not found: {args.xml}")
    if args.xml.stat().st_size > DEFAULT_MAX_XML_BYTES and not args.allow_large_file:
        parser.error(
            f"XML is larger than {DEFAULT_MAX_XML_BYTES} bytes; "
            "inspect its provenance and pass --allow-large-file explicitly"
        )
    try:
        result = slice_document(
            args.xml,
            [] if args.all_skolems else args.skolem_prefix,
            set(args.field),
            args.expand_depth,
        )
    except (ET.ParseError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    errors = selection_errors(result)
    if errors:
        print("; ".join(errors), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
