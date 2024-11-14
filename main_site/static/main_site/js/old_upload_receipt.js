$(document).ready(function() {
    // Обработчик отправки формы
    $('#receipt-form').on('submit', function(event) {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        // Создаем объект FormData для отправки файлов и других данных
        const formData = new FormData(this);

        // Показываем спиннер загрузки и отключаем кнопку отправки
        $('#loading-spinner').show();  // Показываем спиннер
        $('#upload-section').hide();   // Скрываем секцию загрузки
        $('#confirmation-btn').hide(); // Скрываем кнопку подтверждения
        $('#problem-btn').hide(); // Скрываем кнопку подтверждения


        // Выполняем AJAX запрос
        $.ajax({
            url: $(this).attr('action'), // URL для отправки данных (из атрибута action формы)
            type: 'POST',
            data: formData,
            processData: false, // Не обрабатываем данные
            contentType: false, // Не устанавливаем заголовок content-type
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Добавляем CSRF-токен
            },
            success: function(response) {
                // Если успешный ответ
                if (response.status === "success") {
                    // Обновляем информацию о заявке в таблице
                    const activeRow = $('#active-application-table tbody tr');
                    activeRow.find('td:nth-child(4)').text(response.bank_name); // Обновляем название банка
                    activeRow.find('td:nth-child(5)').text('processing'); // Обновляем статус

                    updatePageData('Чек успешно загружен и отправлен на проверку.', 'success');
                } else {
                    // Если статус не success, отображаем ошибку
                    showNotification('Произошла ошибка при отправке, перезагрузите страницу', 'danger');
                    showNotification(response.error, 'danger');
                    $('#upload-section').show();   // Показываем секцию загрузки
                    $('#confirmation-btn').show(); // Показываем кнопку подтверждения

                    // Скрываем спиннер
                    $('#loading-spinner').hide();
                }
            },
            error: function(xhr) {
                // Парсим ответ от сервера
                let errorMessage = 'Произошла ошибка при загрузке чека. Перезагрузите страницу';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }

                // Отображаем уведомление об ошибке
                showNotification(errorMessage, 'danger');
                $('#upload-section').show();   // Показываем секцию загрузки

                // Скрываем спиннер при ошибке
                $('#loading-spinner').hide();
            }
        });

    });

    // Обработчик отображения имени выбранного файла
    $('.custom-file-input').on('change', function() {
        let fileName = $(this).val().split('\\').pop();
        $(this).next('.custom-file-label').addClass("selected").html(fileName);
    });
});
