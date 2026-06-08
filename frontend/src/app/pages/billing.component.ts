import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Subscription, Payment } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { ToastService } from '../core/toast.service';

@Component({
  selector: 'sb-billing', standalone: true, imports: [CommonModule, RouterLink, NavComponent, DatePipe],
  template: `
  <sb-nav/>
  <div class="plans-page" style="max-width:720px">
    <h1>Mon abonnement</h1>
    @if (sub(); as s) {
      <div class="plan-card is-current">
        <h2>{{ s.plan.name }}</h2>
        <p class="muted">Statut : {{ s.status }} · Renouvellement {{ s.renews_at | date:'dd/MM/yyyy' }}</p>
        <div class="flex">
          <a routerLink="/plans" class="btn btn-light">Changer de plan</a>
          <button class="btn btn-ghost" (click)="cancel()">Annuler l'abonnement</button>
        </div>
      </div>
    } @else { <p class="muted">Aucun abonnement actif.</p><a routerLink="/plans" class="btn btn-primary">Voir les plans</a> }
    <h2 style="margin-top:30px">Historique de paiement</h2>
    <table style="width:100%;border-collapse:collapse">
      <thead><tr style="border-bottom:1px solid #333"><th style="text-align:left;padding:10px" class="muted">Date</th><th style="text-align:left" class="muted">Plan</th><th style="text-align:right" class="muted">Montant</th></tr></thead>
      <tbody>@for (p of payments(); track p.id) {<tr style="border-bottom:1px solid #222"><td style="padding:10px">{{ p.created_at | date:'dd/MM/yyyy' }}</td><td>{{ p.plan }}</td><td style="text-align:right">{{ p.amount }} €</td></tr>}</tbody>
    </table>
  </div>`,
})
export class BillingComponent implements OnInit {
  private api = inject(ApiService); private toast = inject(ToastService);
  sub = signal<Subscription | null>(null); payments = signal<Payment[]>([]);
  ngOnInit() { this.load(); }
  load() { this.api.billing().subscribe(b => { this.sub.set(b.subscription); this.payments.set(b.payments); }); }
  cancel() { if (confirm('Confirmer l\'annulation ?')) this.api.cancelSubscription().subscribe(() => { this.toast.show('Abonnement annulé'); this.load(); }); }
}
