import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Browse } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { CardComponent } from '../shared/card.component';
import { ProfileService } from '../core/profile.service';

@Component({
  selector: 'sb-browse', standalone: true, imports: [CommonModule, RouterLink, NavComponent, CardComponent],
  template: `
  <sb-nav/>
  @if (data(); as d) {
    @if (d.hero; as h) {
      <section class="hero">
        <div class="hero-bg" [style.background-image]="'url(' + h.backdrop + ')'"></div>
        <div class="hero-fade"></div>
        <div class="hero-content">
          <div class="meta"><span class="badge">EN VEDETTE</span><span>{{ h.year }}</span><span>{{ h.maturity }}</span><span>★ {{ h.rating }}</span></div>
          <h1>{{ h.title }}</h1><p>{{ h.description }}</p>
          <div class="flex">
            <a class="btn btn-primary" [routerLink]="['/watch', h.slug]">▶ Lecture</a>
            <a class="btn btn-light" [routerLink]="['/title', h.slug]">ⓘ Plus d'infos</a>
          </div>
        </div>
      </section>
    }
    @if (d.history.length) { <div class="row"><h2>Continuer à regarder</h2><div class="row-scroll">@for (t of d.history; track t.id) {<sb-card [t]="t"/>}</div></div> }
    @if (d.recommended.length) { <div class="row"><h2>✨ Recommandé pour {{ profile.active()?.name }}</h2><div class="row-scroll">@for (t of d.recommended; track t.id) {<sb-card [t]="t"/>}</div></div> }
    @if (d.trending.length) { <div class="row"><h2>Tendances</h2><div class="row-scroll">@for (t of d.trending; track t.id) {<sb-card [t]="t"/>}</div></div> }
    @if (d.movies.length) { <div class="row"><h2>Films populaires</h2><div class="row-scroll">@for (t of d.movies; track t.id) {<sb-card [t]="t"/>}</div></div> }
    @if (d.series.length) { <div class="row"><h2>Séries</h2><div class="row-scroll">@for (t of d.series; track t.id) {<sb-card [t]="t"/>}</div></div> }
    @for (r of d.rows_by_genre; track r.genre.id) { <div class="row"><h2>{{ r.genre.name }}</h2><div class="row-scroll">@for (t of r.items; track t.id) {<sb-card [t]="t"/>}</div></div> }
  } @else { <div class="spinner"></div> }`,
})
export class BrowseComponent implements OnInit {
  private api = inject(ApiService); profile = inject(ProfileService);
  data = signal<Browse | null>(null);
  ngOnInit() { this.api.browse().subscribe(d => this.data.set(d)); }
}
