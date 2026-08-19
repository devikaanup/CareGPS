import type { Pitstop } from '@/data/mockRoutes';
import { DoodleBench, DoodleCup, DoodleRestroom, DoodleBusStop } from './Doodles';

const pitstopDoodle: Record<Pitstop['type'], typeof DoodleBench> = {
  rest: DoodleBench,
  coffee: DoodleCup,
  restroom: DoodleRestroom,
  accessible: DoodleBusStop,
};

const typeLabel: Record<Pitstop['type'], string> = {
  rest: 'Rest stop',
  coffee: 'Café break',
  restroom: 'Restroom',
  accessible: 'Accessible stop',
};

export function PitstopList({ pitstops }: { pitstops: Pitstop[] }) {
  return (
    <section
      aria-label="Pit stops along this route"
      className="bg-paper rounded-doodle border-[2.5px] border-ink shadow-doodle p-5"
    >
      <h2 className="font-hand text-2xl text-ink mb-1">Pit stops on this route</h2>
      <p className="text-sm text-ink-soft mb-4">Verified spots to rest, refuel, and take a breath.</p>

      <ol className="relative pl-6">
        {/* connector line */}
        <span className="absolute left-[10px] top-2 bottom-2 w-[3px] bg-ink/20 rounded-full" aria-hidden />
        {pitstops.map((stop, i) => {
          const Icon = pitstopDoodle[stop.type];
          return (
            <li key={stop.id} className="relative mb-4 last:mb-0">
              <span
                className="absolute -left-6 top-1.5 grid place-items-center w-6 h-6 rounded-full border-[2.5px] border-ink bg-sun text-ink text-xs font-bold"
                aria-hidden
              >
                {i + 1}
              </span>
              <div className="flex items-start gap-3 p-3 rounded-[0.8rem] border-2 border-ink/30 bg-paper-50 hover:border-ink/60 transition-colors">
                <Icon className="w-8 shrink-0 text-ink" aria-hidden />
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="font-semibold text-ink">{stop.name}</p>
                    <span className="text-[11px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border-2 border-ink bg-paper-200 text-ink-soft">
                      {typeLabel[stop.type]}
                    </span>
                  </div>
                  <p className="text-sm text-ink-soft mt-0.5">{stop.note}</p>
                  <p className="text-xs font-semibold text-sky-dark mt-1">At {stop.distance} from start</p>
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
