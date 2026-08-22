

// Ждем полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {

    // Пример: добавляем обработчик клика на кнопку
    // Сначала проверяем, существует ли элемент
    const myButton = document.getElementById('my-button');
    if (myButton) {
        myButton.addEventListener('click', function() {
            alert('Вы нажали на кнопку!');
        });
    }

    // Пример: меняем текст в блоке
    const textBlock = document.getElementById('text-block');
    if (textBlock) {
        textBlock.textContent = 'Текст изменён с помощью custom.js';
    }
});