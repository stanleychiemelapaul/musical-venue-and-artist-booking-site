from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    address = db.Column(db.String())
    phone = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String())
    seeking_description = db.Column(db.String())
    artists = db.relationship('Artist', secondary='shows')

def __repr__(self):
    return f'<Venue {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website_link} {self.seeking_description}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String())
    state = db.Column(db.String())
    phone = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website_link = db.Column(db.String())
    seeking_description = db.Column(db.String())
    venues = db.relationship(Venue, secondary='shows')
    
def __repr__(self):
    return f'<Artist {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website_link} {self.seeking_description}>'

class Association(db.Model):
  __tablename__ = "shows"
  venue_id = db.Column(db.ForeignKey("venue.id"), primary_key=True)
  artist_id = db.Column(db.ForeignKey("artist.id"), primary_key=True)
  start_time = db.Column(db.DateTime(timezone=False))
  venues = db.relationship(Venue, backref=db.backref('allartists'))
  artists = db.relationship(Artist, backref=db.backref('allvenues'))

def __repr__(self):
    return f'<Association {self.venue_id} {self.artist_id} {self.start_time}>'
