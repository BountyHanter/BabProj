document.addEventListener("DOMContentLoaded", function () {
    const rowsPerPageSelect = document.querySelector("select[name='requests_value']");
    const filterButton = document.querySelector(".filter_btn"); // Кнопка "Фильтровать"
    const applyButton = document.querySelector(".requests_value a"); // Кнопка "Применить"
    const statusSelect = document.querySelector("#statusSelect");
    const dateFromInput = document.querySelector("#dateFrom"); // Поле "Дата от"
    const dateToInput = document.querySelector("#dateTo");     // Поле "Дата до"

    // Обработчик для кнопки "Фильтровать"
    filterButton.addEventListener("click", function () {
        const rowsPerPage = rowsPerPageSelect.value;
        const status = statusSelect ? statusSelect.value.toLowerCase() : ''; // Получаем выбранный статус
        const dateFrom = dateFromInput.value; // Получаем значение "Дата от"
        const dateTo = dateToInput.value;     // Получаем значение "Дата до"

        // Сбрасываем на первую страницу при фильтрации
        goToPage(1, rowsPerPage, status, dateFrom, dateTo);
    });

    // Обработчик для кнопки "Применить" (изменение количества строк на странице)
    applyButton.addEventListener("click", function () {
        const rowsPerPage = rowsPerPageSelect.value;
        const status = statusSelect ? statusSelect.value.toLowerCase() : ''; // Получаем выбранный статус
        const dateFrom = dateFromInput.value; // Получаем значение "Дата от"
        const dateTo = dateToInput.value;     // Получаем значение "Дата до"

        // Сбрасываем на первую страницу при изменении количества строк
        goToPage(1, rowsPerPage, status, dateFrom, dateTo);
    });
});

// Обновление таблицы заявок
function updateTable(applications) {
    const tableBody = document.querySelector(".requests_table table tbody");
    tableBody.innerHTML = "";

    applications.forEach(application => {
        const row = document.createElement("tr");
        const statusClass = getStatusClass(application.status);

        row.innerHTML = `
            <th scope="row">${application.id}</th>
            <td>${application.type}</td>
            <td>${application.amount}</td>
            <td>${application.payment_details}</td>
            <td>${application.to_bank}</td>
            <td>${application.from_bank || 'None'}</td>
            <td class="${statusClass}">${application.status_display}</td>
            <td>${application.created_at}</td>
            <td>${application.taken_time || 'None'}</td>
            <td>${application.completed_time || 'None'}</td>
            <td>${application.receipt_link ? `<a href="${application.receipt_link}" target="_blank">Скачать</a>` : 'None'}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Обновление пагинации
function updatePagination(totalPages, currentPage, rowsPerPage, status, dateFrom, dateTo) {
    const paginationContainer = document.querySelector(".pagin ul");
    paginationContainer.innerHTML = "";

    const maxPagesToShow = 5;
    const halfRange = Math.floor(maxPagesToShow / 2);
    let startPage = Math.max(currentPage - halfRange, 1);
    let endPage = Math.min(currentPage + halfRange, totalPages);

    if (currentPage <= halfRange) endPage = Math.min(maxPagesToShow, totalPages);
    if (currentPage > totalPages - halfRange) startPage = Math.max(totalPages - maxPagesToShow + 1, 1);

    // Кнопка "Первая страница"
    if (startPage > 1) {
        const firstPageItem = document.createElement("li");
        firstPageItem.textContent = "1";
        firstPageItem.classList.add("page-item");
        firstPageItem.addEventListener("click", (event) => {
            goToPage(1, rowsPerPage, status, dateFrom, dateTo);
        });
        paginationContainer.appendChild(firstPageItem);

        if (startPage > 2) {
            const dots = document.createElement("li");
            dots.textContent = "...";
            paginationContainer.appendChild(dots);
        }
    }

    // Диапазон страниц
    for (let i = startPage; i <= endPage; i++) {
        const pageItem = document.createElement("li");
        pageItem.className = i === currentPage ? "active" : "";
        pageItem.textContent = i;
        pageItem.addEventListener("click", (event) => {
            goToPage(i, rowsPerPage, status, dateFrom, dateTo);
        });
        paginationContainer.appendChild(pageItem);
    }

    // Кнопка "Последняя страница"
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement("li");
            dots.textContent = "...";
            paginationContainer.appendChild(dots);
        }

        const lastPageItem = document.createElement("li");
        lastPageItem.textContent = totalPages;
        lastPageItem.addEventListener("click", (event) => {
            goToPage(totalPages, rowsPerPage, status, dateFrom, dateTo);
        });
        paginationContainer.appendChild(lastPageItem);
    }
}



// Функция перехода на страницу
function goToPage(pageNumber, rowsPerPage, status, dateFrom = '', dateTo = '') {
    // Формируем URL с параметрами фильтрации
    const url = `/statistics/?page=${pageNumber}&rows_per_page=${rowsPerPage}&status=${status}&date_from=${dateFrom}&date_to=${dateTo}`;

    fetch(url, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        updateTable(data.applications); // Обновляем таблицу
        updatePagination(data.total_pages, data.current_page, rowsPerPage, status, dateFrom, dateTo); // Обновляем пагинацию
    })
    .catch(error => console.error("Ошибка:", error));
}

// Функция выбора CSS-класса для статуса
function getStatusClass(status) {
    switch (status) {
        case 'new': return 'new';
        case 'active': return 'active';
        case 'processing': return 'processing';
        case 'completed': return 'completed';
        case 'canceled': return 'canceled';
        case 'manual': return 'manual';
        default: return '';
    }
}
