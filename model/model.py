import networkx as nx

from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph=nx.DiGraph()
        self._idMapArtists={}

    def createGraph(self, genreId):
        self._graph.clear()
        self._graph.clear_edges()
        self._idMapArtists = {}
        artists=DAO.getNodes(genreId)
        self._graph.add_nodes_from(artists)
        for a in artists:
            self._idMapArtists[a.ArtistId]=a
        self._getPopularity()
        self._addEdges()

    def _getPopularity(self):
        popularity=DAO.getPopularity()
        for a_id, artista in self._idMapArtists.items():
            artista.popularity=int(popularity.get(a_id,0))


    def _addEdges(self):
        edges=DAO.getAllEdges()
        for id1,id2 in edges:
            if id1 in self._idMapArtists and id2 in self._idMapArtists:
                a1=self._idMapArtists[id1]
                a2=self._idMapArtists[id2]
                peso=a1.popularity+a2.popularity

                if a1.popularity>a2.popularity:
                    self._graph.add_edge(a1,a2,weight=peso)
                elif a2.popularity>a1.popularity:
                    self._graph.add_edge(a2,a1,weight=peso)
                else:
                    self._graph.add_edge(a1,a2,weight=peso)
                    self._graph.add_edge(a2,a1,weight=peso)

    def getAllGeneri(self):
        return DAO.getAllGeneri()

    def getInfoGraph(self):
        bestArtist=None
        influenceMax=-float('inf')
        for artist in self._graph.nodes:
            influenza=self._calcolaInfluenza(artist)
            if influenza>influenceMax:
                bestArtist=artist
                influenceMax=influenza
        return len(self._graph.nodes), len(self._graph.edges), bestArtist, influenceMax

    def _calcolaInfluenza(self, artist):
        pesoUscenti=0
        pesoEntranti=0
        for u,v, data in self._graph.out_edges(artist, data=True):
            pesoUscenti+=data["weight"]
        for u,v, data in self._graph.in_edges(artist, data=True):
            pesoUscenti+=data["weight"]
        return pesoUscenti-pesoEntranti

    def getTopEdges(self):
        edges=self._graph.edges(data=True)
        edgesSorted=sorted(edges, key=lambda x: x[2]["weight"], reverse= True)
        return edgesSorted