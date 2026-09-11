/**
 * Общая конфигурация WYSIWYG редактора TinyMCE для форм сайта.
 *
 * Ресурсы TinyMCE загружаются локально (tinymceScriptSrc /static/tinymce/),
 * без CDN и API-ключа; скины и стили содержимого входят в комплект пакета
 * и копируются сборкой в /static/tinymce/skins/.
 */

/**
 * Возвращает объект init для компонента Editor (@tinymce/tinymce-react)
 * в цветовой схеме, соответствующей теме сайта.
 *
 * @param {boolean} isDark - Действует ли темная тема сайта
 * @return {Object} Конфигурация init для TinyMCE
 *
 * @example
 * <Editor init={getEditorInit(isDark)} />
 */
export const getEditorInit = (isDark) => ({
  license_key: 'gpl',
  // Тема редактора следует теме сайта: скин интерфейса и стили содержимого
  menubar: true,
  statusbar: true,
  branding: false,
  promotion: false,
  skin: isDark ? 'oxide-dark' : 'oxide',
  content_css: isDark ? 'dark' : 'default',
  // Контент рендерится на страницах другой глубины, чем страница редактора:
  // относительные адреса разрешались бы в другие места. Адреса сохраняются
  // от корня сайта, без хоста
  relative_urls: false,
  remove_script_host: true,
  plugins: [
    'link', 'image', 'media', 'preview', 'codesample',
    'table', 'code', 'lists', 'fullscreen', 'insertdatetime', 'nonbreaking',
    'directionality', 'searchreplace', 'wordcount', 'visualblocks',
    'visualchars', 'autolink', 'charmap', 'anchor', 'pagebreak', 'autoresize',
  ],
  toolbar1: 'fullscreen preview bold italic underline | fontfamily fontsize | forecolor backcolor | alignleft alignright | aligncenter alignjustify | indent outdent | bullist numlist table | link image media | codesample',
  toolbar2: 'visualblocks visualchars | charmap hr pagebreak nonbreaking anchor | code',
});

export default getEditorInit;
