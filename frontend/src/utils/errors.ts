/**
 * Единое извлечение сообщения об ошибке из перехваченного исключения.
 *
 * Повторяющийся паттерн catch-блоков: у Error с непустым сообщением берется
 * сообщение, остальное приводится к строке.
 */

/** Извлекает понятное сообщение об ошибке из перехваченного исключения. */
export function getErrorMessage(err: unknown): string {
  return err instanceof Error && err.message ? err.message : String(err);
}
