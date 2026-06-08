import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Plan } from '../core/models';
import { NavComponent } from '../shared/nav.component';
import { AuthService } from '../core/auth.service';
import { ToastService } from '../core/toast.service';

@Component({
  selector: 'sb-checkout', standalone: true, imports: [CommonModule, FormsModule, RouterLink, NavComponent],
  template: `
  <sb-nav/>
  <div class="plans-page" style="max-width:520px">
    @if (plan(); as p) {
      <h1>Paiement</h1>
      <div class="plan-card">
        <h2>{{ p.name }}</h2>
        <div class="price">{{ p.price_eur }} € <small style="font-size:13px;color:var(--muted)">/mois</small></div>
        <p class="muted">{{ p.description }}</p>
        <form (ngSubmit)="pay()" style="display:flex;flex-direction:column;gap:12px;margin-top:18px">
          <input [(ngModel)]="card" name="c" placeholder="Numéro de carte (simulation)" maxlength="19" style="padding:12px;background:#222;border:1px solid #555;color:#fff;border-radius:4px">
          <div class="flex"><input [(ngModel)]="exp" name="e" placeholder="MM/AA" style="padding:12px;background:#222;border:1px solid #555;color:#fff;border-radius:4px;flex:1"><input [(ngModel)]="cvc" name="v" placeholder="CVC" maxlength="4" style="padding:12px;background:#222;border:1px solid #555;color:#fff;border-radius:4px;flex:1"></div>
          <button class="btn btn-primary" type="submit" [disabled]="loading()">{{ loading() ? '…' : 'Payer ' + p.price_eur + ' €' }}</button>
          <a routerLink="/plans" class="muted" style="text-align:center;font-size:13px">Changer de plan</a>
        </form>
      </div>
    }
  </div>`,
})
export class CheckoutComponent implements OnInit {
  private api = inject(ApiService); private route = inject(ActivatedRoute); private router = inject(Router);
  private auth = inject(AuthService); private toast = inject(ToastService);
  plan = signal<Plan | null>(null); loading = signal(false);
  card = '4242 4242 4242 4242'; exp = '12/30'; cvc = '123';
  ngOnInit() {
    const code = this.route.snapshot.paramMap.get('code')!;
    this.api.plans().subscribe(ps => this.plan.set(ps.find(p => p.code === code) || null));
  }
  pay() {
    const p = this.plan(); if (!p) return;
    this.loading.set(true);
    this.api.subscribe(p.code).subscribe({
      next: () => this.auth.fetchMe().subscribe(() => { this.loading.set(false); this.toast.show('Abonnement activé !'); this.router.navigateByUrl('/profiles'); }),
      error: () => { this.loading.set(false); this.toast.show('Paiement échoué'); },
    });
  }
}
