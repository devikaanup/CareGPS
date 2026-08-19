import { useState } from 'react';
import {
  ChevronDown,
  MapPin,
  Navigation,
  Sparkles,
  Waypoints,
  Construction,
  Lightbulb,
  CircleDot,
  Accessibility,
  Coffee,
  ShieldCheck,
  Trees,
} from 'lucide-react';

export type AdvancedOptions = {
  avoidHighways: boolean;
  avoidUnpaved: boolean;
  avoidPoorlyLit: boolean;
  avoidComplexRoundabouts: boolean;
  wheelchairAccessible: boolean;
  manyPitStops: boolean;
  womenSafety: boolean;
  scenicRoute: boolean;
};

export const defaultOptions: AdvancedOptions = {
  avoidHighways: false,
  avoidUnpaved: false,
  avoidPoorlyLit: false,
  avoidComplexRoundabouts: false,
  wheelchairAccessible: false,
  manyPitStops: false,
  womenSafety: false,
  scenicRoute: false,
};

type ToggleDef = {
  key: keyof AdvancedOptions;
  label: string;
  icon: typeof Waypoints;
  hint: string;
};

const toggles: ToggleDef[] = [
  { key: 'avoidHighways', label: 'Avoid highways', icon: Waypoints, hint: 'Skip fast multi-lane roads and tight merges' },
  { key: 'avoidUnpaved', label: 'Avoid unpaved roads', icon: Construction, hint: 'Stick to paved, smoother surfaces' },
  { key: 'avoidPoorlyLit', label: 'Avoid poorly lit roads', icon: Lightbulb, hint: 'Prefer well-lit streets after dark' },
  { key: 'avoidComplexRoundabouts', label: 'Avoid complex roundabouts', icon: CircleDot, hint: 'Simplify intersections and lane changes' },
  { key: 'wheelchairAccessible', label: 'Wheelchair / mobility accessible stops only', icon: Accessibility, hint: 'Only stops with ramps and step-free access' },
  { key: 'manyPitStops', label: 'Route with plenty of pit stops', icon: Coffee, hint: 'Add regular rest stops along the way' },
  { key: 'womenSafety', label: 'Women safety', icon: ShieldCheck, hint: 'Prefer well-lit, busier, verified-safe stretches' },
  { key: 'scenicRoute', label: 'Scenic route', icon: Trees, hint: 'Choose a road with more trees and nature rather than the city road' },
];

type InputPanelProps = {
  onSubmit: (data: {
    challenge: string;
    origin: string;
    destination: string;
    options: AdvancedOptions;
  }) => void;
};

export function InputPanel({ onSubmit }: InputPanelProps) {
  const [challenge, setChallenge] = useState('');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [options, setOptions] = useState<AdvancedOptions>(defaultOptions);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [error, setError] = useState('');

  function toggle(key: keyof AdvancedOptions) {
    setOptions((o) => ({ ...o, [key]: !o[key] }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!origin.trim() || !destination.trim()) {
      setError('Please provide both a starting point and a destination to get a route.');
      return;
    }
    setError('');
    onSubmit({ challenge: challenge.trim(), origin: origin.trim(), destination: destination.trim(), options });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="relative z-10 bg-paper border-[2.5px] border-ink rounded-doodle shadow-doodleLg p-5 sm:p-7"
    >
      <label htmlFor="challenge" className="block font-hand text-2xl text-ink mb-2">
        Describe your challenge
      </label>
      <p className="text-ink-soft text-sm mb-3">
        Tell us, in your own words, what makes travel tricky for you. We'll shape the route around it.
      </p>
      <textarea
        id="challenge"
        value={challenge}
        onChange={(e) => setChallenge(e.target.value)}
        placeholder="Describe your challenge — e.g. 'I have astigmatism and can't handle harsh lighting at night' or 'I'm new to driving'"
        rows={4}
        className="w-full min-h-[120px] resize-y rounded-doodle border-[2.5px] border-ink bg-paper-100 p-4 text-base placeholder:text-ink-soft/70 focus:bg-paper"
      />

      <div className="scribble-divider my-6" aria-hidden="true" />

      <div className="grid sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="origin" className="flex items-center gap-2 font-semibold text-ink mb-1.5">
            <MapPin size={18} className="text-leaf-dark" aria-hidden /> Starting point
          </label>
          <input
            id="origin"
            type="text"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            placeholder="e.g. VIT Chennai"
            className="w-full min-h-[48px] rounded-doodle border-[2.5px] border-ink bg-paper-100 px-4 py-2.5 text-base placeholder:text-ink-soft/70 focus:bg-paper"
          />
        </div>
        <div>
          <label htmlFor="destination" className="flex items-center gap-2 font-semibold text-ink mb-1.5">
            <Navigation size={18} className="text-sky-dark" aria-hidden /> Destination
          </label>
          <input
            id="destination"
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="e.g. Phoenix Mall"
            className="w-full min-h-[48px] rounded-doodle border-[2.5px] border-ink bg-paper-100 px-4 py-2.5 text-base placeholder:text-ink-soft/70 focus:bg-paper"
          />
        </div>
      </div>

      {/* Advanced options */}
      <div className="mt-5">
        <button
          type="button"
          onClick={() => setAdvancedOpen((v) => !v)}
          aria-expanded={advancedOpen}
          aria-controls="advanced-options"
          className="flex items-center gap-2 min-h-[44px] px-3 py-2 rounded-doodle border-[2.5px] border-ink bg-paper-200 hover:bg-paper-100 font-semibold transition-colors"
        >
          <ChevronDown
            size={20}
            className={`transition-transform ${advancedOpen ? 'rotate-180' : ''}`}
            aria-hidden
          />
          Advanced options
          <span className="text-xs font-normal text-ink-soft">
            ({Object.values(options).filter(Boolean).length} on)
          </span>
        </button>

        {advancedOpen && (
          <fieldset
            id="advanced-options"
            className="mt-4 grid sm:grid-cols-2 gap-3 p-4 rounded-doodle border-2 border-dashed border-ink/60 bg-paper-50"
          >
            <legend className="px-2 font-hand text-lg text-ink">Route preferences</legend>
            {toggles.map(({ key, label, icon: Icon, hint }) => {
              const on = options[key];
              return (
                <label
                  key={key}
                  className={[
                    'flex items-start gap-3 p-3 rounded-[0.8rem] border-[2.5px] cursor-pointer transition-colors min-h-[64px]',
                    on ? 'border-ink bg-sky-soft' : 'border-ink/30 bg-paper hover:border-ink/60',
                  ].join(' ')}
                >
                  <span
                    className={[
                      'mt-0.5 grid place-items-center w-9 h-9 rounded-[0.6rem] border-[2.5px] border-ink shrink-0',
                      on ? 'bg-sky text-paper' : 'bg-paper text-ink-soft',
                    ].join(' ')}
                  >
                    <Icon size={18} strokeWidth={2.5} />
                  </span>
                  <span className="flex-1">
                    <span className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={on}
                        onChange={() => toggle(key)}
                        className="sr-only"
                      />
                      <span className="font-semibold text-ink">{label}</span>
                      <span
                        className={[
                          'ml-auto text-xs font-bold px-2 py-0.5 rounded-full border-2 border-ink',
                          on ? 'bg-leaf text-paper' : 'bg-paper text-ink-soft',
                        ].join(' ')}
                        aria-hidden
                      >
                        {on ? 'ON' : 'OFF'}
                      </span>
                    </span>
                    <span className="block text-xs text-ink-soft mt-0.5">{hint}</span>
                  </span>
                </label>
              );
            })}
          </fieldset>
        )}
      </div>

      {error && (
        <p role="alert" className="mt-4 p-3 rounded-doodle border-[2.5px] border-coral bg-coral-soft text-coral-dark font-medium">
          {error}
        </p>
      )}

      <button
        type="submit"
        className="mt-6 w-full sm:w-auto min-h-[56px] inline-flex items-center justify-center gap-2 px-7 py-3.5 rounded-doodle border-[2.5px] border-ink bg-sky text-paper font-bold text-lg shadow-doodle hover:bg-sky-dark hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-doodleSm active:translate-x-[4px] active:translate-y-[4px] active:shadow-none transition-all"
      >
        <Sparkles size={22} strokeWidth={2.5} aria-hidden />
        Get My Route
      </button>
    </form>
  );
}
