function openModal() {
    // Получаем ID заявки из скрытого поля
    const applicationId = document.getElementById('application_id').value;

    // Обновляем содержимое заголовка в модальном окне
    const modalTitle = document.querySelector('.modal_title');
    modalTitle.textContent = `Сообщите о проблеме для заявки ID: ${applicationId}`;

    document.getElementById('problemModal').classList.add('show');
}

function closeModal() {
    document.getElementById('problemModal').classList.remove('show');
}

function reportProblem() {
    // Получаем ID заявки из скрытого поля
    const applicationId = document.getElementById('application_id').value;

    // Получаем выбранную проблему из селектора
    const problem = document.getElementById('problemSelect').value;

    // Получаем CSRF-токен из cookie
    const csrfToken = getCookie('csrftoken');

    // Проверка, что выбрана проблема
    if (!problem) {
        alert("Пожалуйста, выберите описание проблемы.");
        return;
    }

    // Используем FormData для создания данных запроса
    const formData = new FormData();
    formData.append('application_id', applicationId);
    formData.append('problem', problem);

    // Выполняем AJAX-запрос
    $.ajax({
        url: reportProblemUrl, // URL для отправки проблемы
        type: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        data: formData,
        processData: false, // Отключаем обработку данных, чтобы передавать FormData как есть
        contentType: false, // Отключаем установку Content-Type, он будет установлен автоматически
        success: function(response) {
            if (response.status === "success") {
                showMessage("Проблема успешно зафиксирована.", 'success');
                closeModal(); // Закрываем модальное окно
            } else if (response.error) {
                showMessage("Ошибка: " + response.error, 'error');
            } else {
                showMessage("Подробности не доступны", 'error');
            }
        },
        error: function(xhr, status, error) {
            showMessage("Произошла ошибка: " + error, 'error');
        }
    });
}
