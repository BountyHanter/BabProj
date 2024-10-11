const socket = socketDomain;
console.log(socketDomain)

socket.onopen = function(event) {
    console.log('WebSocket connection established.');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data);

    if (data.action === 'update') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Вызываем функцию для обновления данных на клиенте
        updatePageData('Заявка принята', 'success');
    } else if (data.action === 'cancel') {
        console.log(`Заявка с ID ${data.application_id} отменена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        updatePageData('Заявка отклонена', 'danger', 1);
    }
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed.');
    showNotification('Произошла ошибка, перезагрузите страницу', 'danger')
};

socket.onerror = function(event) {
    console.error('WebSocket error observed:', event);
    showNotification('Произошла ошибка, перезагрузите страницу', 'danger')
};
