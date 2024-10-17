// timer.js

$(document).ready(function() {
    initTimer();
});

function parseDateTime(datetimeStr) {
    // datetimeStr: '2024-09-23T19:25:02+00:00'
    return new Date(datetimeStr);
}

function initTimer() {
    const timerContainer = document.getElementById('timer-container');
    const timerElement = document.getElementById('timer');

    // Если нет активной заявки или таймера, ничего не делаем
    if (!timerContainer || !timerElement) {
        return;
    }

    // Получаем taken_time из data-атрибута
    const takenTimeElement = document.querySelector('.taken-time');
    if (!takenTimeElement) {
        timerElement.textContent = 'N/A';
        return;
    }

    const takenTimeStr = takenTimeElement.getAttribute('data-taken-time');

    if (!takenTimeStr) {
        timerElement.textContent = 'N/A';
        return;
    }

    // Парсим taken_time
    const takenTime = parseDateTime(takenTimeStr);
    if (isNaN(takenTime.getTime())) {
        console.error('Invalid takenTime:', takenTimeStr);
        timerElement.textContent = 'N/A';
        return;
    }

    // Вычисляем end_time: taken_time + 30 минут
    const endTime = new Date(takenTime.getTime() + 30 * 60 * 1000);

    // Функция для обновления таймера
    function updateTimer() {
        const now = new Date(); // Текущее время клиента
        const remainingTime = endTime - now;

        if (remainingTime <= 0) {
            timerElement.textContent = '00:00';
            clearInterval(timerInterval);
            // Дополнительная логика при истечении времени (например, обновление статуса заявки)
            return;
        }

        const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

        // Форматируем минуты и секунды с ведущим нулём
        const formattedMinutes = minutes.toString().padStart(2, '0');
        const formattedSeconds = seconds.toString().padStart(2, '0');

        timerElement.textContent = `${formattedMinutes}:${formattedSeconds}`;
    }

    // Первоначальное обновление таймера
    updateTimer();

    // Обновляем таймер каждую секунду
    const timerInterval = setInterval(updateTimer, 1000);
}
