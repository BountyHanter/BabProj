$(document).ready(function() {
    // Делегирование события клика на документ для кнопки "Подтвердить"
    $(document).on('click', '#confirmation-btn', function(event) {
        event.preventDefault(); // Предотвращаем стандартное поведение кнопки

        const applicationId = $('#application-id').text(); // Получаем ID заявки из модального окна
        const csrfToken = getCookie('csrftoken'); // Получаем CSRF-токен из cookies

        // Создаем объект FormData для отправки данных в формате POST
        const formData = new FormData();
        formData.append('application_id', applicationId); // Добавляем ID заявки

        // Отправляем AJAX-запрос на подтверждение заявки
        fetch(confirmApplicationsUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Сохранить уведомление в sessionStorage перед перезагрузкой
                sessionStorage.setItem('notification', JSON.stringify({
                    message: 'Заявка подтверждена',
                    type: 'success'
                }));

                // Перезагрузить страницу
                location.reload();
            } else {
                // Ошибка подтверждения
                showNotification(data.error || `Ошибка при подтверждении заявки ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке запроса:', error);
            showNotification('Произошла ошибка при подтверждении заявки. Попробуйте перезагрузить страницу', 'danger');
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