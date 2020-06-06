import community as community_louvain
import networkx as nx
import netflow_tools
import matplotlib.cm as cm
import matplotlib.pyplot as plt


def add_node(G, node):
    if not G.has_node(node):
        G.add_node(node)


def create_graph(interface_pairs):
    G = nx.Graph()
    for interface1, interface2 in interface_pairs:
        add_node(G, interface1)
        add_node(G, interface2)
        G.add_edge(interface1, interface2)
    return G


def get_pairs(filename, threshold):
    pairs_dict = netflow_tools.read_dict(filename)
    pairs = set()
    for pair, correlation in pairs_dict.items():
        if abs(float(correlation)) >= threshold:
            pairs.add((pair.split(",")[0][2:-1], pair.split(",")[1][2:-2]))
    return pairs


def get_cliques(partition):
    clique_dict = {}
    for clique in set(partition.values()):
        clique_dict[clique] = set()
    for interface, clique in partition.items():
        clique_dict[clique].add(interface)
    return clique_dict


def draw_cliques(G, partition):
    # draw the graph
    pos = nx.spring_layout(G)
    # color the nodes according to their partition
    cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
    nx.draw_networkx_nodes(G, pos, partition.keys(), node_size=40,
                           cmap=cmap, node_color=list(partition.values()))
    nx.draw_networkx_edges(G, pos, alpha=0.7)
    plt.show()


def cluster_interfaces(filename, threshold):
    pairs = get_pairs(filename, threshold)
    G = create_graph(pairs)
    partition = community_louvain.best_partition(G)
    netflow_tools.write_dict(get_cliques(partition), 'clique_dict')
    draw_cliques(G, partition)
