from django import forms
from django.utils.safestring import mark_safe
import json
from main_site.utils.banks_name import get_bank_names

class BankSelectionWidget(forms.Widget):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.bank_choices = get_bank_names()

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        if attrs is None:
            attrs = {}
        final_attrs = self.build_attrs(attrs, extra_attrs={'name': name})
        id_ = final_attrs.get('id', 'id_%s' % name)
        safe_id = id_.replace('-', '_')  # Заменяем дефисы на подчеркивания

        selected_banks = value or []
        all_banks = [bank for bank in self.bank_choices if bank not in selected_banks]

        options_html = ''.join(['<option value="{}">{}</option>'.format(bank, bank) for bank in all_banks])
        selected_list_html = ''.join(['<li>{}</li>'.format(bank) for bank in selected_banks])

        html = f"""
        <div id="{id_}_bank-selection">
            <select id="{id_}_bank-choices" class="bank-choice-dropdown">
                {options_html}
            </select>
            <button type="button" onclick="addBank_{safe_id}()">Добавить</button>
            <button type="button" onclick="clearBanks_{safe_id}()">Очистить</button>
            <ul id="{id_}_selected-banks-list">
                {selected_list_html}
            </ul>
            <input type="hidden" name="{name}" id="{id_}" value='{json.dumps(selected_banks)}'>
        </div>

        <script>
        function addBank_{safe_id}() {{
            var bankSelect = document.getElementById("{id_}_bank-choices");
            var selectedBank = bankSelect.options[bankSelect.selectedIndex].value;
            if (!selectedBank) return;
            var selectedList = document.getElementById("{id_}_selected-banks-list");
            selectedList.insertAdjacentHTML('beforeend', `<li>${{selectedBank}}</li>`);
            updateHiddenInput_{safe_id}();
            bankSelect.remove(bankSelect.selectedIndex);
        }}

        function clearBanks_{safe_id}() {{
            document.getElementById("{id_}_selected-banks-list").innerHTML = '';
            updateHiddenInput_{safe_id}();
        }}

        function updateHiddenInput_{safe_id}() {{
            var selectedBanks = Array.from(document.getElementById("{id_}_selected-banks-list").getElementsByTagName("li"))
                .map(li => li.textContent);
            document.getElementById("{id_}").value = JSON.stringify(selectedBanks);
        }}
        </script>
        """

        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return []
        return []
