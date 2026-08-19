import { Clock, Route as RouteIcon, Check } from 'lucide-react';
import type { RouteOption } from '@/data/mockRoutes';

type RouteCardProps = {
  route: RouteOption;
  selected: boolean;
  onSelect: (id: string) => void;
};

const toneMap: Record<RouteOption['badge']['tone'], { chip: string; ring: string }> = {
  leaf: { chip: 'bg-leaf text-paper', ring: 'border-leaf-dark' },
  sky: { chip: 'bg-sky text-paper', ring: 'border-sky-dark' },
  sun: { chip: 'bg-sun text-ink', ring: 'border-sun-dark' },
};

export function RouteCard({ route, selected, onSelect }: RouteCardProps) {
  const tone = toneMap[route.badge.tone];
  return (
    <div
      className={[
        'relative bg-paper rounded-doodle border-[2.5px] border-ink p-5 transition-all',
        selected ? `${tone.ring} shadow-doodleLg ring-[3px] ring-offset-2 ring-offset-paper` : 'shadow-doodle hover:shadow-doodleLg',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-hand text-2xl text-ink leading-tight">{route.label}</h3>
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full border-2 border-ink ${tone.chip}`}>
              {route.badge.text}
            </span>
          </div>
          <p className="text-sm text-ink-soft">{route.emoji}</p>
        </div>
      </div>

      <div className="flex items-center gap-4 mt-3 text-ink">
        <span className="flex items-center gap-1.5 font-semibold">
          <Clock size={18} className="text-sky-dark" aria-hidden />
          {route.duration}
        </span>
        <span className="flex items-center gap-1.5 font-semibold">
          <RouteIcon size={18} className="text-leaf-dark" aria-hidden />
          {route.distance}
        </span>
      </div>

      <ul className="mt-4 flex flex-wrap gap-2" aria-label="Why this route">
        {route.why.map((tag) => (
          <li
            key={tag}
            className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-full border-2 border-ink bg-paper-200 text-ink font-medium"
          >
            <Check size={14} className="text-leaf-dark" aria-hidden />
            {tag}
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={() => onSelect(route.id)}
        aria-pressed={selected}
        className={[
          'mt-5 w-full min-h-[48px] inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-doodle border-[2.5px] border-ink font-bold transition-all',
          selected
            ? 'bg-leaf text-paper shadow-doodleSm'
            : 'bg-sky text-paper shadow-doodle hover:bg-sky-dark hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-doodleSm active:translate-x-[4px] active:translate-y-[4px] active:shadow-none',
        ].join(' ')}
      >
        {selected ? (
          <>
            <Check size={20} aria-hidden /> Selected
          </>
        ) : (
          'Select this route'
        )}
      </button>
    </div>
  );
}
