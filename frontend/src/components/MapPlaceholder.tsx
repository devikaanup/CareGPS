import { Map as MapIcon } from 'lucide-react';
import { DoodleCar, DoodleTree } from './Doodles';

export function MapPlaceholder() {
  return (
    <div
      className="relative w-full h-full min-h-[260px] rounded-doodle border-[2.5px] border-dashed border-ink/70 bg-paper-100 overflow-hidden"
      role="img"
      aria-label="Map preview placeholder — a real map will appear here"
    >
      {/* Sketchy grid lines suggesting a map */}
      <svg className="absolute inset-0 w-full h-full opacity-30" aria-hidden>
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M0 20 L40 20 M20 0 L20 40" stroke="#1f2233" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Suggested route path */}
      <svg className="absolute inset-0 w-full h-full" aria-hidden viewBox="0 0 400 260" preserveAspectRatio="none">
        <path
          d="M30 220 Q120 200 140 150 T 230 110 Q300 90 370 40"
          fill="none"
          stroke="#2f6fed"
          strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray="2 10"
        />
        <circle cx="30" cy="220" r="7" fill="#1f9d63" stroke="#1f2233" strokeWidth="2.5" />
        <circle cx="370" cy="40" r="7" fill="#e8624a" stroke="#1f2233" strokeWidth="2.5" />
      </svg>

      {/* Center label */}
      <div className="absolute inset-0 grid place-items-center pointer-events-none">
        <div className="flex items-center gap-2 px-4 py-2 rounded-doodle border-[2.5px] border-ink bg-paper/90 shadow-doodleSm">
          <MapIcon size={20} className="text-sky-dark" aria-hidden />
          <span className="font-hand text-xl text-ink">Map preview coming soon</span>
        </div>
      </div>

      {/* Flavor doodles near edges */}
      <DoodleCar className="absolute bottom-2 left-2 w-12 text-ink/50 animate-drive" aria-hidden />
      <DoodleTree className="absolute top-2 right-2 w-10 text-leaf-dark/50" aria-hidden />
    </div>
  );
}
