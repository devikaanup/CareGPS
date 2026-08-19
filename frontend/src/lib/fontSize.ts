export type FontSize = 'small' | 'medium' | 'large';

const scaleMap: Record<FontSize, number> = {
  small: 0.9,
  medium: 1,
  large: 1.15,
};

export function applyFontSize(size: FontSize) {
  document.documentElement.style.setProperty('--font-scale', String(scaleMap[size]));
}
