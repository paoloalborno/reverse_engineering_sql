import json
import graphviz
import networkx as nx

from src.cli import GRAPH_DIR


def build_graph(lineage: dict):
    nx_graph = nx.DiGraph()
    for procedure, procedure_data in lineage['procedures'].items():
        nx_graph.add_node(procedure, type="procedure")
        for table in procedure_data['writes']:
            nx_graph.add_node(table, type='table')
            nx_graph.add_edge(procedure, table, relation='writes', color="red", action="writes")
        for table in procedure_data['reads']:
            nx_graph.add_node(table, type='table')
            nx_graph.add_edge(table, procedure, relation='reads', color="blue", action="read by")

    print("NODES:")
    for node, data in nx_graph.nodes(data=True):
        print(f"  {node} -> {data}")

    print("\nEDGES:")
    for src, dst, data in nx_graph.edges(data=True):
        print(f"  {src} -> {dst}  {data}")
    return nx_graph


def export_graphviz(nx_graph: nx.DiGraph, path: str):
    dot = graphviz.Digraph(comment='Data Lineage', format='png')

    dot.attr(rankdir='LR')  # Left to right
    dot.attr('node', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='8')
    dot.attr(bgcolor='white')

    with dot.subgraph(name='cluster_procedures') as proc:
        proc.attr(label='Stored Procedures', style='filled', color='lightgray')
        for node, data in nx_graph.nodes(data=True):
            if data['type'] == 'procedure':
                proc.node(node, node, shape='box', style='filled,rounded',
                          fillcolor='lightblue', color='blue')

    with dot.subgraph(name='cluster_tables') as tables:
        tables.attr(label='Tables', style='filled', color='lightgray')
        for node, data in nx_graph.nodes(data=True):
            if data['type'] == 'table':
                tables.node(node, node, shape='ellipse', style='filled',
                            fillcolor='orange', color='darkorange')

    for src, dst, data in nx_graph.edges(data=True):
        color = data.get('color', 'black')
        action = data.get('action', '')
        dot.edge(src, dst, color=color, label=action)

    dot.render(path, cleanup=True)


with open(GRAPH_DIR+"lineage_graph.png", "r") as file:
    graph = build_graph(json.loads(file.read()))
    export_graphviz(graph, GRAPH_DIR+"/lineage_graph.png")






