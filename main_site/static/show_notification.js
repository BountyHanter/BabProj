// Функция для отображения уведомлений
function showNotification(message, type) {
    const alertDiv = $('<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
        message +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Закрыть">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button>' +
        '</div>');

    $('#notification-container').append(alertDiv);

    // Автоматически закрыть уведомление через 10 секунд
    setTimeout(function() {
        alertDiv.alert('close');
    }, 10000);
}