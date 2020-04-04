#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import *
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf.init_app(app)

moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venue_query = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    city_state = ""
    data = []
    for venue in venue_query:
        upcoming_shows = venue.shows.filter(
            Show.start_time > current_time).all()

        if(city_state == venue.city + venue.state):
            data[-1]["venues"].append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
            })
        else:
            city_and_state = venue.city + venue.state
            data.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(upcoming_shows)
                }]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():

    venue_query = Venue.query.filter(
        Venue.name.ilike('%' + request.form['search_term']+'%'))
    venues = list(map(Venue.shortDetails, venue_query))

    response = {
        "count": len(venues),
        "data": venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue_query = Venue.query.get(venue_id)

    if venue_query:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        venue_details = Venue.details(venue_query)
        # Find upcoming shows using join
        upcoming_shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
        upcoming_shows_list = list(map(Show.artist_details, upcoming_shows_query))
        venue_details["upcoming_shows"] = upcoming_shows_list
        venue_details["upcoming_shows_count"] = len(upcoming_shows_list)
        # Find past shows using join
        past_shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
        past_shows_list = list(map(Show.artist_details, past_shows_query))
        venue_details["past_shows"] = past_shows_list
        venue_details["past_shows_count"] = len(past_shows_list)
       
        return render_template('pages/show_venue.html', venue=venue_details)
    return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm(request.form)

    if(form.validate()):
        try:
            # Update seeking_talent and description if there in the form
            seeking_talent = False
            seeking_description = ""
            if('seeking_talent' in request.form):
                seeking_talent = request.form['seeking_talent'] == 'y'
            if ('seeking_description' in request.form):
                seeking_description = request.form['seeking_description']
            new_venue = Venue(
                name=request.form['name'],
                genres=request.form.getlist('genres'),
                address=request.form['address'],
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                website_link=request.form['website_link'],
                facebook_link=request.form['facebook_link'],
                image_link=request.form['image_link'],
                seeking_talent=seeking_talent,
                seeking_description=seeking_description)

            Venue.insert(new_venue)
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')

        except SQLAlchemyError as e:
            db.session.rollback()
            print(e._message)
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        print(e._message)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

    query = Artist.query.order_by(Artist.id).all()
    data = []

    for artist in query:
        data.append(Artist.shortDetails(artist))

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    artist_query = Artist.query.filter(
        Artist.name.ilike('%' + request.form['search_term']+'%'))
    artists = list(map(Artist.shortDetails, artist_query))

    response = {
        "count": len(artists),
        "data": artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist_query = Artist.query.get(artist_id)
    
    if artist_query:
        artist_details = Artist.details(artist_query)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        upcoming_shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
        upcoming_shows_list = list(map(Show.venue_details, upcoming_shows_query))
        artist_details["upcoming_shows"] = upcoming_shows_list
        artist_details["upcoming_shows_count"] = len(upcoming_shows_list)
        past_shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
        past_shows_list = list(map(Show.venue_details, past_shows_query))
        artist_details["past_shows"] = past_shows_list
        artist_details["past_shows_count"] = len(past_shows_list)
        
        return render_template('pages/show_artist.html', artist=artist_details)
    
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    form = ArtistForm()

    query = Artist.query.get(artist_id)

    if(query):
        artist_details = Artist.details(query)

        form.name.data = artist_details["name"]
        form.genres.data = artist_details["genres"]
        form.city.data = artist_details["city"]
        form.state.data = artist_details["state"]
        form.phone.data = artist_details["phone"]
        form.website_link.data = artist_details["website_link"]
        form.facebook_link.data = artist_details["facebook_link"]
        form.image_link.data = artist_details["image_link"]

        return render_template('forms/edit_artist.html', form=form, artist=artist_details)

    return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
    artist_data = Artist.query.get(artist_id)

    if(artist_data and form.validate()):
        try:
            # Update seeking_talent and description if there in the form
            seeking_talent = False
            seeking_description = ""
            if('seeking_talent' in request.form):
                seeking_talent = request.form['seeking_talent'] == 'y'
            if ('seeking_description' in request.form):
                seeking_description = request.form['seeking_description']
            setattr(artist_data, 'name', request.form['name'])
            setattr(artist_data, 'genres', request.form.getlist('genres'))
            setattr(artist_data, 'city', request.form['city'])
            setattr(artist_data, 'state', request.form['state'])
            setattr(artist_data, 'phone', request.form['phone'])
            setattr(artist_data, 'website_link', request.form['website_link'])
            setattr(artist_data, 'facebook_link', request.form['facebook_link'])
            setattr(artist_data, 'image_link', request.form['image_link'])
            Artist.update(artist_data)

            return redirect(url_for('show_artist', artist_id=artist_id))

        except SQLAlchemyError as e:
            db.session.rollback()
            print(e._message)
            flash('An error occurred. Artist ' +
                  request.form['name'] + ' could not be updated.')

    return render_template('errors/404.html'), 40



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    query = Venue.query.get(venue_id)

    if(query):

        venue_details = Venue.details(query)
        form.name.data = venue_details["name"]
        form.genres.data = venue_details["genres"]
        form.city.data = venue_details["city"]
        form.address.data = venue_details["address"]
        form.state.data = venue_details["state"]
        form.phone.data = venue_details["phone"]
        form.website_link.data = venue_details["website_link"]
        form.facebook_link.data = venue_details["facebook_link"]
        form.image_link.data = venue_details["image_link"]

        return render_template('forms/edit_venue.html', form=form, venue=venue_details)

    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm(request.form)
    venue_data = Venue.query.get(venue_id)

    if(venue_data and form.validate()):
        try:
            # Update seeking_talent and description if there in the form
            seeking_talent = False
            seeking_description = ""
            if('seeking_talent' in request.form):
                seeking_talent = request.form['seeking_talent'] == 'y'
            if ('seeking_description' in request.form):
                seeking_description = request.form['seeking_description']
            setattr(venue_data, 'name', request.form['name'])
            setattr(venue_data, 'genres', request.form.getlist('genres'))
            setattr(venue_data, 'address', request.form['address'])
            setattr(venue_data, 'city', request.form['city'])
            setattr(venue_data, 'state', request.form['state'])
            setattr(venue_data, 'phone', request.form['phone'])
            setattr(venue_data, 'website_link', request.form['website_link'])
            setattr(venue_data, 'facebook_link', request.form['facebook_link'])
            setattr(venue_data, 'image_link', request.form['image_link'])
            setattr(venue_data, 'seeking_description', seeking_description)
            setattr(venue_data, 'seeking_talent', seeking_talent)
            Venue.update(venue_data)

            return redirect(url_for('show_venue', venue_id=venue_id))

        except SQLAlchemyError as e:
            db.session.rollback()
            print(e._message)
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')

    return render_template('errors/404.html'), 40

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form = ArtistForm(request.form)

    if(form.validate()):
        try:
            seeking_venue = False
            seeking_description = ""
            if('seeking_venue' in request.form):
                seeking_venue = request.form['seeking_venue'] == 'y'
            if ('seeking_description' in request.form):
                seeking_description = request.form['seeking_description']
            new_artist = Artist(
                name=request.form['name'],
                genres=request.form.getlist('genres'),
                city=request.form['city'],
                state=request.form['state'],
                phone=request.form['phone'],
                website_link=request.form['website_link'],
                facebook_link=request.form['facebook_link'],
                image_link=request.form['image_link'],
                seeking_venue=seeking_venue,
                seeking_description=seeking_description)

            Artist.insert(new_artist)
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')

        except SQLAlchemyError as e:
            db.session.rollback()
            print(e._message)
            flash('An error occurred. Artist ' +

                  request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        print(e._message)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("index"))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

    shows_query = Show.query.options(db.joinedload(
        Show.Venue), db.joinedload(Show.Artist)).all()
    data = list(map(Show.details, shows_query))

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():

    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    form = ShowForm(request.form)

    if(form.validate()):
        try:
            new_show = Show(
                venue_id=request.form['venue_id'],
                artist_id=request.form['artist_id'],
                start_time=request.form['start_time'])
            Show.insert(new_show)
            flash('Show was successfully listed!')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
