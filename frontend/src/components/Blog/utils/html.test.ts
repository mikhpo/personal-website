/**
 * Тесты для утилит работы с HTML-строками.
 *
 * Проверяет подсчет слов в сыром HTML и обрезку HTML до заданного числа слов
 * с сохранением целостности разметки.
 */

import { countHtmlWords, truncateHtmlWords } from './html';

describe('countHtmlWords', () => {
  test('считает слова в текстовых узлах', () => {
    expect(countHtmlWords('<p>один два три</p>')).toBe(3);
  });

  test('учитывает содержимое тегов и атрибуты', () => {
    expect(countHtmlWords('<p style="text-align: justify;">один два</p>')).toBe(4);
  });

  test('возвращает 0 для пустой строки', () => {
    expect(countHtmlWords('')).toBe(0);
  });
});

describe('truncateHtmlWords', () => {
  test('обрезает текст до заданного числа слов и добавляет многоточие', () => {
    expect(truncateHtmlWords('<p>один два три четыре пять</p>', 4)).toBe('<p>один два три четыре…</p>');
  });

  test('сохраняет фотографию до точки обрезки', () => {
    const html = '<p><img src="/x.jpg" alt=""></p><p>один два три четыре пять</p>';
    expect(truncateHtmlWords(html, 4)).toBe('<p><img src="/x.jpg" alt=""></p><p>один два три четыре…</p>');
  });

  test('не ставит void-элемент на стек открытых тегов', () => {
    expect(truncateHtmlWords('<p>один<br>два три</p>', 1)).toBe('<p>один<br>…</p>');
  });

  test('закрывает открытые теги в обратном порядке', () => {
    expect(truncateHtmlWords('<p><b><i>один два</i> три</p>', 2)).toBe('<p><b><i>один два</i>…</b></p>');
  });

  test('самозакрывающийся тег не остается на стеке', () => {
    expect(truncateHtmlWords('<p>один<img src="x"/> два три</p>', 2)).toBe('<p>один<img src="x"/> два…</p>');
  });

  test('возвращает короткий контент без изменений', () => {
    expect(truncateHtmlWords('<p>один два</p>', 5)).toBe('<p>один два</p>');
  });

  test('не добавляет многоточие при числе слов ровно по лимиту', () => {
    expect(truncateHtmlWords('<p>один два</p>', 2)).toBe('<p>один два</p>');
  });

  test('обрезает на границе текстовых узлов', () => {
    expect(truncateHtmlWords('<p>один</p><p>два</p>', 1)).toBe('<p>один</p><p>…</p>');
  });

  test('пробельный узел между абзацами считается одним словом', () => {
    const html = '<p>раз</p>\r\n<p style="text-align: justify;">два три четыре</p>';
    expect(truncateHtmlWords(html, 3)).toBe('<p>раз</p>\r\n<p style="text-align: justify;">два…</p>');
  });

  test('выбрасывает комментарии из результата', () => {
    expect(truncateHtmlWords('<!-- комментарий --><p>один два три</p>', 1)).toBe('<p>один…</p>');
  });

  test('сохраняет ведущий пробел обрезанного узла при непустом срезе', () => {
    expect(truncateHtmlWords('<p>   один   два   </p>', 1)).toBe('<p>   один…</p>');
  });

  test('сохраняет теги внутри текста до точки обрезки', () => {
    expect(truncateHtmlWords('<p>один <b>жирный</b> два три</p>', 3)).toBe('<p>один <b>жирный</b> два…</p>');
  });

  test('закрывает теги списков', () => {
    expect(truncateHtmlWords('<ul><li>один</li><li>два</li><li>три</li></ul>', 2)).toBe(
      '<ul><li>один</li><li>два</li><li>…</li></ul>',
    );
  });

  test('возвращает пустую строку для пустого контента', () => {
    expect(truncateHtmlWords('', 5)).toBe('');
  });

  test('возвращает пустую строку при нулевом лимите', () => {
    expect(truncateHtmlWords('<p>один</p>', 0)).toBe('');
  });
});
