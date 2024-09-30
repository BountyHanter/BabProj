// show_modal.js

$(document).ready(function() {
    // Делегированный обработчик клика для строк активных заявок
    $(document).on('click', '.active-application', function (event) {
        // Проверяем, не был ли клик по интерактивному элементу внутри строки (например, кнопке)
        if ($(event.target).closest('button, a, input, select, textarea').length === 0) {
            $('#receiptModal').modal('show');
        }
    });

    // Обработчик закрытия модального окна
    $('#receiptModal').on('hidden.bs.modal', function () {
        // Сброс выбранного банка
        $('#bank-select').val(null).trigger('change');

        // Очистка поля загрузки файла
        $('#receipt-file').val('');

        // Обновление метки выбранного файла (Select2 уже инициализирован в show_banks.js)
        $('.custom-file-label').removeClass("selected").html('Выберите файл');
    });
});
