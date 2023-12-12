from email_validator import validate_email, EmailNotValidError
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection

from utils import check_password, hash_password
from mysql.connector import Error

# 회원가입 API
class UserRegisterResource(Resource) :
    
    def post(self) :
        
        data = request.get_json()

        try :
            validate_email(data['email'])
        except EmailNotValidError as e :
            print(e)
            return {'error' : str(e)}, 400
        
        if len(data['password']) < 4 or len(data['password']) > 15 :
            return {'error' : '비밀번호는 4글자 이상 15글자 이하로 설정해 주세요.'}
        
        password = hash_password(data['password'])

        try :
            connection = get_connection()
            query = '''insert into user
                        (email, password, nickname, gender)
                        values
                        (%s, %s, %s, %s);'''
            record = (data['email'],
                      password,
                      data['nickname'],
                      data['gender'])
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'error' : str(e)}, 500
        
        access_token = create_access_token(user_id)

        return {'result' : 'success',
                'accessToken' : access_token}, 200


# 로그인 API
class UserLoginResource(Resource) :

   def post(self) :
       
        data = request.get_json()

        try :
            connection = get_connection()
            query = '''select *
                        from user
                        where email = %s;'''
            record = (data['email'], )

            cursor = connection.cursor(dictionary = True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 500
        
        if len(result_list) == 0 :
            return {'error' : '먼저 회원가입을 해주세요.'}, 400
        
        check = check_password(data['password'], result_list[0]['password'])

        if check == False :
            return{'error' : '비밀번호가 틀렸습니다.'}, 400
        
        access_token = create_access_token(result_list[0]['id'])

        return {'result' : 'success',
                'accessToken' : access_token}, 200


# 로그아웃 API
jwt_blocklist = set()
class UserLogoutResource(Resource) :

    @jwt_required()
    def delete(self) :

        jti = get_jwt()['jti']
        print(jti)

        jwt_blocklist.add(jti)

        return {"result" : "success"}, 200


