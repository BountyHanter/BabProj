function showMessage(message, type = '') {
    let iconHtml = '';
    if (type === 'success') {
        iconHtml = '<div class="icon success-icon">&#10004;</div>'; // Галочка
    } else if (type === 'error') {
        iconHtml = '<div class="icon error-icon">&#10006;</div>'; // Крестик
    }

    const $notification = $(`
        <div class="notification ${type}">
            <button class="close">&times;</button>
            ${iconHtml}
            <div class="message-content">${message}</div>
        </div>
    `);

    $('#notification-container').prepend($notification);

    $notification.css({ right: '-320px', display: 'block' }).animate({ right: '0' }, 500);

    let hideTimeout = setTimeout(function() {
        $notification.fadeOut(500, function() {
            $(this).remove();
        });
    }, 5000);

    $notification.on('mouseenter', function() {
        clearTimeout(hideTimeout);
    }).on('mouseleave', function() {
        hideTimeout = setTimeout(function() {
            $notification.fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    });

    $notification.find('.close').on('click', function() {
        $notification.fadeOut(500, function() {
            $(this).remove();
        });
    });
}