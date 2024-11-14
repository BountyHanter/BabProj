function initUploadFeature() {
    const dropZone = document.querySelector(".upload_zone_dragover");
    const uploadInput = document.querySelector("#uploadForm_File");
    const sendButton = document.querySelector(".send_check_btn");
    let selectedFile = null;

    // Если элементы отсутствуют (при первом рендере или после обновления), выходим из функции
    if (!dropZone || !uploadInput || !sendButton) {
        return;
    }

    // Обработчики для визуального эффекта при перетаскивании файла
    ["dragenter", "dragover"].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.add("_active");
        });
    });

    ["dragleave", "drop"].forEach(event => {
        dropZone.addEventListener(event, (e) => {
            e.preventDefault();
            dropZone.classList.remove("_active");
        });
    });

    // Обработчик drop для отображения имени файла
    dropZone.addEventListener("drop", (event) => {
        event.preventDefault();
        selectedFile = event.dataTransfer.files[0];

        if (selectedFile) {
            uploadInput.files = event.dataTransfer.files;
            document.querySelector('.upload_zone_dragover > span').textContent = selectedFile.name;
        }
    });

    // Обработчик изменения input для отображения имени файла через выбор
    uploadInput.addEventListener("change", () => {
        selectedFile = uploadInput.files[0];

        if (selectedFile) {
            document.querySelector('.upload_zone_dragover > span').textContent = selectedFile.name;
        }
    });

    // Обработчик для кнопки отправки (нажимаем для загрузки файла и отправки выбранного банка)
    sendButton.addEventListener("click", () => {
        if (!selectedFile) {
            showMessage('Перед загрузкой выберите файл', 'error');
            return;
        }

        const bankName = document.querySelector('select[name="bank_sender"]').value;
        if (!bankName) {
            showMessage('Перед загрузкой укажите банк', 'error');
            return;
        }

        const applicationId = document.querySelector('#application_id').value;
        const formData = new FormData();
        formData.append("file_name", selectedFile);
        formData.append("application_id", applicationId);
        formData.append("bank_name", bankName);

        // Скрываем основной контент и показываем индикатор загрузки
        document.getElementById("original-content").style.display = "none";
        document.getElementById("loading-indicator").style.display = "block";

        // Отправляем AJAX-запрос на сервер
        fetch(uploadReceiptUrl, {
            method: "POST",
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().then(errData => {
                    showMessage(errData.error || "Ошибка при загрузке файла", 'error');
                    throw new Error(errData.error || "Ошибка при загрузке файла");
                });
            }
        })
        .then(data => {
            if (data.status === "success") {
                console.log('Успешно загружено');
                showMessage('Файл успешно загружен', "success");
            } else {
                showMessage(data.error || "Ошибка при загрузке файла", 'error');
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
            showMessage(error, 'error')
        });
    });
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", initUploadFeature);
