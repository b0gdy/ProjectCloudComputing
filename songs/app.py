import mysql.connector
from mysql.connector import connect, Error
import json
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    #return 'Application songs'
    return render_template('index.html')

@app.route('/create-database')
def createDatabase():
	with connect(host='mysqldb', user='root', password='p@ssw0rd1') as connection:
		try:
			drop_database_query = "DROP DATABASE IF EXISTS projectdb"
			create_database_query = "CREATE DATABASE projectdb"
			with connection.cursor() as cursor:
				cursor.execute(drop_database_query)
				cursor.execute(create_database_query)
				connection.commit()
				return 'Database created'
				
		except errors.DatabaseError:
			pass

@app.route('/artists/create-table')
def createTableArtists():
	with connect(host='mysqldb', user='root', password='p@ssw0rd1', database="projectdb") as connection:
		try:
			drop_table_query = "DROP TABLE IF EXISTS artists"
			create_table_query = "CREATE TABLE artists (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255), PRIMARY KEY (id))"
			with connection.cursor() as cursor:
				cursor.execute(drop_table_query)
				cursor.execute(create_table_query)
				connection.commit()
				return 'Table artists created'
				
		except errors.ProgrammingError:
			pass

@app.route('/songs/create-table')
def createTableSongs():
	with connect(host='mysqldb', user='root', password='p@ssw0rd1', database="projectdb") as connection:
		try:
			drop_table_query = "DROP TABLE IF EXISTS songs"
			create_table_query = "CREATE TABLE songs (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255), artistId INT, PRIMARY KEY (id), FOREIGN KEY(artistId) REFERENCES artists(id))"
			with connection.cursor() as cursor:
				cursor.execute(drop_table_query)
				cursor.execute(create_table_query)
				connection.commit()
				return 'Table songs created'
		
		except errors.ProgrammingError:
			pass

@app.route('/artists/add', methods=('GET', 'POST'))
def addArtist():
	if request.method == 'POST':
		name = request.form['name']
		with connect(host='mysqldb', user='root',password='p@ssw0rd1' ,database='projectdb') as connection:
			insert_query = "INSERT INTO artists (name) VALUES (%s)"
			data_query = [name]
			with connection.cursor() as cursor:
				cursor.execute(insert_query, data_query)
				connection.commit()
				return redirect(url_for('getArtists'))
				
	return render_template('addArtist.html')

@app.route('/artists')
def getArtists():
	with connect(host='mysqldb', user='root',password='p@ssw0rd1' ,database='projectdb') as connection:
		select_query = "SELECT * FROM artists"
		with connection.cursor() as cursor:
			cursor.execute(select_query)
			row_header=[x[0] for x in cursor.description]
			result = cursor.fetchall()
			artists=[]
			for row in result:
				artists.append(dict(zip(row_header, row)))
			connection.commit()
			if not artists:
					return "No artists found!"
			return render_template('listArtists.html', artists=artists)

@app.route('/songs/add', methods=('GET', 'POST'))
def addSong():
	if request.method == 'POST':
		name = request.form['name']
		artistName = request.form['artistName']
		with connect(host='mysqldb', user='root',password='p@ssw0rd1' ,database='projectdb') as connection:
			select_query = "SELECT id FROM artists WHERE name = %s"
			data_select_query = [artistName]
			with connection.cursor() as cursor:
				cursor.execute(select_query, data_select_query)
				row_header=[x[0] for x in cursor.description]
				result = cursor.fetchall()
				artists=[]
				for row in result:
					artists.append(dict(zip(row_header, row)))
				if not artists:
					return ("Artist with name %s not found!" %(artistName))
				artistId = artists[0].get('id')
				connection.commit()
				
			insert_query = "INSERT INTO songs (name, artistId) VALUES (%s, %s)"
			data_insert_query = [name, artistId]
			with connection.cursor() as cursor:
				cursor.execute(insert_query, data_insert_query)
				connection.commit()
				return redirect(url_for('getSongs'))
	
	return render_template('addSong.html')
	
@app.route('/songs')
def getSongs():
	with connect(host='mysqldb', user='root',password='p@ssw0rd1' ,database='projectdb') as connection:
		select_query = """SELECT s.id AS 'song.id', s.name AS 'song.name', a.name AS 'artist.name', (
			SELECT COUNT(l.id)
			FROM likes l
			WHERE s.id = l.songId
		) AS 'likes.number'
		FROM songs s
		JOIN artists a ON s.artistId = a.id;
		"""
		with connection.cursor() as cursor:
			cursor.execute(select_query)
			row_header=[x[0] for x in cursor.description]
			result = cursor.fetchall()
			songs=[]
			for row in result:
				songs.append(dict(zip(row_header, row)))
			connection.commit()
			if not songs:
					return "No songs found!"
			return render_template('listSongs.html', songs=songs)

class Artist:
	def __init__(self, id, name):
		self.id = id
		self.name = name

	def getId(self):
		return self.id
	
	def getName(self):
		return self.name
	
	def setId(self, id):
		self.id = id
	
	def setName(self, name):
		self.name = name

class Song:
	def __init__(self, id, name, artistId):
		self.id = id
		self.name = name
		self.artistId = artistId

	def getId(self):
		return self.id
	
	def getName(self):
		return self.name

	def getArtistId(self):
		return self.artistId
	
	def setId(self, id):
		self.id = id
	
	def setName(self, name):
		self.name = name
	
	def setArtistId(self, artistId):
		self.artistId = artistId

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port=5001)
