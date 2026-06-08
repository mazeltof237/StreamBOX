import { Injectable, computed, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { User, Subscription } from './models';
import { environment } from '../../environments/environment';

const ACCESS = 'sb_access';
const REFRESH = 'sb_refresh';
const api = (path: string) => `${environment.apiBase}${path}`;

@Injectable({ providedIn: 'root' })
export class AuthService {
  user = signal<User | null>(null);
  subscription = signal<Subscription | null>(null);
  isLoggedIn = computed(() => this.user() !== null);
  isAdmin = computed(() => this.user()?.is_staff === true);
  hasActiveSubscription = computed(() => !!this.subscription()?.active || this.isAdmin());

  constructor(private http: HttpClient, private router: Router) {}

  get accessToken() { return localStorage.getItem(ACCESS); }
  get refreshToken() { return localStorage.getItem(REFRESH); }
  setTokens(access: string, refresh?: string) {
    localStorage.setItem(ACCESS, access);
    if (refresh) localStorage.setItem(REFRESH, refresh);
  }
  clear() {
    localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH);
    this.user.set(null); this.subscription.set(null);
    localStorage.removeItem('sb_profile');
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<{ access: string; refresh: string }>(api('/api/auth/login/'), { username, password })
      .pipe(tap(r => { this.setTokens(r.access, r.refresh); }));
  }
  signup(username: string, email: string, password: string): Observable<any> {
    return this.http.post<{ access: string; refresh: string; user: User }>(api('/api/auth/signup/'), { username, email, password })
      .pipe(tap(r => { this.setTokens(r.access, r.refresh); this.user.set(r.user); }));
  }
  refresh(): Observable<any> {
    return this.http.post<{ access: string }>(api('/api/auth/refresh/'), { refresh: this.refreshToken })
      .pipe(tap(r => this.setTokens(r.access)));
  }
  fetchMe(): Observable<any> {
    return this.http.get<{ user: User; subscription: Subscription | null }>(api('/api/auth/me/'))
      .pipe(tap(r => { this.user.set(r.user); this.subscription.set(r.subscription); }));
  }
  logout() { this.clear(); this.router.navigateByUrl('/login'); }
}
