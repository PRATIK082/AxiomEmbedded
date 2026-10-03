from packages.core.graph import ArtifactGraph
from packages.context.selector import ContextSelector

def test_context_is_bounded():
    g=ArtifactGraph(); [g.add_node(str(i),{}) for i in range(10)]
    for i in range(9): g.link(str(i),str(i+1))
    assert len(ContextSelector(g).select(["0"])) <= 20
