import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'sb-login', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink],
  template: `
  <div class="auth-body">
    <header class="auth-header">
      <a routerLink="/" class="logo"><span class="stream">Stream</span><span class="box">BOX.</span></a>
    </header>
    <div class="auth-box">
      <h1>Connexion</h1>
      @if (err()) { <div class="errors">{{ err() }}</div> }
      <form [formGroup]="form" (ngSubmit)="submit()">
        <div class="field">
          <input formControlName="username" placeholder="Nom d'utilisateur" autocomplete="username">
          @if (showErr('username', 'required')) { <small class="err">Nom d'utilisateur requis.</small> }
        </div>
        <div class="field">
          <input type="password" formControlName="password" placeholder="Mot de passe" autocomplete="current-password">
          @if (showErr('password', 'required')) { <small class="err">Mot de passe requis.</small> }
          @if (showErr('password', 'minlength')) { <small class="err">8 caractères minimum.</small> }
        </div>
        <button class="btn btn-primary" type="submit" [disabled]="loading() || form.invalid">
          @if (loading()) { <span class="spinner-inline"></span> Connexion… }
          @else { Se connecter }
        </button>
        <div class="signup-now">Nouveau sur StreamBOX ? <a routerLink="/signup">Inscrivez-vous</a>.</div>
        <div class="demo-hint">
          🎬 Démo : <strong>demo / demo12345</strong> &nbsp;·&nbsp; Admin : <strong>admin / admin12345</strong>
        </div>
      </form>
    </div>
  </div>`,
})
export class LoginComponent {
  private auth = inject(AuthService);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  err = signal('');
  loading = signal(false);

  form = this.fb.nonNullable.group({
    username: ['', [Validators.required]],
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
    const { username, password } = this.form.getRawValue();
    this.auth.login(username, password).subscribe({
      next: () => this.auth.fetchMe().subscribe(() => {
        this.loading.set(false);
        this.router.navigateByUrl('/profiles');
      }),
      error: (e) => {
        this.loading.set(false);
        this.err.set(e?.error?.detail || 'Identifiants invalides.');
      },
    });
  }
}
