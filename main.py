from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

TMBD_URL = "https://api.themoviedb.org/3/search/movie"
API_KEY = "ae485b9dd69aceae2a6578c3f4eea1b1"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


class RateMovieForm(FlaskForm):
    rating = FloatField(label='Your Rating out of 10 eg.7.5')
    review = StringField(label='Your Review')
    submit = SubmitField(label='Done')


class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField(label='Add Movie')


@app.route("/")
def home():
    # This line creates a list of all the movies sorted by rating
    all_movies = Movie.query.order_by(Movie.rating).all()

    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:movie_id>", methods=['POST', 'GET'])
def edit(movie_id):
    movie_update = Movie.query.get(movie_id)
    form = RateMovieForm()
    if form.validate_on_submit():
        movie_update.rating = form.rating.data
        movie_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie_update)


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        params = {
            'api_key': API_KEY,
            'language': 'en-US',
            'query': form.title.data
        }
        response = requests.get(url=TMBD_URL, params=params)
        data = response.json()['results']
        # print(data)
        return render_template('select.html', movies=data)

    return render_template("add.html", form=form)


@app.route("/add-movie")
def add_movie():
    movie_id = request.args.get('movie_id')
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url=url).json()
    movie_title = data['original_title']
    movie_date = int(data['release_date'].split('-')[0])
    movie_description = data['overview']
    movie_img_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    print(movie_date)
    new_movie = Movie(
        title=movie_title,
        year=movie_date,
        description=movie_description,
        img_url=movie_img_url
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_id = Movie.query.filter_by(title=movie_title).first().id
    return redirect(url_for('edit',movie_id=movie_id))


@app.route("/delete")
def delete():
    movie_id = request.args.get('movie_id')
    movie_delete = Movie.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
