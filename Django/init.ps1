# init.ps1 - Django 프로젝트 초기화 스크립트

Write-Host "Django 프로젝트의 Migrations 초기화를 시작합니다!" -ForegroundColor Green

# db.sqlite3 파일 삭제
$DB_FILE = "./db.sqlite3"
if (Test-Path $DB_FILE) {
    Write-Host "데이터베이스 파일을 찾았습니다. 삭제: $DB_FILE" -ForegroundColor Yellow
    Remove-Item $DB_FILE -Force
} else {
    Write-Host "데이터베이스 파일을 찾을 수 없습니다. : $DB_FILE" -ForegroundColor Red
}

# 모든 디렉토리에서 migrations 디렉토리 삭제
Write-Host "모든 하위 디렉토리에 마이그레이션이 있는지 검색 후 삭제..." -ForegroundColor Green
Get-ChildItem -Recurse -Directory -Filter "migrations" | ForEach-Object {
    Write-Host "삭제 중: $($_.FullName)" -ForegroundColor Yellow
    Remove-Item $_.FullName -Recurse -Force
}

# 모든 디렉토리에서 __pycache__ 디렉토리 삭제
Write-Host "모든 하위 디렉토리에 파이썬 캐시 파일이 있는지 검색 후 삭제..." -ForegroundColor Green
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
    Write-Host "삭제 중: $($_.FullName)" -ForegroundColor Yellow
    Remove-Item $_.FullName -Recurse -Force
}

# 패키지 설치
Write-Host "의존설을 다시 설정하는 중..." -ForegroundColor Green
pip install -r requirements.txt

# makemigrations 실행
Write-Host "마이그레이션을 다시 설정하는 중..." -ForegroundColor Green
$app_list = @("app_core", "app_api", "app_user", "app_partner", "app_supervisor", "app_post", "app_coupon", "app_message")
foreach ($app in $app_list) {
    Write-Host "마이그레이션 생성 중: $app" -ForegroundColor Yellow
    python manage.py makemigrations $app
}
python manage.py makemigrations

# migrate 실행
Write-Host "마이그레이션을 적용하는 중..." -ForegroundColor Green
foreach ($app in $app_list) {
    Write-Host "마이그레이션 적용 중: $app" -ForegroundColor Yellow
    python manage.py migrate $app
}
python manage.py migrate

Write-Host "Django 프로젝트의 Migrations 초기화가 완료되었습니다!" -ForegroundColor Green
Write-Host "python manage.py runserver 명령어로 서버를 실행하세요. :)" -ForegroundColor Green
