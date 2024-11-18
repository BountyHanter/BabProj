$(document).ready(function() {
    const modal = $('.modal_creating_report');
    const acknowledgeCheckbox = $('.modal_creating_report input[type="checkbox"]');
    const submitRequestButton = $('.modal_creating_report .btn_b');

    // Открытие модального окна по кнопке
    $('.creating_report_btn').on('click', function() {
        modal.css('display', 'flex'); // Показываем модальное окно
    });

    // Закрытие модального окна по кнопке "Закрыть"
    $('.modal_creating_report .close').on('click', function() {
        modal.css('display', 'none'); // Скрываем модальное окно
    });

    // Активация кнопки "Создать запрос" при установке галочки
    acknowledgeCheckbox.on('change', function() {
        if (acknowledgeCheckbox.prop('checked')) {
            submitRequestButton.css('opacity', '1');
            submitRequestButton.css('pointer-events', 'auto');
        } else {
            submitRequestButton.css('opacity', '0.5');
            submitRequestButton.css('pointer-events', 'none');
        }
    });

    // ** Новая часть кода для включения/отключения полей **

    // Функция для обработки изменений в чекбоксах
    $('.toggle-input').on('change', function() {
        const isChecked = $(this).prop('checked');
        const parentDiv = $(this).closest('div'); // Находим ближайший родительский <div>
        const relatedFields = parentDiv.find('.toggle-field'); // Находим связанные поля

        if (isChecked) {
            relatedFields.prop('disabled', false); // Включаем поля
        } else {
            relatedFields.prop('disabled', true); // Отключаем поля
        }
    });

    // Обработка отправки данных на сервер при нажатии на "Создать запрос"
    submitRequestButton.on('click', function(event) {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        if (!acknowledgeCheckbox.prop('checked')) return; // Проверяем, что чекбокс отмечен

        const formData = {};

        // Функция для добавления значения, если поле не пустое и чекбокс отмечен
        function addFieldIfCheckedAndNotEmpty(checkboxSelector, inputSelector, fieldName) {
            const checkbox = $(checkboxSelector);
            const input = $(inputSelector);

            if (checkbox.prop('checked') && input.val()) { // Только если чекбокс отмечен и поле заполнено
                formData[fieldName] = input.val();
            }
        }

        // Собираем данные формы
        addFieldIfCheckedAndNotEmpty('input[name="date_created_checkbox"]', 'input[name="date_created_from"]', 'date_created_from');
        addFieldIfCheckedAndNotEmpty('input[name="date_created_checkbox"]', 'input[name="date_created_to"]', 'date_created_to');
        addFieldIfCheckedAndNotEmpty('input[name="date_completed_checkbox"]', 'input[name="date_completed_from"]', 'date_completed_from');
        addFieldIfCheckedAndNotEmpty('input[name="date_completed_checkbox"]', 'input[name="date_completed_to"]', 'date_completed_to');
        addFieldIfCheckedAndNotEmpty('input[name="type_checkbox"]', 'select[name="type"]', 'type'); // Изменено с transaction_type_checkbox
        addFieldIfCheckedAndNotEmpty('input[name="status_checkbox"]', 'select[name="status"]', 'status');
        addFieldIfCheckedAndNotEmpty('input[name="from_bank_checkbox"]', 'select[name="from_bank"]', 'from_bank'); // Изменено с bank_sender_checkbox
        addFieldIfCheckedAndNotEmpty('input[name="to_bank_checkbox"]', 'select[name="to_bank"]', 'to_bank');   // Изменено с bank_receiver_checkbox
        addFieldIfCheckedAndNotEmpty('input[name="amount_from_checkbox"]', 'input[name="amount_from"]', 'amount_from');
        addFieldIfCheckedAndNotEmpty('input[name="amount_to_checkbox"]', 'input[name="amount_to"]', 'amount_to');

        const csrfToken = getCookie('csrftoken');

        // Выполняем AJAX-запрос
        $.ajax({
            url: reportUrl, // Используем URL, определенный в HTML
            type: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': csrfToken,  // Используем CSRF-токен из куки
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.file_url) {
                    window.location.href = response.file_url; // Перенаправляем на файл отчета
                } else {
                    alert("Ошибка создания отчета.");
                }
            },
            error: function(xhr, status, error) {
                console.error("Ошибка:", error);
                alert("Произошла ошибка при отправке отчета.");
            }
        });

        // Закрытие модального окна после отправки запроса
        modal.css('display', 'none');
    });
});
