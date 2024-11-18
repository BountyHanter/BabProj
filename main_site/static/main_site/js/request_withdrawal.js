// Открытие модального окна
function openModal() {
    document.querySelector('.modal_request_withdrawal').style.display = 'block';
}

// Закрытие модального окна
function closeModal() {
    document.querySelector('.modal_request_withdrawal').style.display = 'none';
}

// Отправка запроса на вывод
function submitWithdrawalRequest() {
    const amountInput = document.getElementById("withdrawal-amount");
    const errorMessage = document.getElementById("error-message");
    const amount = parseFloat(amountInput.value);

    // Проверка на минимальную сумму
    if (isNaN(amount) || amount < 100) {
        errorMessage.style.display = 'block';
        return;
    } else {
        errorMessage.style.display = 'none';
    }

    // Отправка запроса на сервер
    fetch(WithdrawalRequestUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),  // CSRF-токен
        },
        body: JSON.stringify({ amount: amount })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage("Запрос на вывод успешно создан", 'success');
            closeModal();
            // Перезагрузка страницы через 5 секунд
            setTimeout(function() {
                location.reload();
            }, 2000);
        } else {
            showMessage("Ошибка: " + data.message, 'error');
        }
    })
    .catch(error => {
        showMessage("Ошибка при отправке запроса: " + error, 'error');
    });
}