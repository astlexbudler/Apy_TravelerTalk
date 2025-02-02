// csrftoken 가져오기
getCookie = (name) => {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken'); // 이걸 사용해서 fetch 요청 시 header에 넣어줘야 함

// 현재 시간 문자열 반환
getNowDatetimeString = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  const date = now.getDate();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const second = now.getSeconds();
  return `${year}-${month}-${date} ${hour}:${minute}:${second}`;
}

// 타임스탬프 생성
function getTimestamp() {
  return new Date().getTime();
}

// 파일 업로드
async function uploadFile(file) {
  var formData = new FormData();
  formData.append('file', file)
  var path = await fetch('/api/upload', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formData
  })
  .then((response) => response.json())
  .then((data) => {
    return data["path"];
  });
  console.log('파일을 업로드했습니다. 업로드된 파일의 경로: ' + path);
  return path
}

// SweetAlert2 알림창 사전 정의
showAlert = async(title, message, icon) => {
  await Swal.fire({
    html: `
    <div>
      <div class="text-center py-4">
        <h1 class="text-dark">${title}</h1>
      </div>
      <div class="text-start">
        <p class="text-black-50">
          ${message}
        </p>
      </div>
    </div>`,
    icon: icon,
    showConfirmButton: true,
    confirmButtonText: `확인`,
    showCancelButton: false,
    cancelButtonText: ``
  });
}

// SweetAlert2 확인창 사전 정의(isConfirm: true/false)
showConfirm = async(title, message, icon, confirmButtonText, cancelButtonText) => {
  return await Swal.fire({
    html: `
    <div>
      <div class="text-center py-4">
        <h1 class="text-dark">${title}</h1>
      </div>
      <div class="text-start">
        <p class="text-black-50">
          ${message}
        </p>
      </div>
    </div>`,
    icon: icon,
    showConfirmButton: true,
    confirmButtonText: confirmButtonText,
    showCancelButton: true,
    cancelButtonText: cancelButtonText
  })
  .then((result) => {
    return result.isConfirmed; // 확인 버튼을 눌렀을 때 true 반환
  });
}

// 로그인 버튼 클릭 시 로그인 시도
tryLogin = async () => {

  // 로그인 폼이 2개로 나뉘어져 있으므로, 각각의 값을 가져옴
  var loginId = '';
  document.querySelectorAll('.accountLoginId').forEach(element => {
    if (element.value !== '') { // 값이 비어있지 않은 경우에만 값을 가져옴
      loginId = element.value;
    }
  });
  var loginPassword = '';
  document.querySelectorAll('.accountLoginPassword').forEach(element => {
    if (element.value !== '') { // 값이 비어있지 않은 경우에만 값을 가져옴
      loginPassword = element.value;
    }
  });

  // 아이디 또는 비밀번호가 비어있는 경우
  if (loginId === '' || loginPassword === '') {
    await showAlert('로그인 실패', '아이디 또는 비밀번호를 입력해주세요.', 'error');
    return;
  }

  // 로그인 시도
  var formdata = new FormData();
  formdata.append('id', loginId);
  formdata.append('password', loginPassword);
  var result = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formdata
  })
  .then((response) => response.json())
  .then(async (data) => {
    console.log(data); // fetch 요청 결과 출력
    return data.result;
  });

  // 로그인 결과에 따른 분기 처리
  if (result === 'success') { // 로그인 성공
    location.reload();
    return;
  } else if (result.indexOf('pending') != -1) {
    // 심사 대기중 안내 및 로그인 성공
    await showAlert('계정 확인중', '아직 계정 승인 대기 중입니다. 확인이 완료될 때까지 일부 기능이 제한됩니다.', 'warning');
    location.reload();
    return;
  } else if (result.indexOf('banned') != -1) {
    // 계정 정지 안내 및 로그인 실패
    await showAlert('계정 정지', '활동이 정지된 계정입니다. 관리자에게 문의하세요.', 'error');
    document.querySelectorAll('.accountLoginId').forEach(element => {
      element.value = '';
    });
    document.querySelectorAll('.accountLoginPassword').forEach(element => {
      element.value = '';
    });
    return;
  }

  // 로그인 실패
  await showAlert('로그인 실패', '아이디 또는 비밀번호가 일치하지 않습니다.', 'error');
  document.querySelectorAll('.accountLoginId').forEach(element => {
    element.value = '';
  });
  document.querySelectorAll('.accountLoginPassword').forEach(element => {
    element.value = '';
  });
}

// 로그아웃 버튼 클릭 시
logout = async () => {
  await fetch('/api/logout'); // 로그아웃 요청

  // 로그아웃 메세지 출럭
  await showAlert('로그아웃 완료', '로그아웃되었습니다. 메인 페이지로 이동합니다.', 'success');
  location.href = '/'; // 메인 페이지로 이동
  return;
}

// 검색바 검색 버튼 클릭 시
searchPost = async () => {
  // 현재 게시판 정보 확인
  var board_ids = '{{ request.GET.board_ids }}';
  var mobileSearchKeyword = document.getElementById('mobileSearchKeyword').value; // 검색어 가져오기 1
  var pcSearchKeyword = document.getElementById('pcSearchKeyword').value; // 검색어 가져오기 2 (모바일 검색바)
  location.href = `/post?board_ids=${board_ids}&search=${mobileSearchKeyword + pcSearchKeyword}`;
  return;
}

// 댓글 삭제 함수
deleteComment = async (comment_id) => {
  // 댓글 삭제 확인
  var isConfirmed = await showConfirm('댓글 삭제', '정말로 댓글을 삭제하시겠습니까?', 'warning', '삭제', '취소');
  if (!isConfirmed) {
    return;
  }

  // 댓글 삭제 요청
  var formdata = new FormData();
  formdata.append('comment_id', comment_id);
  var result = await fetch('/api/delete_comment', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formdata
  })
  .then((response) => response.json())
  .then(async (data) => {
    console.log(data); // fetch 요청 결과 출력
    return data.result;
  });

  // 댓글 삭제 결과에 따른 분기 처리
  if (result === 'success') { // 댓글 삭제 성공
    await showAlert('삭제 성공', '댓글 삭제가 완료되었습니다.', 'success');
    location.reload();
    return;
  } else {
    await showAlert('삭제 실패', '댓글 삭제 권한이 없습니다.', 'error');
    return;
  }
}

// 댓글 작성 함수
writeComment = async (post_id, content) => {

  // 사용자 확인. 로그인 여부만 확인
  // 그 외 권한이나 계정 상태는 서버에서 확인
  var account_type = '{{ request.account.account_type }}';
  if (account_type == 'guest') {
    await showAlert('작성 실패', '댓글 작성을 위해 로그인이 필요합니다.', 'error');
    return;
  }

  // 댓글 내용 확인
  if (content === '') {
    await showAlert('작성 실패', '댓글 내용을 입력해주세요.', 'error');
    return;
  }

  // 댓글 작성 요청
  var formdata = new FormData();
  formdata.append('post_id', post_id);
  formdata.append('content', content);
  var result = await fetch('/api/write_comment', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formdata
  })
  .then((response) => response.json())
  .then(async (data) => {
    console.log(data); // fetch 요청 결과 출력
    return data.result;
  });

  // 댓글 작성 결과에 따른 분기 처리
  if (result === 'success') { // 댓글 작성 성공
    await showAlert('작성 성공', '댓글 작성이 완료되었습니다.', 'success');
    location.reload();
    return;
  } else {
    await showAlert('작성 실패', '댓글을 작성할 수 없는 게시글이거나, 댓글 작성 권한이 없습니다.', 'error');
    return;
  }
}

// 페이지 버튼 생성(pagenation)
// 페이지네이션이 필요한 페이지에서 사용
makePaegeButton = (page, lastPage, url) => {
  if(page == '') {
    page = 1;
  } else {
    page = parseInt(page);
  }
  nowPage = page;
  lastPage = parseInt(lastPage);

  pageButtonsBox = document.getElementById('pageButton');
  html = '';
  pages = [
    page - 2,
    page - 1,
    page,
    page + 1,
    page + 2
  ];
  html += '<ul class="pagination mt-6 justify-content-center">';
  if (pages[0] > 1) {
    html += `<li class="page-item">
      <a class="page-link" href="${url}&page=1">처음</a>
    </li>`;
  }
  for (var i = 0; i < pages.length; i++) {
    page = pages[i];
    if (page < 1 || page > lastPage) {
      continue;
    } else if (nowPage == page) {
      html += `<li class="page-item active">
        <a class="page-link" href="#">${page}</a>
      </li>`;
    } else {
      html += `<li class="page-item">
        <a class="page-link" href="${url}&page=${page}">${page}</a>
      </li>`;
    }
  }
  if (page < lastPage) {
    html += `<li class="page-item">
      <a class="page-link" href="${url}&page=${lastPage}">마지막</a>
    </li>`;
  }
  html += '</ul>';

  pageButtonsBox.innerHTML = html;
}

needLogin = () => {
  showAlert('로그인 필요', '로그인이 필요한 서비스입니다.', 'warning');
}