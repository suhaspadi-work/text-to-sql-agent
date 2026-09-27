import sqlite3

conn = sqlite3.connect('chinook.db')
cursor = conn.cursor()

queries = {
    1: "SELECT COUNT(*) FROM Track WHERE GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Rock');",
    2: "SELECT Country, COUNT(*) as cnt FROM Customer GROUP BY Country ORDER BY cnt DESC LIMIT 1;",
    3: "SELECT Name FROM Artist WHERE ArtistId = (SELECT ArtistId FROM Album WHERE AlbumId = (SELECT AlbumId FROM Track WHERE Name = 'Balls to the Wall'));",
    4: "SELECT ROUND(AVG(Total), 2) FROM Invoice;",
    5: "SELECT COUNT(*) FROM Employee;",
    6: "SELECT p.Name, COUNT(*) as cnt FROM Playlist p JOIN PlaylistTrack pt ON p.PlaylistId = pt.PlaylistId GROUP BY p.PlaylistId ORDER BY cnt DESC LIMIT 1;",
    7: "SELECT COUNT(DISTINCT CustomerId) FROM Invoice WHERE BillingCountry = 'USA';",
    8: "SELECT MediaType.Name FROM MediaType JOIN Track ON MediaType.MediaTypeId = Track.MediaTypeId GROUP BY MediaType.MediaTypeId ORDER BY COUNT(*) DESC LIMIT 1;",
    9: "SELECT Genre.Name, COUNT(*) as cnt FROM Track JOIN Genre ON Track.GenreId = Genre.GenreId GROUP BY Genre.GenreId ORDER BY cnt ASC LIMIT 1;",
    10: "SELECT COUNT(*) FROM Customer WHERE SupportRepId IS NOT NULL;",
    11: "SELECT ROUND(SUM(UnitPrice * Quantity), 2) FROM InvoiceLine JOIN Track ON InvoiceLine.TrackId = Track.TrackId WHERE Track.GenreId = (SELECT GenreId FROM Genre WHERE Name = 'Jazz');",
    12: "SELECT Track.Name, Track.Milliseconds FROM Track ORDER BY Milliseconds DESC LIMIT 1;",
    13: "SELECT COUNT(*) FROM Album WHERE ArtistId = (SELECT ArtistId FROM Artist WHERE Name = 'Iron Maiden');",
    14: "SELECT COUNT(*) FROM Customer WHERE Fax IS NULL;",
    15: "SELECT City, COUNT(*) as cnt FROM Customer GROUP BY City ORDER BY cnt DESC LIMIT 1;",
}

with open('ground_truth_results.txt', 'w') as f:
    for num, q in queries.items():
        try:
            cursor.execute(q)
            result = cursor.fetchall()
            line = f'{num}: {result}'
        except Exception as e:
            line = f'{num}: ERROR - {e}'
        print(line)
        f.write(line + '\n')

conn.close()
print("\nResults written to ground_truth_results.txt")