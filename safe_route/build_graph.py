"""
scripts/build_graph.py - Pre-build OSM walk graph for AsthmaSafe routing.
"""

import os
import osmnx as ox

OUT_DIR = "data"
NORTH = -37.780
SOUTH = -37.845
EAST  = 144.995
WEST  = 144.920


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Building walk graph for inner Melbourne bbox...")
    print(f"  N={NORTH}, S={SOUTH}, E={EAST}, W={WEST}")

    try:
        G = ox.graph_from_bbox(
            bbox=(WEST, SOUTH, EAST, NORTH),
            network_type="walk",
        )
    except TypeError:
        G = ox.graph_from_bbox(NORTH, SOUTH, EAST, WEST, network_type="walk")

    walk_path = os.path.join(OUT_DIR, "melbourne_walk.graphml")
    ox.save_graphml(G, walk_path)
    print(f"  saved {walk_path}: {len(G.nodes)} nodes, {len(G.edges)} edges")
    print("\nDone.")


if __name__ == "__main__":
    main()
