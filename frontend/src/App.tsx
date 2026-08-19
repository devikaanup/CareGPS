import { useState } from 'react';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { Header } from '@/components/Header';
import { DoodleDecoration } from '@/components/DoodleDecoration';
import { InputPanel, type AdvancedOptions } from '@/components/InputPanel';
import { RouteCard } from '@/components/RouteCard';
import { PitstopList } from '@/components/PitstopList';
import { MapPlaceholder } from '@/components/MapPlaceholder';
import { RouteMap } from '@/components/RouteMap';
import { mockRoutes, type RouteOption } from '@/data/mockRoutes';
import { applyFontSize, type FontSize } from '@/lib/fontSize';

type View = 'dashboard' | 'results';

function App() {
  const [view, setView] = useState<View>('dashboard');
  const [fontSize, setFontSize] = useState<FontSize>('medium');
  const [selectedRouteId, setSelectedRouteId] = useState<string>('');
  const [submitted, setSubmitted] = useState<{
    challenge: string;
    origin: string;
    destination: string;
    options: AdvancedOptions;
  } | null>(null);

  const [realRoutes, setRealRoutes] = useState<RouteOption[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleFontSize(size: FontSize) {
    setFontSize(size);
    applyFontSize(size);
  }

  async function handleSubmit(data: {
    challenge: string;
    origin: string;
    destination: string;
    options: AdvancedOptions;
  }) {
    setSubmitted(data);
    setView('results');
    setLoading(true);
    setError(null);
    setRealRoutes(null);

    try {
      const response = await fetch('/api/routes/frontend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const routes = await response.json();
      setRealRoutes(routes);
      if (routes.length > 0) {
        setSelectedRouteId(routes[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch routes", err);
      setError("Failed to generate routes from backend. Using fallback data.");
      setSelectedRouteId(mockRoutes[0].id);
    } finally {
      setLoading(false);
    }
  }

  function handleBack() {
    setView('dashboard');
  }

  const routesToDisplay = realRoutes ?? mockRoutes;

  return (
    <div className="min-h-screen flex flex-col">
      <Header fontSize={fontSize} onFontSizeChange={handleFontSize} />
      <DoodleDecoration />

      <main className="relative z-10 flex-1 mx-auto w-full max-w-6xl px-4 sm:px-6 py-8 sm:py-10">
        {view === 'dashboard' ? (
          <DashboardView onSubmit={handleSubmit} />
        ) : (
          <ResultsView
            submitted={submitted}
            routes={routesToDisplay}
            selectedRouteId={selectedRouteId}
            onSelectRoute={setSelectedRouteId}
            onBack={handleBack}
            loading={loading}
            error={error}
          />
        )}
      </main>

      <footer className="relative z-10 border-t-[2.5px] border-ink/80 bg-paper-100">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-5 text-center">
          <p className="font-hand text-lg text-ink">CareGPS — calm routes, drawn with care.</p>
        </div>
      </footer>
    </div>
  );
}

function DashboardView({ onSubmit }: { onSubmit: (data: { challenge: string; origin: string; destination: string; options: AdvancedOptions }) => void }) {
  return (
    <div className="grid lg:grid-cols-5 gap-8 items-start">
      <div className="lg:col-span-3">
        <div className="mb-5">
          <p className="font-hand text-sky-dark text-lg">Hi there — let's find your calm way.</p>
          <h1 className="font-hand text-4xl sm:text-5xl text-ink stroke-hand leading-tight">
            Plan a route that fits <span className="text-leaf-dark">you</span>, not the other way around.
          </h1>
          <p className="text-ink-soft mt-3 max-w-xl">
            CareGPS shapes journeys around your needs — accessibility, confidence behind the wheel,
            comfort with lighting, and time to rest. Tell us what's hard, and we'll do the thinking.
          </p>
        </div>
        <InputPanel onSubmit={onSubmit} />
      </div>

      <aside className="lg:col-span-2 lg:sticky lg:top-24">
        <div className="bg-sky-soft border-[2.5px] border-ink rounded-doodle shadow-doodle p-5">
          <h2 className="font-hand text-2xl text-ink mb-2">How it works</h2>
          <ol className="space-y-3">
            {[
              { t: 'Describe your challenge', d: 'Plain words are enough — we translate them into route preferences.' },
              { t: 'Add your trip', d: 'Tell us where you\'re starting and where you\'re headed.' },
              { t: 'Pick your best route', d: 'Compare 2–3 options with pit stops and accessibility notes.' },
            ].map((s, i) => (
              <li key={s.t} className="flex gap-3">
                <span className="grid place-items-center w-8 h-8 rounded-full border-[2.5px] border-ink bg-paper text-ink font-bold shrink-0">
                  {i + 1}
                </span>
                <div>
                  <p className="font-semibold text-ink">{s.t}</p>
                  <p className="text-sm text-ink-soft">{s.d}</p>
                </div>
              </li>
            ))}
          </ol>
          <div className="scribble-divider my-4" aria-hidden />
          <p className="text-sm text-ink-soft">
            <Sparkles size={16} className="inline -mt-0.5 mr-1 text-sun-dark" aria-hidden />
            Built for people with disabilities, elderly travelers, new drivers and women.
          </p>
        </div>
      </aside>
    </div>
  );
}

function ResultsView({
  submitted,
  routes,
  selectedRouteId,
  onSelectRoute,
  onBack,
  loading,
  error,
}: {
  submitted: { challenge: string; origin: string; destination: string; options: AdvancedOptions } | null;
  routes: RouteOption[];
  selectedRouteId: string;
  onSelectRoute: (id: string) => void;
  onBack: () => void;
  loading: boolean;
  error: string | null;
}) {
  const route = routes.find((r) => r.id === selectedRouteId) ?? routes[0];
  const activeOptions = submitted ? Object.entries(submitted.options).filter(([, v]) => v).map(([k]) => k) : [];

  const optionLabels: Record<string, string> = {
    avoidHighways: 'Avoid highways',
    avoidUnpaved: 'Avoid unpaved',
    avoidPoorlyLit: 'Avoid poorly lit',
    avoidComplexRoundabouts: 'Avoid complex roundabouts',
    wheelchairAccessible: 'Wheelchair accessible',
    manyPitStops: 'Plenty of pit stops',
    womenSafety: 'Women safety',
    scenicRoute: 'Scenic route',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 min-h-[44px] px-4 py-2 rounded-doodle border-[2.5px] border-ink bg-paper shadow-doodleSm hover:bg-paper-200 font-semibold transition-colors"
        >
          <ArrowLeft size={20} aria-hidden /> New route
        </button>
        <div className="text-right">
          <p className="font-hand text-xl text-ink">Your calm routes</p>
          {submitted && (submitted.origin || submitted.destination) && (
            <p className="text-sm text-ink-soft">
              {submitted.origin || 'Current location'} → {submitted.destination || 'Destination'}
            </p>
          )}
        </div>
      </div>

      {/* Trip summary */}
      {(submitted?.challenge || activeOptions.length > 0) && (
        <div className="bg-paper-200 border-[2.5px] border-ink rounded-doodle p-4 shadow-doodleSm">
          {submitted?.challenge && (
            <p className="text-ink">
              <span className="font-bold">Your challenge: </span>
              <span className="font-hand text-lg">"{submitted.challenge}"</span>
            </p>
          )}
          {activeOptions.length > 0 && (
            <p className="text-sm text-ink-soft mt-2">
              <span className="font-semibold text-ink">Preferences: </span>
              {activeOptions.map((k) => optionLabels[k] ?? k).join(' · ')}
            </p>
          )}
        </div>
      )}

      <div className="grid lg:grid-cols-5 gap-6 items-start">
        {/* Map */}
        <div className="lg:col-span-3 lg:sticky lg:top-24">
          <div className="bg-paper rounded-doodle border-[2.5px] border-ink shadow-doodle p-3 relative z-0">
            {loading ? (
              <MapPlaceholder />
            ) : (
              <RouteMap route={route} />
            )}
          </div>
          {!loading && route && route.pitstops.length > 0 && (
            <div className="mt-4">
              <PitstopList pitstops={route.pitstops} />
            </div>
          )}
        </div>

        {/* Route options */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="font-hand text-2xl text-ink">Choose a route</h2>

          {loading && (
            <div className="p-6 bg-paper-200 rounded-doodle border-[2.5px] border-ink text-center">
              <p className="font-hand text-xl text-ink animate-pulse">Consulting the maps...</p>
              <p className="text-sm text-ink-soft mt-2">Connecting to local AI and routing services.</p>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-doodle border-[2.5px] border-red-200 mb-4">
              {error}
            </div>
          )}

          {!loading && routes.map((r) => (
            <RouteCard key={r.id} route={r} selected={r.id === selectedRouteId} onSelect={onSelectRoute} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
