base
HTML 템플릿의 기본 틀이 정의된 디렉토리입니다.

작성방법:
1. HTML 템플릿을 작성할 때, 기본적인 틀을 정의합니다. html 태그, head 태그, body 태그 등이 포함되어 있습니다.
2. 이 HTML을 상속받아 다른 HTML 템플릿을 사용하는 위치에는 {% block content %} {% endblock %}로 다른 HTML을 삽입할 수 있습니다.
3. 다른 HTML 템플릿에서는 {% extends 'base/파일명.html' %}로 상속받아 사용합니다.

기타 궁금한 내용이 있다면 라이브 커뮤니티에 질문해주세요. 감사합니다.
