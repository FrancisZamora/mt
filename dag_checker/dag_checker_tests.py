import pytest

from dag_checker import is_acyclic


def test_single_root_commit_is_acyclic():
    """
    A single commit with no parents should be considered acyclic.
    Input:
        [
            ("root", [])
        ]
    Expected:
        True (ACYCLIC)
    """
    commits = [
        ("root", [])
    ]
    assert is_acyclic(commits) is True


def test_linear_chain_is_acyclic():
    """
    A simple linear chain of commits (root → child1 → child2) should be acyclic.
    Input:
        [
            ("a1", []),
            ("b2", ["a1"]),
            ("c3", ["b2"])
        ]
    Expected:
        True (ACYCLIC)
    """
    commits = [
        ("a1", []),
        ("b2", ["a1"]),
        ("c3", ["b2"])
    ]
    assert is_acyclic(commits) is True


def test_simple_merge_is_acyclic():
    """
    A merge commit with two parents but no cycles:
        root → (branch into x and y) → merge
    Input:
        [
            ("root", []),
            ("x", ["root"]),
            ("y", ["root"]),
            ("m", ["x", "y"])
        ]
    Expected:
        True (ACYCLIC)
    """
    commits = [
        ("root", []),
        ("x", ["root"]),
        ("y", ["root"]),
        ("m", ["x", "y"])
    ]
    assert is_acyclic(commits) is True


def test_direct_cycle_two_commits():
    """
    Two commits referencing each other form a cycle:
        A → B → A
    Input:
        [
            ("A", ["B"]),
            ("B", ["A"])
        ]
    Expected:
        False (CYCLIC)
    """
    commits = [
        ("A", ["B"]),
        ("B", ["A"])
    ]
    assert is_acyclic(commits) is False


def test_indirect_cycle_three_commits():
    """
    Three commits forming an indirect cycle:
        A → B → C → A
    Input:
        [
            ("A", ["B"]),
            ("B", ["C"]),
            ("C", ["A"])
        ]
    Expected:
        False (CYCLIC)
    """
    commits = [
        ("A", ["B"]),
        ("B", ["C"]),
        ("C", ["A"])
    ]
    assert is_acyclic(commits) is False


def test_multiple_roots_and_branches_acyclic():
    """
    Multiple root commits and branches without cycles:
        root1     root2
         |         |
         v         v
        a1        b1
         \       /
           \   /
             m
    Input:
        [
            ("root1", []),
            ("root2", []),
            ("a1", ["root1"]),
            ("b1", ["root2"]),
            ("m", ["a1", "b1"])
        ]
    Expected:
        True (ACYCLIC)
    """
    commits = [
        ("root1", []),
        ("root2", []),
        ("a1", ["root1"]),
        ("b1", ["root2"]),
        ("m", ["a1", "b1"])
    ]
    assert is_acyclic(commits) is True


def test_override_definition_creates_cycle():
    """
    A commit ID appears twice, second definition overrides the first, creating a cycle.
    Example 2 from problem statement:
        6
        root1 0
        root2 0
        devA 1 root1
        devB 1 devA
        mergeX 2 devB devA
        root1 1 mergeX  ← overrides root1’s previous parents
    This forms: root1 → mergeX → (devB, devA) → root1
    Input representation after override:
        [
            ("root1", ["mergeX"]),
            ("root2", []),
            ("devA", ["root1"]),
            ("devB", ["devA"]),
            ("mergeX", ["devB", "devA"])
        ]
    Expected:
        False (CYCLIC)
    """
    commits = [
        # The second tuple for "root1" should override the first when constructing the graph.
        ("root1", ["mergeX"]),
        ("root2", []),
        ("devA", ["root1"]),
        ("devB", ["devA"]),
        ("mergeX", ["devB", "devA"])
    ]
    assert is_acyclic(commits) is False


def test_duplicate_definition_acyclic_after_override():
    """
    A commit ID appears twice, second definition overrides the first, but no cycle emerges.
    E.g. override parent list to eliminate a potential cycle.
    Input sequence:
        ("A", ["B"])
        ("B", ["C"])
        ("C", ["A"])
        ("A", ["C"])  ← override A’s parents (now A → C)
    After override:
        A → C → A is still cyclic due to B→C→A→C, so expect False.
    But if override breaks cycle:
        ("A", ["B"])
        ("B", [])
        ("A", [])  ← override to no parents
    Then graph is:
        A with no parents, B with no parents → acyclic.
    Expected:
        True (ACYCLIC)
    """
    commits_override = [
        ("A", ["B"]),
        ("B", ["C"]),
        ("C", ["A"]),
        ("A", ["C"])
    ]
    assert is_acyclic(commits_override) is False

    commits_break_cycle = [
        ("A", ["B"]),
        ("B", []),
        ("A", [])
    ]
    assert is_acyclic(commits_break_cycle) is True


def test_large_acyclic_chain():
    """
    A longer chain that remains acyclic.
    Input: 1000 commits where each commit i has parent i-1 for i in [1..999], and commit0 is root.
    Expected: True (ACYCLIC)
    """
    N = 1000
    commits = [("commit0", [])]
    for i in range(1, N):
        commits.append((f"commit{i}", [f"commit{i-1}"]))
    assert is_acyclic(commits) is True


def test_large_cycle_in_middle():
    """
    A chain of 1000 commits, but introduce a cycle in the middle:
        commit500 → commit499 → ... → commit400 → commit500
    Expected: False (CYCLIC)
    """
    N = 1000
    # Build linear chain first
    commits = [("commit0", [])]
    for i in range(1, N):
        commits.append((f"commit{i}", [f"commit{i-1}"]))
    # Introduce a cycle: make commit400 point to commit500
    # Override the parent list of "commit400"
    commits[400] = ("commit400", ["commit500"])
    assert is_acyclic(commits) is False

