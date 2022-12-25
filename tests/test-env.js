const test = require('node:test');
const assert = require('node:assert').strict;

/**
 * Список модулей node, которые должны быть установлены в проекте.
 * @type {!Array<string>}
 */
const modules = [
    'bootstrap',
];

/**
 * Проверяет возможность импорта модуля, 
 * не производя фактический импорт.
 * @param {string} module
 * @return {boolean}
 */
function moduleInstalled(module) {
    try {
        require.resolve(module);
        return true;
    } catch(e) {
        return false;
    }
}

test(`Проверка установки модулей node`, (t) => {
    modules.forEach((module) => {
        assert.ok(moduleInstalled(module), `Модуль ${module} не установлен`);
    })
});