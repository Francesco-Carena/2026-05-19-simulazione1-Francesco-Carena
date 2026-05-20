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
    def getPopularity(genreId):
        conn = DBConnect.get_connection()
        result = {}
        cursor = conn.cursor(dictionary=True)
        query = """select distinct ar.ArtistId, SUM(il.Quantity) as Popularity
                    from track t, album a, artist ar,invoiceline il 
                    where t.AlbumId=a.AlbumId and t.TrackId =il.TrackId and ar.ArtistId=a.ArtistId and t.GenreId=%s 
                    group by ar.ArtistId """

        cursor.execute(query, (genreId,))

        for row in cursor:
            result[row["ArtistId"]]=row["Popularity"]

        cursor.close()
        conn.close()
        return result

    @staticmethod
    def getAllEdges(genreId):
        conn = DBConnect.get_connection()
        result = []
        cursor = conn.cursor(dictionary=True)
        query = """SELECT DISTINCT ar1.ArtistId as ID1, ar2.ArtistId as ID2
                FROM artist ar1, album al1, track t1, invoice inv1, invoiceline il1,
                artist ar2, album al2, track t2, invoice inv2, invoiceline il2
                WHERE 
                inv1.InvoiceId = il1.InvoiceId 
                AND il1.TrackId = t1.TrackId 
                AND t1.AlbumId = al1.AlbumId 
                AND al1.ArtistId = ar1.ArtistId
                
                AND inv2.InvoiceId = il2.InvoiceId 
                AND il2.TrackId = t2.TrackId 
                AND t2.AlbumId = al2.AlbumId 
                AND al2.ArtistId = ar2.ArtistId 
                
                AND inv1.CustomerId = inv2.CustomerId 
                AND ar1.ArtistId < ar2.ArtistId
                
                AND t1.GenreId = %s 
                AND t2.GenreId = %s"""

        cursor.execute(query, (genreId, genreId))

        for row in cursor:
            result.append((row["ID1"],row["ID2"]))

        cursor.close()
        conn.close()
        return result