/**
 * Общая конфигурация WYSIWYG редактора TinyMCE для форм сайта.
 *
 * URL скрипта редактора передается из шаблона (STATIC_URL хранилища статики);
 * скины и стили содержимого входят в комплект пакета и копируются сборкой
 * рядом со скриптом.
 */

import type { ComponentProps } from 'react';
import type { Editor } from '@tinymce/tinymce-react';

/** Тип пропа init компонента Editor: опции TinyMCE без selector и target. */
export type EditorInitOptions = ComponentProps<typeof Editor>['init'];

/**
 * Возвращает объект init для компонента Editor (@tinymce/tinymce-react)
 * в цветовой схеме, соответствующей теме сайта.
 *
 * @example
 * <Editor init={getEditorInit(isDark)} />
 */
export const getEditorInit = (isDark: boolean): EditorInitOptions => ({
  // Интеграция @tinymce/tinymce-react перекрывает license_key пропом licenseKey
  // (по умолчанию 'gpl'); поле оставлено для прежнего объекта init
  license_key: 'gpl' as unknown as never,
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
    'link',
    'image',
    'media',
    'preview',
    'codesample',
    'table',
    'code',
    'lists',
    'fullscreen',
    'insertdatetime',
    'nonbreaking',
    'directionality',
    'searchreplace',
    'wordcount',
    'visualblocks',
    'visualchars',
    'autolink',
    'charmap',
    'anchor',
    'pagebreak',
    'autoresize',
  ],
  toolbar1:
    'fullscreen preview bold italic underline | fontfamily fontsize | forecolor backcolor | alignleft alignright | aligncenter alignjustify | indent outdent | bullist numlist table | link image media | codesample',
  toolbar2: 'visualblocks visualchars | charmap hr pagebreak nonbreaking anchor | code',
});

export default getEditorInit;
