class Sorter:
    """
    Currently from: Cormen, Leiserson, Rivest, Stein psuedocode

    TODO: Implement iterative version so you don't run into maximum recursion depth exceptions
    """

    def __init__(self):
        self.sorted_vertices = []
        """:type:list[]"""

        self.TIME = 0


    def dfs_visit(self, graph, cur_vertex):
        self.TIME = self.TIME + 1
        cur_vertex.d = self.TIME
        cur_vertex.color = "GRAY"
        for v in cur_vertex.Adj:
            if v.color == "WHITE":
                v.p = cur_vertex.id
                self.dfs_visit(graph, v)
        cur_vertex.color = "BLACK"
        self.TIME = self.TIME + 1
        cur_vertex.f = self.TIME

        #: These verticies will come back topologically sorted
        self.sorted_vertices.append(cur_vertex)


    def dfs(self,graph):
        """

        :param graph:  Needs to have properties {color: str, d: int, f: int, Adj: list}
        :return:
        """
        for v in graph:
            if v.color == "WHITE":
                self.dfs_visit(graph,v)
