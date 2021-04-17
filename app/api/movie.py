from flask import request, jsonify, session
from app import db, db_m, collection_m, collection_l
from . import api
import numpy as np
from app.models import User, Movie, Label, Label_Movie


def user_like_list(uid):
    result = collection_l.find({"userid":str(uid)})
    likes = [ int(i["movieid"]) for i in result ]
    return likes


label_dict = {'Film-Noir': 1,
            'Crime': 2,
            'Romance': 3,
            'Fantasy': 4,
            'Horror': 5,
            "Children's": 6,
            'Action': 7,
            'War': 8,
            'Thrill3er': 9,
            'Sci-Fi': 10,
            'Drama': 11,
            'Western': 12,
            'Musical': 13,
            'Documentary': 14,
            'Animation': 15,
            'Comedy': 16,
            'Mystery': 17,
            'Thriller': 18,
            'Adventure': 19
}


@api.route('/movie/add/', methods=['POST'])
@User.check
def add_movie():
    data = request.get_json()
    url = data.get('url')
    title = data.get('title')
    label_list = data.get('label_list')
    introduce = data.get('introduce')
    new_movie = Movie(url=url,
                      title=title,
                      introduce=introduce)
    db.session.add(new_movie)
    for id in label_list:
        label_movie = Label_Movie(movie_id=new_movie.id,
                                  label_id=id)
        db.session.add(label_movie)
    db.session.commit
    return jsonify({
        "msg": "movie add successful",
        "movieid": new_movie.id
    }), 200


@api.route('/movie/evaluation/', methods=['POST'])
@User.check
def movie_evalutions(user):
    data = request.get_json()
    movie_id = data.get("movie_id")
    rating = int(data.get("rating"))
    comment = data.get("comment")
    collection_m.insert_one({
        "userid": str(user.id),
        "movieid": str(movie_id),
        "rating": str(rating),
        "comment": str(comment)
    })
    movie = Movie.query.filter_by(id=movie_id).first()
    movie.score = (movie.score * movie.people_num + rating) / (movie.people_num + 1)
    movie.people_num += 1
    db.session.add(movie)
    db.session.commit()
    return jsonify({"msg":"evaluation add successful"}), 200


@api.route('/movie/search/', methods=['POST'])
@User.check
def search(user):
    keyword = request.get_json().get("keyword")
    movie_list = []
    movies = Movie.query.filter(Movie.title.contains(keyword)).limit(24).all()
    like_list = user_like_list(user.id)
    for movie in movies:
        new_movie = dict()
        result = collection_m.find_one({"$and":[{"movieid": str(movie.id)},{"userid": str(user.id)}]})
        if movie.id in like_list:
            new_movie["like"] = 1
        else:
            new_movie["like"] = 0
        new_movie["id"] = movie.id
        new_movie["url"] = movie.url
        new_movie["title"] = movie.title
        new_movie["introduce"] = movie.introduce
        new_movie["score"] = round(movie.score, 1)
        new_movie["people_num"] = movie.people_num
        new_movie["rating"] = 1 if result else 0
        new_movie["rating_num"] = int(result["rating"]) if result else 0
        new_movie["evaluation"] = 1 if result else 0
        new_movie["evaluation_text"] = str(result["comment"]) if result else 0
        movie_list.append(new_movie)
    return jsonify({"movie_list":movie_list}), 200


@api.route('/movie/like/', methods=['POST'])
@User.check
def movie_like(user):
    movie_id = request.get_json().get("movie_id")
    collection_l.insert_one({
        "userid": str(user.id),
        "movieid": str(movie_id)
    })
    return jsonify({"msg":"movie like successful"}), 200


@api.route('/movie/label/', methods=['GET'])
@User.check
def movie_label(user):
    label_movie_list = {}
    like_list = user_like_list(user.id)
    for label in label_dict.items():
        label_id = label[1]
        label_word = label[0]
        movie_list = list()
        mmovies = list()
        movies = db.session.query(Movie).join(
            Label_Movie, Label_Movie.label_id == label_id
        ).filter(Movie.id == Label_Movie.movie_id).order_by(db.desc(Movie.score)).limit(30).all()
        if(len(movies) < 30):
            continue
        while len(mmovies) < 6:
            val = np.random.choice(len(movies), 1)[0]
            if movies[val] not in mmovies:
                mmovies.append(movies[val])
        for movie in mmovies:
            new_movie = dict()
            rat = collection_m.find_one({"$and":[{"movieid": str(movie.id)},{"userid": str(user.id)}]})
            if movie.id in like_list:
                new_movie["like"] = 1
            else:
                new_movie["like"] = 0
            new_movie["id"] = movie.id
            new_movie["url"] = movie.url
            new_movie["title"] = movie.title
            new_movie["introduce"] = movie.introduce
            new_movie["score"] = round(movie.score, 1)
            new_movie["people_num"] = movie.people_num
            new_movie["rating"] = 1 if rat else 0
            new_movie["rating_num"] = rat["rating"] if rat else 0
            new_movie["comment"] = 1 if rat else 0
            new_movie["comment_text"] = rat["comment"] if new_movie["comment"] else ""
            movie_list.append(new_movie)
        label_movie_list[label_word] = movie_list
    return jsonify({'label_movie_list': label_movie_list}),200