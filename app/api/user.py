from flask import request, jsonify
from . import api
from app.models import User, Movie
from app import db, db_m, collection_m, collection_l


@api.route('/user/signup/', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    age = data.get('age')
    gender = data.get('gender')
    occupation = data.get('occupation')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"msg":"user exist"}),401
    else:
        new_user = User(username=username,
                    password=password,
                    age=age,
                    gender=gender,
                    occupation=occupation)
        db.session.add(new_user)
        db.session.flush()
        db.session.commit()
        token = new_user.generate_confirmation_token()
    return jsonify({
        "token":token.decode()
    }), 200


@api.route('/user/signin/', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        flag = user.verify_password(password)
    else:
        return jsonify({
                "errmsg":"no such user"
        }), 401
    if flag is False:
        return jsonify({
            "msg":"wrong password"
        }), 401
    token = user.generate_confirmation_token()
    return jsonify({
        "token": token.decode()
    }), 200



@api.route('/user/information/', methods=['GET'])
@User.check
def user_information(user):
    return jsonify({
        "uid":user.id,
        "username":user.username,
        "age":user.age,
        "gender":user.gender,
        "occupation":user.occupation,
    }), 200


@api.route('/user/information/edit/', methods=['POST'])
@User.check
def user_information_edit(user):
    data = request.get_json()
    user.username = data.get('username')
    user.age = data.get('age')
    user.occupation = data.get('occupation')
    user.gender = data.get('gender')
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"user information edit successful"}),200


@api.route('/user/evaluation/', methods=['GET'])
@User.check
def user_evaluation(user):
    evaluations = collection_m.find({'userid': str(user.id)})
    evaluation_list = []
    for evaluation in evaluations:
        rat = collection_m.find_one({"$and":[{"movieid": str(evaluation["movieid"])},{"userid": str(user.id)}]})
        movie = Movie.query.filter_by(id=int(evaluation["movieid"])).first()
        if not movie:
            continue
        new_evaluation = dict()
        new_evaluation["id"] = movie.id
        new_evaluation["url"] = movie.url
        new_evaluation["title"] = movie.title
        new_evaluation["introduce"] = movie.introduce
        new_evaluation["score"] = round(movie.score, 1)
        new_evaluation["people_num"] = movie.people_num
        new_evaluation["rating"] = 1 if rat else 0
        new_evaluation["rating_num"] = rat["rating"] if rat else 0
        new_evaluation["comment"] = 1 if rat else 0
        new_evaluation["comment_text"] = rat["comment"] if new_evaluation["comment"] == 1 else ""
        evaluation_list.append(new_evaluation)
    return jsonify({
                "evaluation_list":evaluation_list
    }), 200


@api.route('/user/evaluation/<int:mid>/', methods=['DELETE'])
@User.check
def delete_evaluation(user, mid):
    result = collection_m.remove({"$and":[{"movieid": str(mid)},{"userid": str(user.id)}]})
    return jsonify({"msg":"evaluation delete successful "+str(result)}), 200


@api.route('/user/like_list/', methods=['GET'])
@User.check
def like_list(user):
    result = collection_l.find({"userid":str(user.id)})
    likes = [ int(i["movieid"]) for i in result ]
    like_list = []
    for movieid in likes:
        new_movie = dict()
        rat = collection_m.find_one({"$and":[{"movieid": str(movieid)},{"userid": str(user.id)}]})
        movie = Movie.query.filter_by(id=movieid).first()
        if not movie:
            continue
        new_movie["id"] = movie.id
        new_movie["url"] = movie.url
        new_movie["title"] = movie.title
        new_movie["introduce"] = movie.introduce
        new_movie["score"] = round(movie.score, 1)
        new_movie["people_num"] = movie.people_num
        new_movie["rating"] = 1 if rat else 0
        new_movie["rating_num"] = rat["rating"] if rat else 0
        new_movie["comment"] = 1 if rat else 0
        new_movie["comment_text"] = rat["comment"] if new_movie["comment"] == 1 else ""
        like_list.append(new_movie)
    return jsonify({"like_list": like_list})


@api.route('/user/dislike/<int:mid>/', methods=['DELETE'])
@User.check
def dislike(user, mid):
    result = collection_l.remove({"$and":[{"movieid": str(mid)},{"userid": str(user.id)}]})
    return jsonify({"msg":"movie dislike successful " + str(result)}), 200