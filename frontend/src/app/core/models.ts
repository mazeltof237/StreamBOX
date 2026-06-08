export interface User { id: number; username: string; email: string; is_staff: boolean; }
export interface Profile { id: number; name: string; avatar_preset: string; is_kid: boolean; has_pin: boolean; initial: string; created_at?: string; }
export interface Genre { id: number; name: string; slug: string; }
export interface Episode { id: number; season: number; number: number; name: string; description: string; duration_minutes: number; video_url: string; thumbnail_url: string; }
export interface Title {
  id: number; slug: string; title: string; year: number; kind: 'movie' | 'series';
  kind_display?: string; maturity: string; rating: number;
  poster: string; backdrop: string; is_featured?: boolean; is_trending?: boolean;
  description?: string; duration_minutes?: number; cast?: string; director?: string;
  video_url?: string; trailer_url?: string; genres?: Genre[]; episodes?: Episode[];
}
export interface Plan { id: number; code: string; name: string; price_eur: string; quality: string; max_profiles: number; simultaneous_streams: number; description: string; is_active: boolean; }
export interface Subscription { plan: Plan; status: string; started_at: string; renews_at: string; active: boolean; }
export interface Payment { id: number; plan: string; amount: string; method: string; succeeded: boolean; created_at: string; }
export interface Browse {
  hero: Title | null; trending: Title[]; movies: Title[]; series: Title[];
  history: Title[]; recommended: Title[]; rows_by_genre: { genre: Genre; items: Title[] }[]; genres: Genre[];
}
