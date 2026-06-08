import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Title } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { CardComponent } from '../shared/card.component';

@Component({
  selector: 'sb-genre', standalone: true, imports: [CommonModule, NavComponent, CardComponent],
  template: `<sb-nav/><h1 class="page-title">{{ slug() | titlecase }}</h1>
    <div class="grid">@for (t of items(); track t.id) {<sb-card [t]="t"/>}</div>`,
})
export class GenreComponent implements OnInit {
  private api = inject(ApiService); private route = inject(ActivatedRoute);
  slug = signal(''); items = signal<Title[]>([]);
  ngOnInit() {
    this.route.paramMap.subscribe(p => {
      const s = p.get('slug')!; this.slug.set(s);
      this.api.byGenre(s).subscribe(items => this.items.set(items));
    });
  }
}
