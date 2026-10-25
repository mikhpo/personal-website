import { useCallback, useEffect, useRef, useState } from 'react';

/** Интервал автосохранения статьи в миллисекундах. */
const AUTOSAVE_INTERVAL_MS = 60000;

/** Свойства хука автосохранения статьи. */
export interface UseArticleAutosaveOptions<T> {
  /** Текущее состояние формы. */
  form: T;
  /** Идет ли загрузка данных формы; отпечаток фиксируется после ее завершения. */
  loading: boolean;
  /** Действует ли автосохранение: только для черновиков. */
  enabled: boolean;
  /** Готова ли форма к сохранению. */
  canSave: boolean;
  /** Строит отпечаток состояния формы для сравнения. */
  buildSnapshot: (state: T) => string;
  /** Сохраняет статью на сервере. */
  saveArticle: (state: T) => Promise<unknown>;
}

/** Результат хука автосохранения статьи. */
export interface UseArticleAutosaveResult<T> {
  /** Подпись последнего автосохранения. */
  autosaveStatus: string | null;
  /** Признак ошибки автосохранения. */
  autosaveError: boolean;
  /** Промис выполняемого автосохранения: явное сохранение дожидается его завершения. */
  inFlightRef: React.MutableRefObject<Promise<void> | null>;
  /** Признак выполняемого запроса для блокировки автосохранения. */
  submittingRef: React.MutableRefObject<boolean>;
  /** Перезапускает интервал автосохранения после явного сохранения. */
  restartTimer: () => void;
  /** Фиксирует отпечаток состояния после явного сохранения. */
  markSaved: (state: T) => void;
}

/**
 * Форматирует время для подписи автосохранения в виде ЧЧ:ММ.
 */
const formatTime = (date: Date): string => date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

/**
 * Хук автосохранения статьи: раз в минуту сохраняет форму при наличии изменений.
 *
 * Владеет всей механикой автосохранения: отпечатком состояния на момент
 * последнего сохранения, интервалом, блокировкой параллельных запросов.
 * Автосохранение действует, пока enabled: опубликованная статья обновляется
 * только явной кнопкой. Явное сохранение через inFlightRef дожидается
 * выполняемого автосохранения и через restartTimer перезапускает интервал.
 *
 * @example
 * const { autosaveStatus, autosaveError, inFlightRef, submittingRef, restartTimer, markSaved } =
 *   useArticleAutosave({ form, loading, enabled, canSave, buildSnapshot, saveArticle });
 */
const useArticleAutosave = <T>({
  form,
  loading,
  enabled,
  canSave,
  buildSnapshot,
  saveArticle,
}: UseArticleAutosaveOptions<T>): UseArticleAutosaveResult<T> => {
  /** Подпись последнего автосохранения. */
  const [autosaveStatus, setAutosaveStatus] = useState<string | null>(null);

  /** Признак ошибки автосохранения. */
  const [autosaveError, setAutosaveError] = useState(false);

  /** Ключ для перезапуска интервала автосохранения после явного сохранения. */
  const [timerKey, setTimerKey] = useState(0);

  /** Отпечаток состояния на момент последнего сохранения. */
  const snapshotRef = useRef<string | null>(null);

  /** Промис выполняемого автосохранения: явное сохранение дожидается его завершения. */
  const autosaveInFlightRef = useRef<Promise<void> | null>(null);

  /** Признак выполняемого запроса для блокировки автосохранения. */
  const submittingRef = useRef(false);

  /** Ссылка на последнюю версию обработчика автосохранения. */
  const autosaveRef = useRef<() => void>(() => {});

  /** Признак инициализации отпечатка после загрузки данных. */
  const snapshotInitializedRef = useRef(false);

  /** Фиксирует отпечаток исходного состояния формы после загрузки. */
  useEffect(() => {
    if (!loading && !snapshotInitializedRef.current) {
      snapshotRef.current = buildSnapshot(form);
      snapshotInitializedRef.current = true;
    }
  }, [loading, form, buildSnapshot]);

  /**
   * Обработчик автосохранения: сохраняет только при изменениях и только черновики.
   */
  const handleAutosave = async (): Promise<void> => {
    if (loading || !enabled || submittingRef.current || !canSave) {
      return;
    }
    if (snapshotRef.current === buildSnapshot(form)) {
      return;
    }
    submittingRef.current = true;
    const savePromise = (async () => {
      try {
        await saveArticle(form);
        snapshotRef.current = buildSnapshot(form);
        setAutosaveError(false);
        setAutosaveStatus(`Автосохранено в ${formatTime(new Date())}`);
      } catch {
        setAutosaveError(true);
      } finally {
        submittingRef.current = false;
        autosaveInFlightRef.current = null;
      }
    })();
    autosaveInFlightRef.current = savePromise;
    await savePromise;
  };

  // Эффект обновления ссылки на обработчик автосохранения
  useEffect(() => {
    autosaveRef.current = handleAutosave;
  });

  // Эффект запуска интервала автосохранения
  useEffect(() => {
    const interval = setInterval(() => autosaveRef.current(), AUTOSAVE_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [timerKey]);

  /** Перезапускает интервал автосохранения после явного сохранения. */
  const restartTimer = useCallback(() => {
    setTimerKey((key) => key + 1);
  }, []);

  /** Фиксирует отпечаток состояния после явного сохранения. */
  const markSaved = useCallback(
    (state: T) => {
      snapshotRef.current = buildSnapshot(state);
    },
    [buildSnapshot],
  );

  return {
    autosaveStatus,
    autosaveError,
    inFlightRef: autosaveInFlightRef,
    submittingRef,
    restartTimer,
    markSaved,
  };
};

export default useArticleAutosave;
