export type Pitstop = {
  id: string;
  name: string;
  type: 'rest' | 'coffee' | 'restroom' | 'accessible';
  distance: string;
  note: string;
};

export type RouteOption = {
  id: string;
  label: string;
  emoji: string;
  duration: string;
  distance: string;
  why: string[];
  pitstops: Pitstop[];
  badge: { text: string; tone: 'leaf' | 'sky' | 'sun' };
  polyline?: string;
};

export const mockRoutes: RouteOption[] = [
  {
    id: 'calm-arterials',
    label: 'The Calm Arterials',
    emoji: 'Leafy backstreets',
    duration: '34 min',
    distance: '12.4 km',
    why: ['No highway merges', '2 accessible pitstops', 'Well-lit the whole way'],
    badge: { text: 'Gentlest', tone: 'leaf' },
    pitstops: [
      { id: 'p1', name: 'Riverside Park Bench', type: 'rest', distance: '3.1 km', note: 'Shaded bench, flat path, step-free access' },
      { id: 'p2', name: 'Maple Café', type: 'coffee', distance: '6.8 km', note: 'Open until 9pm, quiet seating, ramp entrance' },
      { id: 'p3', name: 'Lakeside Restrooms', type: 'restroom', distance: '9.2 km', note: 'Accessible stall, automatic doors' },
      { id: 'p4', name: 'Community Center Stop', type: 'accessible', distance: '11.0 km', note: 'Designated drop-off, sheltered waiting' },
    ],
  },
  {
    id: 'main-with-breaks',
    label: 'Main Roads, Easy Breaks',
    emoji: 'Familiar avenues',
    duration: '26 min',
    distance: '11.1 km',
    why: ['Simple intersections', '1 accessible pitstop', 'Bright storefronts'],
    badge: { text: 'Balanced', tone: 'sky' },
    pitstops: [
      { id: 'p1', name: 'Sunrise Plaza Bench', type: 'rest', distance: '4.0 km', note: 'Wide sidewalk, bench with armrest' },
      { id: 'p2', name: 'Corner Bean Coffee', type: 'coffee', distance: '7.5 km', note: 'Drive-through option, low-noise hours' },
      { id: 'p3', name: 'Plaza Restrooms', type: 'restroom', distance: '8.6 km', note: 'Accessible, well-maintained' },
    ],
  },
  {
    id: 'scenic-slow',
    label: 'Scenic & Slow',
    emoji: 'Parkway route',
    duration: '41 min',
    distance: '14.8 km',
    why: ['Most pitstops', 'No complex roundabouts', 'Calm, low traffic'],
    badge: { text: 'Most restful', tone: 'sun' },
    pitstops: [
      { id: 'p1', name: 'Garden Rest Bench', type: 'rest', distance: '2.4 km', note: 'Quiet garden, shaded seating' },
      { id: 'p2', name: 'Garden Café', type: 'coffee', distance: '5.1 km', note: 'Outdoor seating, ramp, calm music' },
      { id: 'p3', name: 'Harbor Restrooms', type: 'restroom', distance: '8.9 km', note: 'Accessible, baby-changing facilities' },
      { id: 'p4', name: 'Harbor Accessible Stop', type: 'accessible', distance: '12.3 km', note: 'Sheltered, real-time arrival board' },
    ],
  },
];
