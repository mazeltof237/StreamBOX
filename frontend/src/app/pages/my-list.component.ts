import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../core/api.service';
import { Title } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { CardComponent } from '../shared/card.component';

@Component({
  selector: 'sb-my-list', standalone: true, imports: [CommonModule, NavComponent, CardComponent],
  template: `<sb-nav/><h1 class="page-title">Ma liste</h1>
    <div class="grid">@for (t of items(); track t.id) {<sb-card [t]="t"/>}</div>
    @if (!items().length) { <p style="text-align:center" class="muted">Votre liste est vide.</p> }`,
})
export class MyListComponent implements OnInit {
  private api = inject(ApiService);
  items = signal<Title[]>([]);
  ngOnInit() { this.api.watchlist().subscribe(rs => this.items.set(rs.map(r => r.title))); }
}
