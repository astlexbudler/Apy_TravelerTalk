#!/bin/bash

# init.sh - Django 프로젝트 초기화 스크립트

echo "Django 프로젝트의 Migrations 초기화를 시작합니다!"

# db.sqlite3 파일 삭제
DB_FILE="./db.sqlite3"
if [ -f "$DB_FILE" ]; then
    echo "데이터베이스 파일을 삭제합니다: $DB_FILE"
    rm "$DB_FILE"
else
    echo "데이터베이스 파일이 없습니다: $DB_FILE"
fi

# migrations 폴더에서 모든 .py 파일 삭제, 하지만 __init__.py는 유지
echo "모든 하위 디렉토리에서 migrations 내부의 .py 파일을 삭제합니다..."
find ./ -type d -name "migrations" -exec find {} -type f -name "*.py" ! -name "__init__.py" -delete \;

# 모든 디렉토리에서 __pycache__ 삭제 (퍼미션 문제 해결)
echo "모든 하위 디렉토리에서 __pycache__ 삭제..."
find ./ -type d -name "__pycache__" -exec chmod -R 777 {} \; -exec rm -rf {} +

# 패키지 설치
echo "의존성을 다시 설정하는중..."
pip3 install -r requirements.txt

# makemigrations 실행. 모델은 app_core에 정의되어 있음
echo "마이그레이션을 다시 설정하는 중..."
python3 manage.py makemigrations
python3 manage.py makemigrations app_core


# migrate 실행
echo "마이그레이션을 적용하는 중..."
python3 manage.py migrate
python3 manage.py migrate app_core

echo "Django 프로젝트의 Migrations 초기화가 완료되었습니다! python3 manage.py runserver 명령어로 서버를 실행하세요. :)"
