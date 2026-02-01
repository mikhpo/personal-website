import React from 'react';
import PropTypes from 'prop-types';
import { Navbar as BSNavbar } from 'react-bootstrap';

/**
 * Компонент секции бренда навигационной панели
 *
 * @param {Object} props - Свойства компонента
 * @param {string} props.brandName - Название бренда
 * @param {string} props.brandUrl - URL для ссылки на главную страницу
 *
 * @return {JSX.Element} Элемент секции бренда
 */
const BrandSection = ({ brandName, brandUrl }) => {
  return (
    <BSNavbar.Brand href={brandUrl}>{brandName}</BSNavbar.Brand>
  );
};

BrandSection.propTypes = {
  brandName: PropTypes.string.isRequired,
  brandUrl: PropTypes.string.isRequired,
};

export default BrandSection;
