function updatePagination(totalPages, currentPage) {
    const paginationContainer = document.querySelector(".pagin ul");
    paginationContainer.innerHTML = ""; // Очистить текущую пагинацию

    const maxPagesToShow = 5;
    const halfRange = Math.floor(maxPagesToShow / 2);

    let startPage = Math.max(currentPage - halfRange, 1);
    let endPage = Math.min(currentPage + halfRange, totalPages);

    if (currentPage <= halfRange) {
        endPage = Math.min(maxPagesToShow, totalPages);
    }

    if (currentPage > totalPages - halfRange) {
        startPage = Math.max(totalPages - maxPagesToShow + 1, 1);
    }

    // Кнопка "Первая страница"
    if (startPage > 1) {
        const firstPageItem = document.createElement("li");
        firstPageItem.innerHTML = `<a href="#">1</a>`;
        firstPageItem.addEventListener("click", (event) => {
            event.preventDefault();
            goToPage(1);
        });
        paginationContainer.appendChild(firstPageItem);

        if (startPage > 2) {
            const dots = document.createElement("li");
            dots.innerHTML = `...`;
            paginationContainer.appendChild(dots);
        }
    }

    // Показать страницы в диапазоне
    for (let i = startPage; i <= endPage; i++) {
        const pageItem = document.createElement("li");
        pageItem.className = i === currentPage ? "active" : "";
        pageItem.innerHTML = `<a href="#">${i}</a>`;
        pageItem.addEventListener("click", (event) => {
            event.preventDefault();
            goToPage(i);
        });
        paginationContainer.appendChild(pageItem);
    }

    // Кнопка "Последняя страница"
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            const dots = document.createElement("li");
            dots.innerHTML = `...`;
            paginationContainer.appendChild(dots);
        }

        const lastPageItem = document.createElement("li");
        lastPageItem.innerHTML = `<a href="#">${totalPages}</a>`;
        lastPageItem.addEventListener("click", (event) => {
            event.preventDefault();
            goToPage(totalPages);
        });
        paginationContainer.appendChild(lastPageItem);
    }
}

// Функция перехода на указанную страницу
function goToPage(pageNumber) {
    const rowsPerPage = document.querySelector("select[name='requests_value']").value; // Получаем количество строк на страницу
    const status = document.querySelector("#statusSelect").value.toLowerCase(); // Получаем выбранный статус

    fetch(`/statistics/?page=${pageNumber}&rows_per_page=${rowsPerPage}&status=${status}`, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then(response => response.json())
    .then(data => {
        updateTable(data.applications); // Обновить таблицу с новыми данными
        updatePagination(data.total_pages, data.current_page); // Обновить пагинацию
    })
    .catch(error => console.error("Ошибка:", error));
}
