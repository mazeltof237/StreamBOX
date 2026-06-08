import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Plan, Subscription } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'sb-plans', standalone: true, imports: [CommonModule, RouterLink, NavComponent],
  template: `
  <sb-nav/>
  <section class="plans-page">
    <h1>Choisissez votre plan</h1>
    <p class="muted">Annulez à tout moment.</p>
    <div class="plans-grid">
      @for (p of plans(); track p.id) {
        <div class="plan-card" [class.is-current]="current()?.plan?.id === p.id">
          <h2>{{ p.name }}</h2>
          <div class="price">{{ p.price_eur }} €<small style="font-size:14px;color:var(--muted)">/mois</small></div>
          <ul>
            <li>Qualité {{ p.quality }}</li>
            <li>{{ p.max_profiles }} profils</li>
            <li>{{ p.simultaneous_streams }} écran(s)</li>
            <li>{{ p.description }}</li>
          </ul>
          @if (current()?.plan?.id === p.id) { <button class="btn btn-light" disabled>Plan actuel</button> }
          @else { <a class="btn btn-primary" [routerLink]="['/checkout', p.code]">S'abonner</a> }
        </div>
      }
    </div>
  </section>`,
})
export class PlansComponent implements OnInit {
  private api = inject(ApiService); private auth = inject(AuthService);
  plans = signal<Plan[]>([]); current = signal<Subscription | null>(null);
  ngOnInit() {
    this.api.plans().subscribe(p => this.plans.set(p));
    this.current.set(this.auth.subscription());
  }
}
