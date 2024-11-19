function initCopyFeature() {
    // Функция для показа уведомления
    function showCopyNotification() {
        const notification = $('#copy-notification');
        notification.css('display', 'block');  // Показываем уведомление
        notification.css('opacity', '1');  // Делаем его видимым

        // Через 1 секунду скрываем уведомление
        setTimeout(() => {
            notification.css('opacity', '0');  // Начинаем скрытие
            setTimeout(() => notification.css('display', 'none'), 300);  // Полностью убираем через 300 мс
        }, 1000);
    }

    // Обработчик клика для всех элементов с классом .copy
    $(document).on('click', '.copy', function() {
        const input = $(this).siblings('input')[0];

        if (input) {
            input.select();  // Выделяем текст
            input.setSelectionRange(0, 99999);  // Для мобильных устройств

            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showCopyNotification();  // Показываем уведомление при успешном копировании
                    console.log("Текст успешно скопирован:", input.value);
                } else {
                    console.error("Не удалось скопировать текст.");
                }
            } catch (err) {
                console.error("Ошибка при копировании текста:", err);
            }

            // Убираем выделение текста
            window.getSelection().removeAllRanges();
        }
    });
}

// Инициализация при загрузке страницы
$(document).ready(initCopyFeature);
