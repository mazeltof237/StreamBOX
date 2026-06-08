import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'sb-landing', standalone: true, imports: [CommonModule, RouterLink, FormsModule],
  template: `
  <div class="landing-hero">
    <div class="landing-bg"></div>
    <div class="landing-fade"></div>
    <header class="landing-nav">
      <a routerLink="/" class="logo"><span class="stream">Stream</span><span class="box">BOX.</span></a>
      <a class="btn btn-primary small" routerLink="/login">Se connecter</a>
    </header>
    <div class="landing-content">
      <h1>Films, séries et bien plus en illimité.</h1>
      <p class="lead">À partir de 7,99 € / mois. Annulez à tout moment.</p>
      <p class="sub">Prêt à regarder ? Saisissez votre email pour créer votre compte.</p>
      <form class="email-cta" (ngSubmit)="go()">
        <input type="email" name="email" [(ngModel)]="email" placeholder="Adresse email" required>
        <button type="submit" class="btn btn-primary">Commencer ›</button>
      </form>
    </div>
  </div>
  <section class="features">
    <div class="feature">
      <div class="feature-text"><h2>Regardez où vous voulez.</h2><p>HD, Full HD, 4K HDR sur télé, ordi, tablette et mobile, sans frais cachés.</p></div>
      <div class="feature-img" style="background-image:url('https://picsum.photos/seed/sbox-tv/800/500')"></div>
    </div>
    <div class="feature reverse">
      <div class="feature-text"><h2>Profils Kids sécurisés.</h2><p>Code PIN, filtres de maturité, contenu adapté. La sérénité parentale.</p></div>
      <div class="feature-img" style="background-image:url('https://picsum.photos/seed/sbox-kids/800/500')"></div>
    </div>
    <div class="feature">
      <div class="feature-text"><h2>IA de recommandation.</h2><p>Notre moteur apprend vos goûts et vous propose le meilleur, chaque jour.</p></div>
      <div class="feature-img" style="background-image:url('https://picsum.photos/seed/sbox-ai/800/500')"></div>
    </div>
  </section>
  <section class="cta-band">
    <h2>Prêt ? 30 secondes suffisent.</h2>
    <a class="btn btn-primary" routerLink="/signup">Commencer maintenant ›</a>
  </section>
  <footer><div class="footer-content"><div class="flex"><a routerLink="/login">Connexion</a><a routerLink="/signup">Inscription</a></div><div>StreamBOX. © 2026</div></div></footer>`,
})
export class LandingComponent {
  email = '';
  constructor(private router: Router) {}
  go() { this.router.navigate(['/signup'], { queryParams: { email: this.email } }); }
}
