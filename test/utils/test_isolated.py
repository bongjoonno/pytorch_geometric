import torch

from torch_geometric.testing import is_full_test
from torch_geometric.utils import (
    contains_isolated_nodes,
    num_isolated_nodes,
    remove_isolated_nodes,
)


def test_num_isolated_nodes():
    edge_index = torch.tensor([[0, 1, 0], [1, 0, 0]])
    assert num_isolated_nodes(edge_index) == 0
    assert num_isolated_nodes(edge_index, num_nodes=3) == 1

    if is_full_test():
        jit = torch.jit.script(num_isolated_nodes)
        assert jit(edge_index) == 0
        assert jit(edge_index, num_nodes=3) == 1

    edge_index = torch.tensor([[0, 1, 2, 0], [1, 0, 2, 0]])
    assert num_isolated_nodes(edge_index, num_nodes=3) == 1


def test_bipartite_num_isolated_nodes():
    edge_index = torch.tensor([[0, 1], [0, 1]])
    assert num_isolated_nodes(edge_index, num_nodes=(2, 2)) == 0
    assert num_isolated_nodes(edge_index, num_nodes=(2, 3)) == 1
    assert num_isolated_nodes(edge_index, num_nodes=(3, 3)) == 2

    if is_full_test():
        jit = torch.jit.script(num_isolated_nodes)
        assert jit(edge_index, num_nodes=(2, 2)) == 0
        assert jit(edge_index, num_nodes=(2, 3)) == 1
        assert jit(edge_index, num_nodes=(3, 3)) == 2


def test_contains_isolated_nodes():
    edge_index = torch.tensor([[0, 1, 0], [1, 0, 0]])
    assert not contains_isolated_nodes(edge_index)
    assert contains_isolated_nodes(edge_index, num_nodes=3)

    if is_full_test():
        jit = torch.jit.script(contains_isolated_nodes)
        assert not jit(edge_index)
        assert jit(edge_index, num_nodes=3)

    edge_index = torch.tensor([[0, 1, 2, 0], [1, 0, 2, 0]])
    assert contains_isolated_nodes(edge_index)


def test_bipartite_contains_isolated_nodes():
    edge_index = torch.tensor([[0, 1], [0, 1]])
    assert not contains_isolated_nodes(edge_index, num_nodes=(2, 2))
    assert contains_isolated_nodes(edge_index, num_nodes=(2, 3))
    assert contains_isolated_nodes(edge_index, num_nodes=(3, 3))

    if is_full_test():
        jit = torch.jit.script(contains_isolated_nodes)
        assert not jit(edge_index, num_nodes=(2, 2))
        assert jit(edge_index, num_nodes=(2, 3))
        assert jit(edge_index, num_nodes=(3, 3))


def test_remove_isolated_nodes():
    edge_index = torch.tensor([[0, 1, 0], [1, 0, 0]])

    out, _, mask = remove_isolated_nodes(edge_index)
    assert out.tolist() == [[0, 1, 0], [1, 0, 0]]
    assert mask.tolist() == [1, 1]

    if is_full_test():
        jit = torch.jit.script(remove_isolated_nodes)
        out, _, mask = jit(edge_index)
        assert out.tolist() == [[0, 1, 0], [1, 0, 0]]
        assert mask.tolist() == [1, 1]

    out, _, mask = remove_isolated_nodes(edge_index, num_nodes=3)
    assert out.tolist() == [[0, 1, 0], [1, 0, 0]]
    assert mask.tolist() == [1, 1, 0]

    edge_index = torch.tensor([[0, 2, 1, 0, 2], [2, 0, 1, 0, 2]])
    edge_attr = torch.tensor([1, 2, 3, 4, 5])
    out1, out2, mask = remove_isolated_nodes(edge_index, edge_attr)
    assert out1.tolist() == [[0, 1, 0, 1], [1, 0, 0, 1]]
    assert out2.tolist() == [1, 2, 4, 5]
    assert mask.tolist() == [1, 0, 1]


def test_remove_bipartite_isolated_nodes():
    edge_index = torch.tensor([[0, 1], [1, 2]])

    out, _, (src_mask,
             dst_mask) = remove_isolated_nodes(edge_index, num_nodes=(2, 3))
    assert out.tolist() == [[0, 1], [0, 1]]
    assert src_mask.tolist() == [1, 1]
    assert dst_mask.tolist() == [0, 1, 1]

    if is_full_test():
        jit = torch.jit.script(remove_isolated_nodes)
        out, _, (src_mask, dst_mask) = jit(edge_index, num_nodes=(2, 3))
        assert out.tolist() == [[0, 1], [0, 1]]
        assert src_mask.tolist() == [1, 1]
        assert dst_mask.tolist() == [0, 1, 1]

    edge_index = torch.tensor([[0, 1, 0], [1, 0, 0]])
    out, _, mask = remove_isolated_nodes(edge_index, num_nodes=(3, 3))
    assert out.tolist() == [[0, 1, 0], [1, 0, 0]]
    assert mask[0].tolist() == [1, 1, 0]
    assert mask[1].tolist() == [1, 1, 0]
