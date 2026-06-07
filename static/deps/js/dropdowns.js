document.addEventListener('DOMContentLoaded', function() {
    // Получаем все кнопки-триггеры (предполагаем, что у них класс .dropdown-toggle)
    const toggleButtons = document.querySelectorAll('.dropdown-toggle');
    
    // Получаем все панели выпадающих списков (предполагаем, что у них класс .dropdown-menu)
    const dropdownMenus = document.querySelectorAll('.dropdown-menu');

    // Функция для закрытия всех открытых меню
    function closeAllMenus() {
        dropdownMenus.forEach(menu => {
            menu.classList.remove('show');
        });
    }

    // Обработчик клика по кнопке
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // Отменяем стандартное действие ссылки, если кнопка — это <a>

            // Находим связанное меню (обычно оно идет сразу после кнопки в HTML)
            const targetMenu = this.nextElementSibling;
            
            // Если это меню и оно не активно — открываем его
            if (targetMenu && targetMenu.classList.contains('dropdown-menu')) {
                closeAllMenus(); // Сначала закрываем все остальные
                targetMenu.classList.add('show');
            }
        });
    });

    // Закрываем меню при клике вне его (на документ)
    document.addEventListener('click', function(e) {
        dropdownMenus.forEach(menu => {
            if (!menu.contains(e.target)) {
                menu.classList.remove('show');
            }
        });
    });
});

