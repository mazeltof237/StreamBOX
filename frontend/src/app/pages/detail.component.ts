import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Title } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { CardComponent } from '../shared/card.component';
import { ToastService } from '../core/toast.service';

@Component({
  selector: 'sb-detail', standalone: true, imports: [CommonModule, RouterLink, NavComponent, CardComponent],
  template: `
  <sb-nav/>
  @if (title(); as t) {
    <section class="detail-hero" [style.background-image]="'url(' + t.backdrop + ')'">
      <div class="detail-meta"><span class="badge">{{ t.kind === 'movie' ? 'FILM' : 'SÉRIE' }}</span><span>{{ t.year }}</span><span>{{ t.maturity }}</span>@if (t.duration_minutes) {<span>{{ t.duration_minutes }} min</span>}<span>★ {{ t.rating }}</span></div>
      <h1>{{ t.title }}</h1><p class="desc">{{ t.description }}</p>
      <div class="flex">
        <a class="btn btn-primary" [routerLink]="['/watch', t.slug]">▶ Lecture</a>
        <button class="btn btn-light" (click)="toggleList()">{{ inList() ? '✓ Dans ma liste' : '＋ Ma liste' }}</button>
      </div>
      <div style="margin-top:18px;color:#b3b3b3;font-size:14px;max-width:700px">
        @if (t.cast) { <div><strong style="color:#fff">Distribution :</strong> {{ t.cast }}</div> }
        @if (t.director) { <div><strong style="color:#fff">Réalisation :</strong> {{ t.director }}</div> }
        @if (t.genres?.length) {
          <div><strong style="color:#fff">Genres :</strong>
            @for (g of t.genres; track g.id) { <a [routerLink]="['/genre', g.slug]">{{ g.name }}</a>@if (!$last) {, } }
          </div>
        }
      </div>
    </section>
    @if (t.episodes?.length) {
      <div style="padding:20px 40px">
        <h2>Épisodes</h2>
        @for (ep of t.episodes; track ep.id) {
          <div class="episode">
            <div class="thumb">@if (ep.thumbnail_url) {<img [src]="ep.thumbnail_url" alt="">}</div>
            <div><h3>S{{ ep.season }}E{{ ep.number }} – {{ ep.name }}</h3><p class="muted">{{ ep.description }}</p><small class="muted">{{ ep.duration_minutes }} min</small></div>
          </div>
        }
      </div>
    }
    @if (similar().length) { <div class="row"><h2>Titres similaires</h2><div class="row-scroll">@for (s of similar(); track s.id) {<sb-card [t]="s"/>}</div></div> }
  } @else { <div class="spinner"></div> }`,
})
export class DetailComponent implements OnInit {
  private api = inject(ApiService); private route = inject(ActivatedRoute); private toast = inject(ToastService);
  title = signal<Title | null>(null); similar = signal<Title[]>([]); inList = signal(false);
  ngOnInit() {
    this.route.paramMap.subscribe(p => {
      const slug = p.get('slug')!;
      this.api.title(slug).subscribe(t => this.title.set(t));
      this.api.similar(slug).subscribe(s => this.similar.set(s));
    });
  }
  toggleList() {
    const t = this.title(); if (!t) return;
    this.api.toggleWatchlist(t.slug).subscribe(r => { this.inList.set(r.added); this.toast.show(r.added ? 'Ajouté à ma liste' : 'Retiré de ma liste'); });
  }
}
