import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Title } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { CardComponent } from '../shared/card.component';

@Component({
  selector: 'sb-search', standalone: true, imports: [CommonModule, NavComponent, CardComponent],
  template: `<sb-nav/><h1 class="page-title">Recherche : {{ q() }}</h1>
    <div class="grid">@for (t of results(); track t.id) {<sb-card [t]="t"/>}</div>
    @if (!results().length && q()) { <p style="text-align:center" class="muted">Aucun résultat.</p> }`,
})
export class SearchComponent implements OnInit {
  private api = inject(ApiService); private route = inject(ActivatedRoute);
  q = signal(''); results = signal<Title[]>([]);
  ngOnInit() {
    this.route.queryParamMap.subscribe(p => {
      const q = p.get('q') || ''; this.q.set(q);
      if (q) this.api.search(q).subscribe(r => this.results.set(r));
    });
  }
}
