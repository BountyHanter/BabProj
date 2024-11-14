// Функция подтверждения заявки
function confirmApplication(applicationId) {
    if (!applicationId) {
        showMessage('ID заявки не найден', 'error');
        return;
    }

    const formData = new FormData();
    formData.append("application_id", applicationId);

    fetch(confirmApplicationsUrl, {
        method: "POST",
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Заявка успешно подтверждена');
        } else {
            showMessage(data.error || 'Ошибка при подтверждении заявки', 'error');
        }
    })
    .catch(error => {
        console.error("Ошибка:", error);
        showMessage(error, 'error');
    });
}

// Пример вызова функции при нажатии кнопки
document.addEventListener("DOMContentLoaded", function() {
    const confirmButton = document.querySelector(".send_confirm_btn");

    confirmButton.addEventListener("click", function(event) {
        event.preventDefault();
        const applicationId = document.getElementById("application_id").value;
        confirmApplication(applicationId); // Вызываем функцию с ID заявки
    });
});