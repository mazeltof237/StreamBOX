import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProfileService } from '../core/profile.service';

const PRESETS = [
  { code: 'kids', label: 'Rouge' }, { code: 'fafi', label: 'Bleu' }, { code: 'nina', label: 'Violet' },
  { code: 'nicky', label: 'Vert eau' }, { code: 'gold', label: 'Or' }, { code: 'dark', label: 'Sombre' },
];

@Component({
  selector: 'sb-profile-form', standalone: true, imports: [CommonModule, FormsModule, RouterLink],
  template: `
  <div class="profiles-page">
    <div style="width:100%;max-width:500px">
      <h1>{{ isEdit() ? 'Modifier le profil' : 'Nouveau profil' }}</h1>
      <form (ngSubmit)="submit()" style="display:flex;flex-direction:column;gap:14px">
        <input name="n" [(ngModel)]="name" placeholder="Nom du profil" required style="padding:14px;background:#222;border:1px solid #555;color:#fff;border-radius:4px">
        <div>
          <label class="muted">Avatar</label>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px">
            @for (p of presets; track p.code) {
              <div (click)="avatar = p.code" class="profile-avatar" [class]="'avatar-' + p.code" [style.width.px]="60" [style.height.px]="60" [style.fontSize.px]="24" [style.outline]="avatar === p.code ? '3px solid #fff' : 'none'">{{ name[0]?.toUpperCase() || '?' }}</div>
            }
          </div>
        </div>
        <label class="flex"><input type="checkbox" [(ngModel)]="isKid" name="k"> Profil Kids (filtre maturité ALL/10)</label>
        <input name="pin" [(ngModel)]="pin" maxlength="4" inputmode="numeric" placeholder="Code PIN 4 chiffres (optionnel)" style="padding:14px;background:#222;border:1px solid #555;color:#fff;border-radius:4px">
        @if (err()) { <div class="err">{{ err() }}</div> }
        <div class="flex" style="margin-top:8px">
          <button class="btn btn-primary" type="submit">Enregistrer</button>
          <a routerLink="/profiles" class="btn btn-ghost">Annuler</a>
          @if (isEdit()) { <button type="button" class="btn btn-ghost" (click)="del()" style="margin-left:auto;color:#ff6b6b">Supprimer</button> }
        </div>
      </form>
    </div>
  </div>`,
})
export class ProfileFormComponent implements OnInit {
  private ps = inject(ProfileService); private router = inject(Router); private route = inject(ActivatedRoute);
  presets = PRESETS;
  id = signal<number | null>(null);
  isEdit = () => this.id() !== null;
  name = ''; avatar = 'fafi'; isKid = false; pin = ''; err = signal('');

  ngOnInit() {
    const idStr = this.route.snapshot.paramMap.get('id');
    if (idStr) {
      const id = +idStr; this.id.set(id);
      this.ps.list().subscribe(ps => {
        const p = ps.find(x => x.id === id);
        if (p) { this.name = p.name; this.avatar = p.avatar_preset; this.isKid = p.is_kid; }
      });
    }
  }
  submit() {
    const data = { name: this.name, avatar_preset: this.avatar, is_kid: this.isKid, pin: this.pin };
    const op = this.isEdit() ? this.ps.update(this.id()!, data) : this.ps.create(data);
    op.subscribe({ next: () => this.router.navigateByUrl('/profiles'),
      error: (e) => this.err.set(e?.error?.detail || e?.error?.[0] || 'Erreur') });
  }
  del() { if (confirm('Supprimer ce profil ?')) this.ps.remove(this.id()!).subscribe(() => this.router.navigateByUrl('/profiles')); }
}
