$(document).ready(function() {
    // Делегирование события клика для кнопки "Проблема с оплатой"
    $(document).on('click', '#report-problem-btn', function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение кнопки

        // Закрываем текущее модальное окно
        $('#receiptModal').modal('hide');

        // Получаем ID текущей заявки
        const applicationId = $('#application-id').text();

        // Устанавливаем ID заявки в новое модальное окно
        $('#problem-application-id').text(applicationId);
        $('#problem-application-id-input').val(applicationId);

        // Открываем новое модальное окно
        $('#problemModal').modal('show');
    });

    // Обработка отправки формы с проблемой
    $('#problem-form').on('submit', function(event) {
        event.preventDefault(); // Останавливаем стандартную отправку формы

        const formData = new FormData(this); // Собираем данные формы

        // Выполняем AJAX запрос
        $.ajax({
            url: reportProblemUrl, // URL для отправки данных (из атрибута action формы)
            type: 'POST',
            data: formData,
            processData: false, // Не обрабатываем данные
            contentType: false, // Не устанавливаем заголовок content-type
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Добавляем CSRF-токен
            },
            success: function(response) {
                if (response.status === "success") {
                    updatePageData(response.message, 'warning');

                    // Закрываем модальное окно после успешной отправки
                    $('#problemModal').modal('hide');
                } else if (response.error) {
                    // Если произошла ошибка, показываем уведомление с ошибкой из ответа
                    showNotification(response.error, "danger");
                } else {
                    // Показываем общее сообщение об ошибке, если ошибка не передана
                    showNotification("Произошла ошибка при отправке проблемы", "danger");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка при отправке проблемы:", error);
                let errorMessage = "Не удалось отправить проблему. Попробуйте перезагрузить страницу.";

                // Попытка извлечь сообщение об ошибке из ответа сервера
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }

                showNotification(errorMessage, "danger");
            }
        });
    });

});
