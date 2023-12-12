from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

# 영화정보 리뷰갯수정렬 API
class MovieListResource(Resource) :

    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select m.id, m.title, count(r.movieId) as review_cnt, avg(rating) as avg_rating
            from movie m
            left join review r
            on m.id = r.movieId
            group by m.title
            order by review_cnt desc
            limit '''+ str(offset) +''' , '''+ str(limit) +''' ;'''

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            for row in result_list:
                # avg_rating 값이 소수인 경우 float로 변환
                if 'avg_rating' in row and row['avg_rating'] is not None:
                    row['avg_rating'] = float(row['avg_rating'])

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500        

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}


# 영화 상세 정보
class MovieResource(Resource) :

    def get(self, movie_id) :

        try :
            connection = get_connection()

            query = '''select m.id, m.title, m.year, m.attendance, avg(rating) as avg_rating
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        where m.id = %s
                        group by m.title;'''
            
            record = (movie_id, )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list:
                result_list[0]['year'] = row['year'].isoformat()
                i = i + 1
            # avg_rating 값이 소수인 경우 float로 변환
                if 'avg_rating' in row and row['avg_rating'] is not None:
                    row['avg_rating'] = float(row['avg_rating'])

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500
        
        if len(result_list) == 0 :
            return {"result" : "fail",
                    "message" : "해당데이터가 없습니다."}, 400
        else :
            return {'result' : 'success', 
                    'item' : result_list[0] }


# 영화 리뷰 정보
# class MovieReviewResource(Resource) :

#     def get(self, movie_id) :

#         offset = request.args.get('offset', 0)
#         limit = request.args.get('limit', 25)

#         try :
#             connection = get_connection()

#             query = '''select m.id, m.title, u.nickname, u.gender, r.rating
#                         from movie m
#                         left join review r
#                         on m.id = r.movieId
#                         join user u
#                         on u.id = r.userId
#                         where m.id = %s
#                         order by u.nickname
#                         limit %s, %s;'''
            
#             record = (movie_id, offset, limit)

#             cursor = connection.cursor(dictionary = True)

#             cursor.execute(query, record)

#             result_list = cursor.fetchall()

#             cursor.close()
#             connection.close()

#         except Error as e:
#             print(e)
#             cursor.close()
#             connection.close()
#             return {"result" : "fail", "error" : str(e)}, 500
        
#         if len(result_list) == 0 :
#             return {"result" : "fail",
#                     "message" : "해당데이터가 없습니다."}, 400
#         else :
#             return {'result' : 'success', 
#                     'item' : result_list,
#                     'count' : len(result_list)}


