from packages.core.graph import ArtifactGraph

def test_graph_neighbors_are_deterministic():
    g=ArtifactGraph(); g.add_node("A",{}); g.add_node("B",{}); g.link("A","B")
    assert g.neighbors("A")==["B"]
