import { Component, inject, signal, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../core/auth.service';
import { ProfileService } from '../core/profile.service';

@Component({
  selector: 'sb-nav', standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, FormsModule],
  template: `
  <nav class="app-nav" [class.scrolled]="scrolled()">
    <a routerLink="/browse" class="logo"><span class="stream">Stream</span><span class="box">BOX.</span></a>
    <div class="nav-links">
      <a routerLink="/browse" routerLinkActive="active">Accueil</a>
      <a routerLink="/genre/drame">Séries</a>
      <a routerLink="/genre/action">Films</a>
      <a routerLink="/my-list" routerLinkActive="active">Ma liste</a>
    </div>
    <div class="spacer"></div>
    <input type="search" placeholder="Titres, personnes, genres" [(ngModel)]="q" (keyup.enter)="go()"/>
    @if (profile.active(); as p) {
      <div class="nav-profile">
        <button class="profile-trigger" (click)="open.set(!open())">
          <div class="mini-avatar" [class]="'avatar-' + p.avatar_preset">{{ p.initial }}</div>
          <span style="font-size:14px">{{ p.name }}</span>
          <span>▾</span>
        </button>
        <div class="nav-menu" [class.open]="open()" (click)="open.set(false)">
          <a routerLink="/profiles">Changer de profil</a>
          <a routerLink="/billing">Mon abonnement</a>
          <a routerLink="/plans">Plans</a>
          @if (auth.isAdmin()) { <a routerLink="/admin">Tableau de bord</a> }
          <button type="button" (click)="logout()">Déconnexion</button>
        </div>
      </div>
    }
  </nav>`,
})
export class NavComponent {
  auth = inject(AuthService);
  profile = inject(ProfileService);
  router = inject(Router);
  open = signal(false);
  scrolled = signal(false);
  q = '';

  @HostListener('window:scroll') onScroll() { this.scrolled.set(window.scrollY > 30); }

  go() { if (this.q.trim()) this.router.navigate(['/search'], { queryParams: { q: this.q } }); }
  logout() { this.profile.clearActive(); this.auth.logout(); }
}
