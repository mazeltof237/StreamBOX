import { AfterViewInit, Component, ElementRef, OnInit, ViewChild, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../core/api.service';
import { NavComponent } from '../shared/nav.component';
import Chart from 'chart.js/auto';

@Component({
  selector: 'sb-admin', standalone: true, imports: [CommonModule, NavComponent],
  template: `
  <sb-nav/>
  <div class="dash">
    <h1 style="margin-top:0">Tableau de bord admin</h1>
    @if (data(); as d) {
      <div class="kpi-grid">
        <div class="kpi"><h3>Utilisateurs</h3><div class="v">{{ d.kpi.users }}</div></div>
        <div class="kpi"><h3>Profils</h3><div class="v">{{ d.kpi.profiles }}</div></div>
        <div class="kpi"><h3>Profils Kids</h3><div class="v">{{ d.kpi.kids }}</div></div>
        <div class="kpi"><h3>Titres</h3><div class="v">{{ d.kpi.titles }}</div></div>
        <div class="kpi"><h3>Vues</h3><div class="v">{{ d.kpi.views }}</div></div>
        <div class="kpi"><h3>Heures vues</h3><div class="v">{{ d.kpi.hours }}h</div></div>
        <div class="kpi"><h3>Abos actifs</h3><div class="v">{{ d.kpi.active_subs }}</div></div>
        <div class="kpi"><h3>Revenus 30j</h3><div class="v">{{ d.kpi.revenue_30 }} €</div></div>
        <div class="kpi"><h3>Revenus total</h3><div class="v">{{ d.kpi.revenue_total }} €</div></div>
      </div>
      <div class="dash-grid">
        <div class="section-card"><h3>Vues sur 14 jours</h3><canvas #chart1 height="120"></canvas></div>
        <div class="section-card"><h3>Top genres</h3><canvas #chart2 height="120"></canvas></div>
      </div>
      <div class="dash-grid" style="margin-top:20px">
        <div class="section-card">
          <h3>Top titres</h3>
          <table style="width:100%"><tbody>@for (t of d.top_titles; track t.title) {<tr><td style="padding:6px 0">{{ t.title }}</td><td style="text-align:right" class="muted">{{ t.views }} vues</td></tr>}</tbody></table>
        </div>
        <div class="section-card">
          <h3>Abonnements par plan</h3>
          <table style="width:100%"><tbody>@for (p of d.by_plan; track p.plan__name) {<tr><td style="padding:6px 0">{{ p.plan__name }}</td><td style="text-align:right" class="muted">{{ p.c }}</td></tr>}</tbody></table>
        </div>
      </div>
    } @else { <div class="spinner"></div> }
  </div>`,
})
export class AdminDashboardComponent implements OnInit, AfterViewInit {
  private api = inject(ApiService);
  data = signal<any>(null);
  @ViewChild('chart1') c1?: ElementRef<HTMLCanvasElement>;
  @ViewChild('chart2') c2?: ElementRef<HTMLCanvasElement>;

  ngOnInit() { this.api.adminDashboard().subscribe(d => { this.data.set(d); setTimeout(() => this.draw(), 50); }); }
  ngAfterViewInit() {}
  draw() {
    const d = this.data(); if (!d || !this.c1 || !this.c2) return;
    new Chart(this.c1.nativeElement, {
      type: 'line',
      data: { labels: d.days.map((x: any) => x.d), datasets: [{ label: 'Vues', data: d.days.map((x: any) => x.c), borderColor: '#00bf63', backgroundColor: 'rgba(0,191,99,.2)', tension: .3, fill: true }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
    new Chart(this.c2.nativeElement, {
      type: 'doughnut',
      data: { labels: d.top_genres.map((g: any) => g.name), datasets: [{ data: d.top_genres.map((g: any) => g.views), backgroundColor: ['#00bf63','#3b82f6','#a855f7','#facc15','#ef4444','#14b8a6','#f97316','#ec4899'] }] },
      options: { plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } } },
    });
  }
}
