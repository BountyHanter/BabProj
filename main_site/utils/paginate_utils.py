from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate_queryset(queryset, page_number, rows_per_page):
    paginator = Paginator(queryset, rows_per_page)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page, paginator.num_pages


def paginate_with_range(queryset, page_number=1, rows_per_page=15, max_pages_to_show=5):
    # Создаем объект пагинатора
    paginator = Paginator(queryset, rows_per_page)

    # Обработка случаев, когда номер страницы некорректный
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Получаем общее количество страниц
    total_pages = paginator.num_pages

    # Вычисляем диапазон страниц для отображения
    half_range = max_pages_to_show // 2
    start_page = max(page_number - half_range, 1)
    end_page = min(page_number + half_range, total_pages)
    page_range = range(start_page, end_page + 1)

    return page_obj, page_range, total_pages
