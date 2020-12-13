import json
from copy import deepcopy


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data


def save_json(filename, data, pretty=False):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4 if pretty else None)


def remove_node(network: dict, node_id: str) -> dict:
    network_copy = deepcopy(network)
    # remove node
    network_copy['nodes'] = list(
        filter(
            lambda n: n['id'] != node_id,
            network_copy['nodes']
        )
    )
    # remove links
    network_copy['links'] = list(
        filter(
            lambda n: n['source'] != node_id and n['target'] != node_id,
            network_copy['links']
        )
    )
    # remove demands
    network_copy['demands'] = list(
        filter(
            lambda n: n['source'] != node_id and n['target'] != node_id,
            network_copy['demands']
        )
    )
    demands_left = set(demand['id'] for demand in network_copy['demands'])

    # remove admissible paths
    if 'admissible_paths' in network_copy:
        network_copy['admissible_paths'] = list(
            filter(
                lambda admissible_path: admissible_path['demand_id'] in demands_left,
                network_copy['admissible_paths']
            )
        )

    return network_copy


def filter_nodes(network: dict, wanted_nodes: list, in_place=False, strict=False) -> dict:
    if strict:
        _wanted = set(wanted_nodes)
        _nodes = set(n['id'] for n in network['nodes'])
        _diff = _wanted - _nodes
        if len(_diff) != 0:
            raise ValueError('There are nodes on wanted list that do not exist in network')

    net = deepcopy(network) if not in_place else network

    # remove node
    net['nodes'] = list(
        filter(
            lambda n: n['id'] in wanted_nodes,
            net['nodes']
        )
    )

    # remove links
    net['links'] = list(
        filter(
            lambda n: n['source'] in wanted_nodes and n['target'] in wanted_nodes,
            net['links']
        )
    )

    # remove demands
    net['demands'] = list(
        filter(
            lambda n: n['source'] in wanted_nodes and n['target'] in wanted_nodes,
            net['demands']
        )
    )
    demands_left = set(demand['id'] for demand in net['demands'])

    # remove admissible paths
    if 'admissible_paths' in net:
        net['admissible_paths'] = list(
            filter(
                lambda admissible_path: admissible_path['demand_id'] in demands_left,
                net['admissible_paths']
            )
        )

    return net


def make_subgraph(input_file, output_file, wanted_nodes, strict=False):
    raw_net = load_json(input_file)
    filtered_net = filter_nodes(raw_net, wanted_nodes=wanted_nodes, in_place=True, strict=strict)
    save_json(output_file, filtered_net, pretty=True)


if __name__ == '__main__':
    make_subgraph('json/germany50/germany50.json', 'filtered_net.json', ['Berlin', 'Hamburg', 'Leipzig'])
    make_subgraph('json/polska/polska.json', 'filtered_net.json', ['Warsaw', 'Gdansk', 'Szczecin'])
