import { Compass, Type } from 'lucide-react';
import type { FontSize } from '@/lib/fontSize';

type HeaderProps = {
  fontSize: FontSize;
  onFontSizeChange: (size: FontSize) => void;
};

const sizes: FontSize[] = ['small', 'medium', 'large'];

const sizeLabel: Record<FontSize, string> = {
  small: 'Small',
  medium: 'Medium',
  large: 'Large',
};

export function Header({ fontSize, onFontSizeChange }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 bg-paper/95 backdrop-blur border-b-[2.5px] border-ink/80">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <span className="grid place-items-center w-10 h-10 rounded-doodle bg-sky-soft text-sky-dark border-[2.5px] border-ink shadow-doodleSm">
            <Compass size={22} strokeWidth={2.5} />
          </span>
          <div className="leading-tight">
            <p className="font-hand text-2xl stroke-hand">CareGPS</p>
            <p className="text-xs text-ink-soft font-medium -mt-0.5">Calm routes for everyone</p>
          </div>
        </div>

        <div
          className="flex items-center gap-1.5 rounded-doodle border-[2.5px] border-ink bg-paper p-1 shadow-doodleSm"
          role="group"
          aria-label="Text size"
        >
          <Type size={16} className="text-ink-soft ml-1.5" aria-hidden />
          {sizes.map((s) => {
            const active = fontSize === s;
            return (
              <button
                key={s}
                type="button"
                onClick={() => onFontSizeChange(s)}
                aria-pressed={active}
                aria-label={`Text size ${sizeLabel[s]}`}
                className={[
                  'min-w-[44px] min-h-[44px] px-2 rounded-[0.6rem] font-semibold transition-colors',
                  active
                    ? 'bg-ink text-paper'
                    : 'text-ink hover:bg-paper-200',
                ].join(' ')}
              >
                <span className="text-sm">A</span>
                <span className="sr-only">{sizeLabel[s]}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
