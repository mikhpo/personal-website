import React from 'react';
import { Form } from 'react-bootstrap';

/** Элемент справочника для мультивыбора. */
interface TaxonomyOption {
  id: number;
  name: string;
}

/** Свойства мультивыбора справочника статьи. */
export interface TaxonomyMultiSelectProps {
  /** controlId группы форм. */
  controlId: string;
  /** Подпись поля. */
  label: string;
  /** Элементы справочника. */
  options: TaxonomyOption[];
  /** Выбранные идентификаторы. */
  selected: number[];
  /** Обработчик изменения выбора. */
  onChange: (selected: number[]) => void;
}

/**
 * Мультивыбор справочника статьи: категории, серии и темы используют
 * одинаковый элемент формы с множественным выбором.
 */
const TaxonomyMultiSelect = ({ controlId, label, options, selected, onChange }: TaxonomyMultiSelectProps) => {
  /** Обработчик мультивыбора. */
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(Array.from(event.target.selectedOptions, (option) => Number(option.value)));
  };

  return (
    <Form.Group className="mb-3" controlId={controlId}>
      <Form.Label>{label}</Form.Label>
      {/* size={5} исторически превращался в класс form-select-5, а не в нативный
          атрибут размера, а числа в value не совпадали со строковыми option;
          приведения сохраняют прежний DOM (журнал tasks.md, фаза 5) */}
      <Form.Select
        multiple
        size={5 as unknown as 'sm'}
        value={selected as unknown as readonly string[]}
        onChange={handleChange}
      >
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </Form.Select>
    </Form.Group>
  );
};

export default TaxonomyMultiSelect;
