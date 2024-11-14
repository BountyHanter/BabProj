$(document).ready(function() {
    const activeApplicationUrl = '/active_application/';  // Используем URL для AJAX-запросов
    // Делегирование события клика на кнопку "Взять заявку"
    $(document).on('click', '#take-application-btn', function(event) {
        event.preventDefault();

        const csrfToken = getCookie('csrftoken');

        // Отправляем AJAX-запрос для взятия заявки
        $.ajax({
            url: takeApplicationUrl, // URL, по которому принимается заявка
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            contentType: 'application/json',
            success: function(response) {
                if (response.status === "success") {
                    console.log('Заявка взята')
                } else if (response.error) {
                    showMessage(response.error, 'error');
                } else {
                    showMessage('Подробности не доступны', 'error');
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка при взятии заявки:", error);
                let errorMessage = "Не удалось взять заявку. Попробуйте перезагрузить страницу. (Подробности в консоли)";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                    showMessage(errorMessage, 'error')
                }
                else if (errorMessage === "Нет новых заявок") {
                    showMessage('Нет новых заявок', 'error')
                }
                else {
                    showMessage(errorMessage, 'error');
                }
            }
        });
    });
    // Функция для подгрузки активной заявки и обновления DOM
    window.fetchActiveApplication = function(message, type) {
        $.ajax({
            url: activeApplicationUrl, // URL для `active_application_view`, который рендерит частичный шаблон
            type: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: function(response) {
                // Обновляем содержимое контейнера с активной заявкой
                $('#application-container').html(response);
                console.log(message, type)
                // showMessage(message, type);
                // Повторно запускаем таймер после обновления содержимого
                initTimer();
                initUploadFeature();
                initCopyFeature();

                // Привязка события к кнопке подтверждения
                $('.send_confirm_btn').on('click', function() {
                    const applicationId = $('#application_id').val();
                    confirmApplication(applicationId); // Вызов confirmApplication
                });
            },
            error: function(xhr, status, error) {
                console.error("Ошибка при загрузке активной заявки:", error);
            }
        });
    }
});
