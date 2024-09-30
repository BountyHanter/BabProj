$(document).ready(function() {
    // Обработчик отправки формы вывода средств
    $('#withdrawalForm').on('submit', function(event) {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val(); // Получаем CSRF-токен
        const amount = $('#amount').val(); // Получаем введённую сумму

        // Валидация суммы на стороне клиента
        if (amount.trim() === '' || isNaN(amount) || Number(amount) <= 0) {
            showNotification('Пожалуйста, введите корректную сумму.', 'warning');
            return;
        }

        // Отправляем AJAX-запрос для создания заявки на вывод средств
        $.ajax({
            url: $(this).attr('action'), // Используем URL из атрибута action формы
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
                // 'X-Requested-With' автоматически добавляется jQuery как 'XMLHttpRequest'
            },
            data: {
                'amount': amount // Передаём введённую сумму в запросе
            },
            success: function(response) {
                if (response.success) {
                    // Сохраняем уведомление в sessionStorage перед перезагрузкой страницы
                    sessionStorage.setItem('notification', JSON.stringify({
                        message: response.message || 'Запрос на вывод средств успешно создан',
                        type: 'success'
                    }));

                    // Закрываем модальное окно
                    $('#withdrawalModal').modal('hide');
                    alert('Запрос на вывод средств успешно создан')

                    // Перезагружаем страницу для обновления данных
                    location.reload();
                } else {
                    // Если произошла ошибка, показываем уведомление с ошибкой из ответа
                    showNotification(response.message || 'Произошла ошибка при создании запроса', 'danger');
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при создании запроса на вывод средств:', error);
                let errorMessage = 'Не удалось создать запрос на вывод средств. Попробуйте позже.';

                // Попытка извлечь сообщение об ошибке из ответа сервера
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    errorMessage = xhr.responseJSON.message;
                }

                showNotification(errorMessage, 'danger');
            }
        });
    });
});
