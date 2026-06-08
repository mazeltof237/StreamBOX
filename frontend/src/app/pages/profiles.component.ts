import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ProfileService } from '../core/profile.service';
import { Profile } from '../core/models';

@Component({
  selector: 'sb-profiles', standalone: true, imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="profiles-page">
    <div style="width:100%;max-width:1000px">
      <h1>Qui regarde ?</h1>
      <div class="profile-grid">
        @for (p of profiles(); track p.id) {
          <div class="profile-tile" (click)="select(p)">
            <div class="profile-avatar" [class]="'avatar-' + p.avatar_preset">{{ p.initial }}</div>
            <span>{{ p.name }}</span>
            @if (p.is_kid) { <small style="color:var(--sb-green)">KIDS</small> }
            <a [routerLink]="['/profiles', p.id, 'edit']" style="color:#888;font-size:12px">Modifier</a>
          </div>
        }
        <a routerLink="/profiles/new" class="profile-tile">
          <div class="profile-avatar" style="background:#222;color:#fff">+</div>
          <span>Ajouter</span>
        </a>
      </div>
      @if (pinFor()) {
        <div style="text-align:center;margin-top:30px">
          <h3>PIN pour {{ pinFor()!.name }}</h3>
          <input maxlength="4" inputmode="numeric" [(ngModel)]="pin" style="font-size:24px;text-align:center;width:140px;padding:10px;border-radius:4px;border:1px solid #555;background:#222;color:#fff">
          <div style="margin-top:10px"><button class="btn btn-primary" (click)="verifyPin()">Valider</button></div>
          @if (pinErr()) { <div class="err">{{ pinErr() }}</div> }
        </div>
      }
    </div>
  </div>`,
})
export class ProfilesComponent implements OnInit {
  private ps = inject(ProfileService); private router = inject(Router);
  profiles = signal<Profile[]>([]);
  pinFor = signal<Profile | null>(null); pin = ''; pinErr = signal('');

  ngOnInit() { this.ps.list().subscribe(ps => this.profiles.set(ps)); }
  select(p: Profile) {
    if (p.has_pin) { this.pinFor.set(p); return; }
    this.ps.setActive(p); this.router.navigateByUrl('/browse');
  }
  verifyPin() {
    const p = this.pinFor(); if (!p) return;
    this.ps.verifyPin(p.id, this.pin).subscribe({
      next: (r) => { this.ps.setActive(r.profile); this.router.navigateByUrl('/browse'); },
      error: () => this.pinErr.set('PIN incorrect'),
    });
  }
}
