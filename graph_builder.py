from py2neo import Graph, Node, Relationship
import networkx as nx
import matplotlib.pyplot as plt

class KnowledgeGraphBuilder:
    def __init__(self, uri="neo4j://127.0.0.1:7687", user="neo4j", password="12345678"):
        self.graph = Graph(uri, auth=(user, password))
        # Clear all data after connection is established
        self.graph.run("MATCH (n) DETACH DELETE n")

    def visualize_triplets(self, triplets):
        G = nx.MultiDiGraph()
        for subject, relation, object_ in triplets:
            G.add_edge(subject, object_, label=relation)
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 7))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, arrows=True)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Knowledge Graph Preview")
        plt.show()

    def add_triplet(self, subject, relation, object_):
        sub_node = Node("Entity", name=subject)
        obj_node = Node("Entity", name=object_)
        self.graph.merge(sub_node, "Entity", "name")
        self.graph.merge(obj_node, "Entity", "name")
        rel = Relationship(sub_node, relation.upper(), obj_node)
        self.graph.merge(rel)
        print(f"Added triplet: ({subject}, {relation}, {object_})")