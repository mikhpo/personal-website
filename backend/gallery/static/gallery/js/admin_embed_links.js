/**
 * Копирование постоянных ссылок на превью фотографии в админ-панели.
 *
 * Кнопка .embed-copy-button собирает полный адрес из домена сайта и пути
 * в соседнем поле .embed-link-url: ссылка для вставки в редакторы статей
 * и сторонние ресурсы должна быть абсолютной.
 */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.embed-copy-button').forEach((button) => {
    button.addEventListener('click', async () => {
      const input = document.getElementById(button.dataset.target);
      if (!input) {
        return;
      }
      const url = window.location.origin + input.value;
      try {
        await navigator.clipboard.writeText(url);
      } catch {
        input.select();
        document.execCommand('copy');
      }
      button.textContent = 'Скопировано';
      setTimeout(() => {
        button.textContent = 'Копировать';
      }, 2000);
    });
  });
});
