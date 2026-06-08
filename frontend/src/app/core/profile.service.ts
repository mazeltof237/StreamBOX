import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Profile } from './models';
import { environment } from '../../environments/environment';

const ACTIVE = 'sb_profile';
const api = (p: string) => `${environment.apiBase}${p}`;

@Injectable({ providedIn: 'root' })
export class ProfileService {
  profiles = signal<Profile[]>([]);
  private _active = signal<Profile | null>(this.loadActive());
  active = computed(() => this._active());
  activeProfileId = computed(() => this._active()?.id ?? null);

  constructor(private http: HttpClient) {}

  loadActive(): Profile | null {
    try { const raw = localStorage.getItem(ACTIVE); return raw ? JSON.parse(raw) : null; } catch { return null; }
  }
  setActive(p: Profile | null) {
    this._active.set(p);
    if (p) localStorage.setItem(ACTIVE, JSON.stringify(p));
    else localStorage.removeItem(ACTIVE);
  }
  clearActive() { this.setActive(null); }

  list(): Observable<Profile[]> {
    return this.http.get<Profile[]>(api('/api/profiles/')).pipe(tap(p => this.profiles.set(p)));
  }
  create(data: Partial<Profile> & { pin?: string }): Observable<Profile> { return this.http.post<Profile>(api('/api/profiles/'), data); }
  update(id: number, data: Partial<Profile> & { pin?: string }): Observable<Profile> { return this.http.patch<Profile>(api(`/api/profiles/${id}/`), data); }
  remove(id: number): Observable<void> { return this.http.delete<void>(api(`/api/profiles/${id}/`)); }
  verifyPin(id: number, pin: string): Observable<{ ok: boolean; profile: Profile }> {
    return this.http.post<{ ok: boolean; profile: Profile }>(api(`/api/profiles/${id}/verify_pin/`), { pin });
  }
}
