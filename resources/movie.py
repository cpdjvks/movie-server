from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

# 영화 목록 가져오는 API
class MovieListResource(Resource) :

    @jwt_required()
    def get(self) :

        user_id = get_jwt_identity()

        order = request.args.get('order')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select m.id, m.title, count(r.id) as reviewCnt, avg(rating) as avgRating,
                        if(f.id is null, 0, 1) isFavorite
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        left join favorite f
                        on m.id = f.movieId and f.userId = %s
                        group by m.id
                        order by '''+order+''' desc
                        limit '''+offset+''', '''+limit+''';'''
            
            record = (user_id, )

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500        

        for row in result_list :
                # avgRating 값이 소수인 경우 float로 변환
                if 'avgRating' in row and row['avgRating'] is not None:
                    row['avgRating'] = float(row['avgRating'])

        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}


# 영화 상세 정보
class MovieResource(Resource) :

    @jwt_required(optional = True)
    def get(self, movie_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''select m.id, m.title, m.year, m.attendance, avg(r.rating) as rating_avg
                        from movie m
                        left join review r
                        on m.id = r.movieId
                        where m.id = %s;'''
            
            record = (movie_id, )
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500
        
        i = 0
        for row in result_list:
            result_list[0]['year'] = row['year'].isoformat()
            i = i + 1
        # rating_avg 값이 소수인 경우 float로 변환
            if 'rating_avg' in row and row['rating_avg'] is not None:
                row['rating_avg'] = float(row['rating_avg'])

        return {'result' : 'success', 
                'movieInfo' : result_list[0]}


# 영화 검색
class MovieSearchResource(Resource) :

    @jwt_required()
    def get(self) :

        keyword = request.args.get('keyword')
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()
            query = '''select m.id, m.title, m.summary, count(r.id) reviewCnt, ifnull(avg(r.rating), 0) avgRating
                        from movie m 
                        left join review r
                        on m.id = r.movieId
                        where m.title like '%'''+keyword+'''%' or m.summary like '%'''+keyword+'''%'
                        group by m.id
                        limit '''+offset+''', '''+limit+''';'''
            
            cursor = connection.cursor(dictionary = True)
            cursor.execute(query)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        for row in result_list :
                # avgRating 값이 소수인 경우 float로 변환
                if 'avgRating' in row and row['avgRating'] is not None:
                    row['avgRating'] = float(row['avgRating'])
        
        return {'result' : 'success',
                'items' : result_list,
                'count' : len(result_list)}


