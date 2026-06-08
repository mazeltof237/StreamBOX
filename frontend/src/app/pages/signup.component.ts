import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'sb-signup', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
  <div class="auth-body">
    <header class="auth-header">
      <a routerLink="/" class="logo"><span class="stream">Stream</span><span class="box">BOX.</span></a>
    </header>
    <div class="auth-box">
      <h1>Créer un compte</h1>
      @if (err()) { <div class="errors">{{ err() }}</div> }
      <form [formGroup]="form" (ngSubmit)="submit()">
        <div class="field">
          <input formControlName="username" placeholder="Nom d'utilisateur" autocomplete="username">
          @if (showErr('username', 'required')) { <small class="err">Requis.</small> }
          @if (showErr('username', 'minlength')) { <small class="err">3 caractères minimum.</small> }
        </div>
        <div class="field">
          <input type="email" formControlName="email" placeholder="Adresse email" autocomplete="email">
          @if (showErr('email', 'required')) { <small class="err">Email requis.</small> }
          @if (showErr('email', 'email')) { <small class="err">Format email invalide.</small> }
        </div>
        <div class="field">
          <input type="password" formControlName="password" placeholder="Mot de passe (8+ caractères)" autocomplete="new-password">
          @if (showErr('password', 'required')) { <small class="err">Mot de passe requis.</small> }
          @if (showErr('password', 'minlength')) { <small class="err">8 caractères minimum.</small> }
        </div>
        <button class="btn btn-primary" type="submit" [disabled]="loading() || form.invalid">
          @if (loading()) { <span class="spinner-inline"></span> Création… }
          @else { S'inscrire }
        </button>
        <div class="signup-now">Déjà un compte ? <a routerLink="/login">Se connecter</a>.</div>
      </form>
    </div>
  </div>`,
})
export class SignupComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private fb = inject(FormBuilder);

  err = signal('');
  loading = signal(false);

  form = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: [this.route.snapshot.queryParamMap.get('email') || '', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  showErr(name: string, code: string) {
    const c = this.form.get(name);
    return !!c && c.touched && c.hasError(code);
  }

  submit() {
    this.form.markAllAsTouched();
    if (this.form.invalid) return;
    this.err.set(''); this.loading.set(true);
    const { username, email, password } = this.form.getRawValue();
    this.auth.signup(username, email, password).subscribe({
      next: () => this.auth.fetchMe().subscribe(() => {
        this.loading.set(false);
        this.router.navigateByUrl('/plans');
      }),
      error: (e) => {
        this.loading.set(false);
        const d = e?.error;
        this.err.set(typeof d === 'string'
          ? d
          : (d?.password?.[0] || d?.username?.[0] || d?.email?.[0] || 'Inscription impossible.'));
      },
    });
  }
}
