import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Browse, Title, Plan, Subscription, Payment } from './models';
import { environment } from '../../environments/environment';

/** Construit l'URL complète vers l'API (utilise environment.apiBase). */
const api = (path: string) => `${environment.apiBase}${path}`;

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  browse(): Observable<Browse> { return this.http.get<Browse>(api('/api/browse/')); }
  title(slug: string): Observable<Title> { return this.http.get<Title>(api(`/api/titles/${slug}/`)); }
  similar(slug: string): Observable<Title[]> { return this.http.get<Title[]>(api(`/api/titles/${slug}/similar/`)); }
  search(q: string): Observable<Title[]> { return this.http.get<Title[]>(api(`/api/titles/?q=${encodeURIComponent(q)}`)); }
  byGenre(slug: string): Observable<Title[]> { return this.http.get<Title[]>(api(`/api/titles/?genre=${slug}`)); }
  toggleWatchlist(slug: string) { return this.http.post<{ added: boolean }>(api(`/api/titles/${slug}/watchlist/`), {}); }
  saveProgress(slug: string, seconds: number, finished = false) { return this.http.post<any>(api(`/api/titles/${slug}/progress/`), { seconds, finished }); }
  watchlist() { return this.http.get<{ title: Title; added_at: string }[]>(api('/api/watchlist/')); }
  history() { return this.http.get<{ title: Title; progress_seconds: number; finished: boolean }[]>(api('/api/history/')); }

  plans(): Observable<Plan[]> { return this.http.get<Plan[]>(api('/api/plans/')); }
  subscribe(code: string): Observable<{ subscription: Subscription }> { return this.http.post<{ subscription: Subscription }>(api('/api/subscribe/'), { plan_code: code }); }
  cancelSubscription() { return this.http.post(api('/api/subscription/cancel/'), {}); }
  billing(): Observable<{ subscription: Subscription | null; payments: Payment[] }> { return this.http.get<{ subscription: Subscription | null; payments: Payment[] }>(api('/api/billing/')); }

  adminDashboard(): Observable<any> { return this.http.get(api('/api/admin/dashboard/')); }
}
