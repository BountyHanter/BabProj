$(document).ready(function() {
    // Инициализируем Select2 на выпадающем списке банков
    $('#bank-select').select2({
        placeholder: 'Выберите банк',
        allowClear: true
    });

    // Массив банков из глобальной переменной
    const banks = banksData;

    // Функция для заполнения Select2 выпадающего списка
    function populateBanksSelect(banksToShow) {
        const bankSelect = $('#bank-select');
        bankSelect.empty();  // Очищаем список перед добавлением новых значений

        // Добавляем placeholder как пустой элемент
        const placeholderOption = new Option('', '', false, false);
        bankSelect.append(placeholderOption);

        // Проходим по массиву банков и добавляем каждый банк в список
        banksToShow.forEach(function(bank) {
            const newOption = new Option(bank.name, bank.id, false, false);
            bankSelect.append(newOption);
        });

        // Обновляем Select2 после добавления новых опций
        bankSelect.trigger('change');
    }

    // Заполняем список при загрузке страницы
    populateBanksSelect(banks);

    // Функция для фильтрации банков на основе введенного текста
    $('#bank-select').on('select2:open', function() {
        const searchInput = $('.select2-search__field');

        searchInput.on('input', function() {
            const searchTerm = $(this).val().toLowerCase();

            const filteredBanks = banks.filter(function(bank) {
                return bank.name.toLowerCase().includes(searchTerm);
            });

            populateBanksSelect(filteredBanks);  // Обновляем список с фильтрацией
        });
    });
});
