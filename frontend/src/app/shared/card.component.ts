import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Title } from '../core/models';

@Component({
  selector: 'sb-card', standalone: true, imports: [CommonModule, RouterLink],
  template: `
  <a class="card" [routerLink]="['/title', t.slug]">
    <img [src]="t.poster || fallback()" [alt]="t.title" loading="lazy" (error)="onErr($event)">
    <div class="card-info">
      <strong>{{ t.title }}</strong>
      <small>{{ t.year }} · {{ t.kind_display || (t.kind === 'movie' ? 'Film' : 'Série') }} · {{ t.maturity }}</small>
    </div>
  </a>`,
})
export class CardComponent {
  @Input({ required: true }) t!: Title;
  fallback() { return `https://picsum.photos/seed/${this.t.slug}/400/600`; }
  onErr(e: Event) { (e.target as HTMLImageElement).src = this.fallback(); }
}
