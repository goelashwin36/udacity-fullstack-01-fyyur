from app import db
from datetime import *

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="Venue", lazy="dynamic")

    def __init__(self, name, city, state, address, phone, website_link, genres, image_link, facebook_link, seeking_talent=False, seeking_description=""):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.website_link = website_link
        self.genres = genres
        self.image_link = image_link
        self.facebook_link = image_link
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(Self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def shortDetails(self):

        return {
            'id': self.id,
            'name': self.name,
        }

    def longDetails(self):

        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
        }

    def details(self):

        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website_link': self.website_link,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

    def __repr__(self):

        return "<Venue {self.id} {self.description}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy="dynamic")

    def __init__(self, name, genres, city, state, phone, website_link, image_link, facebook_link, seeking_venue=False, seeking_description=""):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.website_link = website_link
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description
        self.image_link = image_link
        self.facebook_link = facebook_link

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(Self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def shortDetails(self):

        return {
            'id': self.id,
            'name': self.name,
        }

    def details(self):

        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website_link': self.website_link,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }


class Show(db.Model):

    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(Self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S')
        }

    def artist_details(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S')
        }

    def venue_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S')
        }