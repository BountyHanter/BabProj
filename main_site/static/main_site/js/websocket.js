const socket = socketDomain;
console.log(socketDomain)

socket.onopen = function(event) {
    console.log('WebSocket connection established.');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data);

    if (data.action === 'active') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Вызываем функцию для обновления данных на клиенте
        fetchActiveApplication('Заявка взята', 'success');
    } else if (data.action === 'completed') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        fetchActiveApplication('Заявка обработана', 'success');
    } else if (data.action === 'canceled') {
        console.log(`Заявка с ID ${data.application_id} отменена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        fetchActiveApplication('Заявка отклонена', 'error');
    } else if (data.action === 'processing') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        fetchActiveApplication('Заявка в процессе', 'success');
    } else if (data.action === 'manual') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        fetchActiveApplication('Заявка взята в исполнение Администрацией', 'error');
    } else if (data.action === 'new') {
        console.log(`Заявка с ID ${data.application_id} обновлена.`);
        // Здесь вы можете добавить любую логику, например, обновление страницы
        fetchActiveApplication('Вас убрали с исполнения заявки', 'error');
    }
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed.');
    showMessage('Потеряно соединение с сервером, перезагрузите страницу', 'error')
};

socket.onerror = function(event) {
    console.error('WebSocket error observed:', event);
    showMessage('Произошла ошибка, перезагрузите страницу', 'error')
};
