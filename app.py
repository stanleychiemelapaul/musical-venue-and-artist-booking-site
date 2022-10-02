#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from itertools import count
import json
from time import timezone
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from models import db, Venue, Artist, Association
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime, timedelta
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


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
  return render_template('pages/venues.html', lists=Venue.query.all() )


@app.route('/venues/search', methods=['POST'])
def search_venues():
    searchreq = request.form["search_term"]
    search = "%{}%".format(searchreq)
    VenueResult = Venue.query.filter(Venue.name.ilike(search)).all()
    
    return render_template('pages/search_venues.html', results=VenueResult, search_term=searchreq)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows_query = db.session.query(Association, Artist).join(Artist).filter(Association.venue_id==venue_id).filter(Association.start_time<datetime.now()).all()

  upcoming_shows_query = db.session.query(Association, Artist).join(Artist).filter(Association.venue_id==venue_id).filter(Association.start_time>datetime.now()).all() 

  return render_template('pages/show_venue.html', 
  past_shows=past_shows_query, 
  upcoming_shows=upcoming_shows_query,
  venue=Venue.query.get(venue_id))




#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    error = False
    if form.validate():
      try:
        
        user = Venue(name = form.name.data, city = form.city.data, state = form.state.data, address = form.address.data, phone = form.phone.data, image_link = form.image_link.data, genres = request.form.getlist('genres'), facebook_link = form.facebook_link.data, website_link = form.website_link.data, seeking_description = form.seeking_description.data)
        
        db.session.add(user)

        db.session.commit()
      except:
        error = True
        db.session.rollback()
        
      finally:
        db.session.close()
        if error == True:
          flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        else:
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
    return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()
      return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    searchreq = request.form["search_term"]
    search = "%{}%".format(searchreq)
    ArtistsSearchResult = Artist.query.filter(Artist.name.ilike(search)).all()
    
    return render_template('pages/search_artists.html', results=ArtistsSearchResult, search_term=searchreq)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows_query = db.session.query(Association, Venue).join(Venue).filter(Association.artist_id==artist_id).filter(Association.start_time<datetime.now()).all()

  upcoming_shows_query = db.session.query(Association, Venue).join(Venue).filter(Association.artist_id==artist_id).filter(Association.start_time>datetime.now()).all() 
    
  return render_template('pages/show_artist.html', 
  past_shows=past_shows_query, 
  upcoming_shows=upcoming_shows_query,
  artist=Artist.query.get(artist_id))



#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    theartist=Artist.query.get(artist_id)
    form.name.data = theartist.name
    form.city.data = theartist.city
    form.state.data = theartist.state
    form.phone.data = theartist.phone
    form.genres.data = theartist.genres
    form.facebook_link.data = theartist.facebook_link

    form.image_link.data = theartist.image_link
    form.website_link.data = theartist.website_link
    form.seeking_description.data = theartist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  error = False
  try:
    thisartist=Artist.query.get(artist_id)
    thisartist.name = form.name.data
    thisartist.city = form.city.data
    thisartist.state = form.state.data
    thisartist.phone = form.phone.data
    thisartist.image_link = form.image_link.data
    thisartist.genres = form.genres.data
    thisartist.facebook_link = form.facebook_link.data
    thisartist.website_link = form.website_link.data
    thisartist.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.')
    else:
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    thevenue=Venue.query.get(venue_id)
    form.name.data = thevenue.name
    form.city.data = thevenue.city
    form.state.data = thevenue.state
    form.address.data = thevenue.address
    form.phone.data = thevenue.phone
    form.genres.data = thevenue.genres
    form.facebook_link.data = thevenue.facebook_link

    form.image_link.data = thevenue.image_link
    form.website_link.data = thevenue.website_link
    form.seeking_description.data = thevenue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  try:
    thisvenue=Venue.query.get(venue_id)
    thisvenue.name = form.name.data
    thisvenue.city = form.city.data
    thisvenue.state = form.state.data
    thisvenue.address = form.address.data
    thisvenue.phone = form.phone.data
    thisvenue.image_link = form.image_link.data
    thisvenue.genres = form.genres.data
    thisvenue.facebook_link = form.facebook_link.data
    thisvenue.website_link = form.website_link.data
    thisvenue.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  error = False
  if form.validate():
    try:
      new_artist = Artist(name = form.name.data, city = form.city.data, state = form.state.data, phone = form.phone.data, image_link = form.image_link.data, genres = request.form.getlist('genres'), facebook_link = form.facebook_link.data, website_link = form.website_link.data, seeking_description = form.seeking_description.data)
      
      db.session.add(new_artist)

      db.session.commit()
    except:
      error = True
      db.session.rollback()
      
    finally:
      db.session.close()
      if error == True:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')

  return render_template('pages/home.html')




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = db.session.query(Association, Venue, Artist).join(Venue).join(Artist).filter(Venue.id == Association.venue_id).filter( Association.artist_id == Artist.id).all()
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False
  try:
    a = Association(venue_id =form.venue_id.data, artist_id=form.artist_id.data, start_time = form.start_time.data)
    db.session.add(a)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
    if error == True:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')

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
