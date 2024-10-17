// Преобразуем массив строк в массив объектов для Select2
const formattedBanksData = banksData.map((name, index) => ({
    id: index + 1, // Можно использовать индекс как ID или другое уникальное значение
    text: name
}));

console.log(formattedBanksData)
// Теперь инициализируем Select2 с этими данными
$(document).ready(function() {
    $('#bank-select').select2({
        theme: 'bootstrap4',
        placeholder: 'Выберите банк',
        allowClear: true,
        data: formattedBanksData
    });
});