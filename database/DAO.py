from database.DB_connect import DBConnect
from model.artist import Artist
from model.genere import Genere


class DAO():
    def __init__(self):
        pass

    @staticmethod
    def getAllGeneri():
        conn=DBConnect.get_connection()
        result=[]
        cursor=conn.cursor(dictionary=True)
        query="""SELECT *
        FROM genre"""

        cursor.execute(query)

        for row in cursor:
            result.append(Genere(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getNodes(genreId):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select DISTINCT ar.ArtistId, ar.Name 
                from track t, album a, artist ar
                where t.GenreId=%s and t.AlbumId=a.AlbumId and ar.ArtistId=a.ArtistId """

        cursor.execute(query, (genreId,))

        for row in cursor:
            result.append(Artist(**row))

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getPopularity():
        conn = DBConnect.get_connection()
        result = {}
        cursor = conn.cursor(dictionary=True)
        query = """select distinct ar.ArtistId, SUM(il.Quantity) as Popularity
                    from track t, album a, artist ar,invoiceline il 
                    where t.AlbumId=a.AlbumId and t.TrackId =il.TrackId and ar.ArtistId=a.ArtistId 
                    group by ar.ArtistId """

        cursor.execute(query,)

        for row in cursor:
            result[row["ArtistId"]]=row["Popularity"]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges():
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """select distinct ar1.ArtistId as ID1, ar2.ArtistId as ID2
                    from artist ar1, album al1,track t1,invoice inv1, invoiceline il1,
                        artist ar2, album al2,track t2,invoice inv2, invoiceline il2
                    where inv1.InvoiceId=inv2.InvoiceId and il1.TrackId=t1.TrackId and t1.AlbumId=al1.AlbumId and al1.ArtistId=ar1.ArtistId
                    and inv2.InvoiceId=il2.InvoiceId and il2.TrackId=t2.TrackId and t2.AlbumId=al2.AlbumId and al2.ArtistId =ar2.ArtistId 
                    and inv1.CustomerId=inv2.CustomerId and ar1.ArtistId<ar2.ArtistId  """

        cursor.execute(query, )

        for row in cursor:
            result.append((row["ID1"],row["ID2"]))

        cursor.close()
        conn.close()
        return result
