const CalendarWidget = {
    today: new Date(),
    selectedDate: null,

    init: function () {
        const $calendarTable = document.querySelector("#calendar-table");
        this.today = new Date();
        this.DATE = new Date();
        this.WEEK = ["일", "월", "화", "수", "목", "금", "토"];
        this.MONTH = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"];

        this.$month = document.querySelector("#month");
        this.tbody = document.createElement("tbody");
        $calendarTable.append(this.tbody);

        /*
        const $prevButton = document.querySelector("#prev-button");
        $prevButton.addEventListener("click", this.handlePrevMonthClick.bind(this));
        const $nextButton = document.querySelector("#next-button");
        $nextButton.addEventListener("click", this.handleNextMonthClick.bind(this));
         */

        // Add event delegation to tbody for handling clicks on day cells
        // this.tbody.addEventListener("click", this.handleDateClick.bind(this));

        this.createCal();
    },

    // 달력 생성
    createCal: function () {
        this.$month.textContent = `${this.today.getFullYear()}년 ${this.MONTH[this.today.getMonth()]}월`;

        const firstDate = new Date(this.today.getFullYear(), this.today.getMonth(), 1);
        const lastDate = new Date(this.today.getFullYear(), this.today.getMonth() + 1, 0);

        while (this.tbody.rows.length > 0) {
            this.tbody.deleteRow(this.tbody.rows.length - 1);
        }

        let row = this.tbody.insertRow();
        let cell = "";
        let count = 0;

        // 달력의 첫째 주에 빈 칸을 채우기
        for (let i = 0; i < firstDate.getDay(); i++) {
            cell = row.insertCell();
            count++;
        }

        // 날짜 채우기
        for (let j = 1; j <= lastDate.getDate(); j++) {
            if (count % 7 === 0) {
                row = this.tbody.insertRow();
            }
            cell = row.insertCell();
            cell.textContent = j;
            cell.dataset.day = j; // Store the day in a data attribute for easy retrieval

            count++;
        }

        // Add event delegation to tbody for handling clicks on day cells
        // this.tbody.addEventListener("click", this.handleDateClick.bind(this));
    },

    handleDateClick: function (event) {
        // Check if the clicked element is a cell with a day
        if (event.target && event.target.nodeName === "TD" && event.target.dataset.day) {
            const selectedDay = event.target.dataset.day;
            const selectedDate = `${this.today.getFullYear()}-${this.MONTH[this.today.getMonth()]}-${selectedDay}`;
            console.log("Selected Date:", selectedDate);

            // 다른 on 지우기
            //Array.from(this.tbody.querySelectorAll("td")).forEach(cell => {
            //    cell.classList.remove("on");
            //});

            // 만약 이미 on 상태라면 해제
            //if (this.selectedDate && this.selectedDate === selectedDate) {
            //    event.target.classList.remove("on");
            //    this.selectedDate = null;
            //    return;
            //}

            // 방금 선택한 on 선택
            //event.target.classList.add("on");

            this.selectedDate = selectedDate;
        }
    },

    /*
    handleNextMonthClick: function () {
        this.today = new Date(this.today.getFullYear(), this.today.getMonth() + 1, this.today.getDate());
        this.createCal();
    },

    handlePrevMonthClick: function () {
        this.today = new Date(this.today.getFullYear(), this.today.getMonth() - 1, this.today.getDate());
        this.createCal();
    }
    */
};
