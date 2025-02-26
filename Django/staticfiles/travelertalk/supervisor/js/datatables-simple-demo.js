window.addEventListener("DOMContentLoaded", (event) => {
  // 모든 datatablesSimple 클래스를 가진 테이블 초기화
  // 반드시 id 따로 설정해줘야 에러 안난다
  const datatables = document.querySelectorAll(".datatablesSimple");
  datatables.forEach((datatable) => {
    new simpleDatatables.DataTable(datatable);
  });
});
