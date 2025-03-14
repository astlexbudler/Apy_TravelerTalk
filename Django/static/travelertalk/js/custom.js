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
      <div class="text-center">
        <p class="text-black-50">
          ${message}
        </p>
      </div>
    </div>`,
    icon: icon,
    showConfirmButton: true,
    confirmButtonText: `확인`,
    showCancelButton: false,
    cancelButtonText: ``,
    customClass: {
      confirmButton: 'custom-swal-confirm-btn' // 커스텀 클래스 적용
    }
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
      <div class="text-center">
        <p class="text-black-50">
          ${message}
        </p>
      </div>
    </div>`,
    icon: icon,
    showConfirmButton: true,
    confirmButtonText: confirmButtonText,
    showCancelButton: true,
    cancelButtonText: cancelButtonText,
    customClass: {
      confirmButton: 'custom-swal-confirm-btn-half', // 커스텀 클래스 적용
      cancelButton: 'custom-swal-cancel-btn-half' // 커스텀 클래스 적용
    },
  })
  .then((result) => {
    return result.isConfirmed; // 확인 버튼을 눌렀을 때 true 반환
  });
}

// 로그인 버튼 클릭 시 로그인 시도
tryLogin = async (form) => {

  const formData = new FormData(form);

  // 아이디 또는 비밀번호가 비어있는 경우
  if (formData.get('id') === '' || formData.get('password') === '') {
    await showAlert('로그인 실패', '아이디 또는 비밀번호를 입력해주세요.', 'error');
    return;
  }

  // 로그인 시도
  var data = await fetch('/api/login', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: formData
  })
  .then((response) => response.json())
  .then(async (data) => {
    console.log(data); // fetch 요청 결과 출력
    return data;
  });

  // 로그인 결과에 따른 분기 처리
  if (data.success) { // 로그인 성공
    if (data.data == 'active') {
      await showAlert('로그인 성공', '로그인에 성공했습니다. 메인 페이지로 이동합니다.', 'success');
      location.href = '/'; // 메인 페이지로 이동
      return;
    } else if (data.data == 'pending') {
      await showAlert('계정 확인중', '아직 계정 승인 대기 중입니다. 확인이 완료될 때까지 일부 기능이 제한됩니다.', 'warning');
      location.reload();
      return;
    } else if (data.data == 'block') {
      await showAlert('계정 정지', '활동이 정지된 계정입니다. 관리자에게 문의하세요.', 'error');
      location.reload();
      return;
    }
  }

  // 로그인 실패
  await showAlert('로그인 실패', '아이디 또는 비밀번호가 일치하지 않습니다.', 'error');
  form.reset(); // 입력창 초기화
  return;
}

// 로그아웃 버튼 클릭 시
logout = async () => {
  await fetch('/api/logout'); // 로그아웃 요청

  // 로그아웃 메세지 출럭
  await showAlert('로그아웃 완료', '로그아웃되었습니다. 메인 페이지로 이동합니다.', 'success');
  location.href = '/'; // 메인 페이지로 이동.
  return;
}

// 검색바 검색 버튼 클릭 시
searchPost = async () => {
  // 현재 게시판 정보 확인
  var pcSearchKeyword = document.getElementById('pcSearchKeyword').value; // 검색어 가져오기 2 (모바일 검색바)
  location.href = `/?search=${pcSearchKeyword}`;
}

// 게시판 내 검색바 검색 버튼 클릭 시
searchBoard = async (board_ids) => {
  console.log(board_ids);
  // 현재 게시판 정보 확인
  var searchInputValue = document.getElementById('searchInput').value; // 검색어 가져오기 1
  location.href = `/post?search=${searchInputValue}&board_ids=${board_ids}`;
}

needLogin = () => {
  showAlert('로그인 필요', '로그인이 필요한 서비스입니다.', 'warning');
}

openExportDataPage = () => {
  nowUrl = window.location.href;
  if (nowUrl.indexOf('?') > -1) {
    nowUrl = nowUrl + '&export=y';
  } else {
    nowUrl = nowUrl + '?export=y';
  }
  window.open(nowUrl, '_blank');
}

scrollToComment = () => {
  commentUl = document.getElementById('commentUl');
  commentUly = commentUl.getBoundingClientRect().top;
  window.scrollTo({'top': commentUly, 'behavior': 'smooth'});
}

// copy to clipboard
function copyToClipboard(text) {
  //navigator.clipboard.writeText('{{coupon.code}}'); showAlert('클립보드 복사', '쿠폰 코드가 복사되었습니다.', 'success');
  navigator.clipboard.writeText(text);
  showAlert('클립보드 복사', '쿠폰 코드가 복사되었습니다.', 'success');
}