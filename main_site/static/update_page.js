$(document).ready(function() {
    // Делегирование события клика на документ для кнопки "Взять заявку"
    $(document).on('click', '#take-application-btn', function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение кнопки

        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val(); // Получаем CSRF-токен

        // Отправляем AJAX-запрос для взятия заявки
        $.ajax({
            url: takeApplicationUrl,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: JSON.stringify({}), // Передаём пустой объект или необходимые данные
            contentType: 'application/json',
            success: function(response) {
                if (response.status === "success") {
                    // Сохранить уведомление в sessionStorage перед перезагрузкой
                    sessionStorage.setItem('notification', JSON.stringify({
                        message: response.message || 'Заявка взята',
                        type: 'success'
                    }));

                    // Перезагрузить страницу
                    location.reload();
                } else if (response.error) {
                    // Если произошла ошибка, показываем уведомление с ошибкой из ответа
                    showNotification(response.error, "danger");
                } else {
                    // Показываем общее сообщение об ошибке, если ошибка не передана
                    showNotification("Произошла ошибка при взятии заявки", "danger");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка при взятии заявки:", error);
                let errorMessage = "Не удалось взять заявку. Попробуйте перезагрузить страницу.";

                // Попытка извлечь сообщение об ошибке из ответа сервера
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }

                showNotification(errorMessage, "danger");
            }
        });
    });

    // Проверка и отображение уведомления после перезагрузки страницы
    const notification = sessionStorage.getItem('notification');
    if (notification) {
        const { message, type } = JSON.parse(notification);
        showNotification(message, type);
        sessionStorage.removeItem('notification');
    }
});

// Функция для обновления данных страницы
function updatePageData(notification, type_notification, modal) {
    fetch(userApplicationsUrl)
    .then(response => response.text())
    .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Обновляем контейнер с активной заявкой
        const activeApplicationContent = doc.querySelector('#active-application-section');
        if (activeApplicationContent) {
            document.querySelector('#active-application-section').innerHTML = activeApplicationContent.innerHTML;
        }

        // Показ уведомления, если оно нужно
        if (notification) {
            showNotification(notification, type_notification);
        }

        // Повторная инициализация Select2 после обновления
        $('.select2').select2({
            theme: 'bootstrap4',
            width: '100%'
        });

        // Таймер
        initTimer();

        // Заново инициализируем CSRF-токен, если он обновился
        const newCsrfToken = getCookie('csrftoken');
        console.log("Новый CSRF-токен:", newCsrfToken);
    })
    .catch(error => {
        showNotification('Произошла ошибка, перезагрузите страницу', 'error')
        console.error("Ошибка обновления страницы:", error);
    });
}

// Функция для повторной инициализации Select2 и заполнения банков после обновления страницы
function populateBanksSelect(banksToShow) {
    const bankSelect = $('#bank-select');
    bankSelect.empty();  // Очищаем список перед добавлением новых значений

    // Добавляем placeholder как пустой элемент
    const placeholderOption = new Option('', '', false, false);
    bankSelect.append(placeholderOption);

    // Проходим по массиву банков и добавляем каждый банк в список
    banksToShow.forEach(function(bank) {
        const newOption = new Option(bank.name, bank.id, false, false);
        bankSelect.append(newOption);
    });

    // Переинициализация Select2
    $('#bank-select').select2({
        placeholder: 'Выберите банк',
        allowClear: true
    });
}


// Функция для закрытия модального окна
function closeModal() {
    const modalElement = document.getElementById('receiptModal');
    if (modalElement) {
        // Если используете Bootstrap 4 с jQuery
        $('#receiptModal').modal('hide');

    }
}