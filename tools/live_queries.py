#!/usr/bin/env python3

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Optional

import overpass


@dataclass(frozen=True)
class ExampleQuery:
    key: str
    title: str
    query: str
    responseformat: str = "geojson"
    verbosity: str = "body"
    build: bool = True


EXAMPLES: list[ExampleQuery] = [
    ExampleQuery(
        key="cafes_sf_bbox",
        title="Cafes in a small SF bbox",
        query='node["amenity"="cafe"](37.770,-122.450,37.790,-122.430)',
    ),
    ExampleQuery(
        key="route_bus_sf",
        title="Bus route relations in SF bbox (with recursion)",
        query=(
            'relation["route"="bus"](37.770,-122.520,37.805,-122.380);'
            "(._;>;);"
        ),
        verbosity="body geom",
    ),
    ExampleQuery(
        key="is_in_paris_admin2",
        title="Find admin areas containing a point (Paris, admin_level=2)",
        query=(
            "is_in(48.856089,2.29789);"
            'area._[admin_level="2"];'
        ),
    ),
    ExampleQuery(
        key="bus_stops_bonn",
        title="Bus stops in Bonn (area by name)",
        query=(
            'area[name="Bonn"];'
            "node(area)[highway=bus_stop];"
        ),
    ),
    ExampleQuery(
        key="multipolygon_relations",
        title="Multipolygon relations in a small bbox",
        query='rel[type=multipolygon](37.770,-122.450,37.790,-122.430)',
        verbosity="body geom",
    ),
    ExampleQuery(
        key="slc_highways_since_2020",
        title="Salt Lake County highways changed since 2020-08-01",
        query=(
            'area[name="Salt Lake County"]->.a;'
            'way[highway~"primary|secondary|trunk|motorway|residential|tertiary"]'
            '(if: version() == 1)'
            '(newer:"2020-08-01T00:00:00Z")'
            "(area.a);"
        ),
        verbosity="geom",
    ),
]


def list_examples() -> None:
    for idx, ex in enumerate(EXAMPLES, start=1):
        print(f"{idx:2d}. {ex.title} ({ex.key})")


def run_query(
    query: str,
    *,
    responseformat: str,
    verbosity: str,
    build: bool,
    model: bool,
    endpoint: Optional[str],
    timeout: Optional[float],
    debug: bool,
) -> object:
    api = (
        overpass.API(endpoint=endpoint, timeout=timeout, debug=debug)
        if endpoint
        else overpass.API(timeout=timeout, debug=debug)
    )
    kwargs = {
        "responseformat": responseformat,
        "verbosity": verbosity,
        "build": build,
    }
    if model and "model" in api.get.__code__.co_varnames:
        kwargs["model"] = True
    return api.get(query, **kwargs)


def summarize(result: object, responseformat: str, model: bool) -> str:
    if model:
        if hasattr(result, "features"):
            return f"GeoJSON FeatureCollection: {len(result.features)} features"
        if hasattr(result, "elements"):
            return f"Overpass JSON: {len(result.elements)} elements"
        if hasattr(result, "rows"):
            return f"CSV: {len(result.rows)} rows"
        if hasattr(result, "text"):
            return f"XML: {len(result.text)} chars"
    if responseformat == "geojson" and isinstance(result, dict):
        return f"GeoJSON FeatureCollection: {len(result.get('features', []))} features"
    if responseformat == "json" and isinstance(result, dict):
        return f"Overpass JSON: {len(result.get('elements', []))} elements"
    if responseformat.startswith("csv") and isinstance(result, list):
        return f"CSV: {max(len(result) - 1, 0)} rows"
    if responseformat == "xml" and isinstance(result, str):
        return f"XML: {len(result)} chars"
    return f"Result type: {type(result).__name__}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live Overpass QL queries.")
    parser.add_argument("--list", action="store_true", help="List built-in example queries")
    parser.add_argument("--run", type=str, help="Run by example key or numeric index")
    parser.add_argument("--query", type=str, help="Run a custom query string")
    parser.add_argument("--responseformat", type=str, default="geojson")
    parser.add_argument("--verbosity", type=str, default="body")
    parser.add_argument("--build", action="store_true", help="Build query wrapper (default)")
    parser.add_argument("--no-build", action="store_true", help="Use raw query without wrapper")
    parser.add_argument("--model", action="store_true", help="Return Pydantic models")
    parser.add_argument("--endpoint", type=str, default=None)
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--save", type=str, help="Write raw output to a file")

    args = parser.parse_args()

    if args.list:
        list_examples()
        return 0

    if args.query:
        query = args.query
        responseformat = args.responseformat
        verbosity = args.verbosity
        build = not args.no_build
    elif args.run:
        example: Optional[ExampleQuery] = None
        if args.run.isdigit():
            idx = int(args.run) - 1
            if 0 <= idx < len(EXAMPLES):
                example = EXAMPLES[idx]
        else:
            for ex in EXAMPLES:
                if ex.key == args.run:
                    example = ex
                    break
        if example is None:
            print("Unknown example. Use --list to see options.", file=sys.stderr)
            return 2
        query = example.query
        responseformat = example.responseformat
        verbosity = example.verbosity
        build = example.build
    else:
        list_examples()
        choice = input("Choose an example number (or 'c' for custom): ").strip()
        if choice.lower() == "c":
            query = input("Enter Overpass QL: ").strip()
            responseformat = input("responseformat [geojson|json|xml|csv(...)]: ").strip() or "geojson"
            verbosity = input("verbosity [ids|skel|body|tags|meta ...]: ").strip() or "body"
            build = input("build wrapper? [Y/n]: ").strip().lower() != "n"
        else:
            if not choice.isdigit():
                print("Invalid selection.", file=sys.stderr)
                return 2
            idx = int(choice) - 1
            if idx < 0 or idx >= len(EXAMPLES):
                print("Invalid selection.", file=sys.stderr)
                return 2
            example = EXAMPLES[idx]
            query = example.query
            responseformat = example.responseformat
            verbosity = example.verbosity
            build = example.build

    result = run_query(
        query,
        responseformat=responseformat,
        verbosity=verbosity,
        build=build,
        model=args.model,
        endpoint=args.endpoint,
        timeout=args.timeout,
        debug=args.debug,
    )

    print(f"Query: {query}")
    print(summarize(result, responseformat, args.model))

    if args.save:
        if hasattr(result, "to_geojson"):
            raw = result.to_geojson()
        elif hasattr(result, "text"):
            raw = result.text
        else:
            raw = json.dumps(result, indent=2 if args.pretty else None)
        with open(args.save, "w", encoding="utf-8") as fp:
            fp.write(raw)
        print(f"Wrote {args.save}")
        return 0

    if args.pretty and isinstance(result, dict):
        print(json.dumps(result, indent=2))
    elif isinstance(result, str):
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
