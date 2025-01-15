#!/bin/bash

# init.sh - Django 프로젝트 초기화 스크립트

echo "Django 프로젝트의 Migrations 초기화를 시작합니다!"

# db.sqlite3 파일 삭제
DB_FILE="./db.sqlite3"
if [ -f "$DB_FILE" ]; then
    echo "데이터베이스 파일을 찾았습니다. 삭제: $DB_FILE"
    rm "$DB_FILE"
else
    echo "데이터베이스 파일을 찾을 수 없습니다. : $DB_FILE"
fi

# 모든 디렉토리에서 migrations 디렉토리 삭제
echo "모든 하위 디렉토리에 마이그레이션이 있는지 검색 후 삭제..."
find ./ -type d -name "migrations" -exec rm -rf {} +

# 모든 디렉토리에서 __pycache__ 디렉토리 삭제
echo "모든 하위 디렉토리에 파이썬 캐시 파일이 있는지 검색 후 삭제..."
find ./ -type d -name "__pycache__" -exec rm -rf {} +

# 패키지 설치
echo "의존설을 다시 설정하는중..."
pip3 install -r requirements.txt

# makemigrations 실행
echo "마이그레이션을 다시 설정하는 중..."
python3 manage.py makemigrations app_core
python3 manage.py makemigrations app_api
python3 manage.py makemigrations app_user
python3 manage.py makemigrations app_partner
python3 manage.py makemigrations app_supervisor
python3 manage.py makemigrations app_post
python3 manage.py makemigrations app_coupon
python3 manage.py makemigrations app_message
python3 manage.py makemigrations

# migrate 실행
echo "마이그레이션을 적용하는 중..."
python3 manage.py migrate app_core
python3 manage.py migrate app_api
python3 manage.py migrate app_user
python3 manage.py migrate app_partner
python3 manage.py migrate app_supervisor
python3 manage.py migrate app_post
python3 manage.py migrate app_coupon
python3 manage.py migrate app_message
python3 manage.py migrate

echo "Django 프로젝트의 Migrations 초기화가 완료되었습니다! python3 manage.py runserver 명령어로 서버를 실행하세요. :)"
