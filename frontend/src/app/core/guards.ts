import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';
import { ProfileService } from './profile.service';
import { catchError, map, of } from 'rxjs';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  if (!auth.accessToken) { router.navigateByUrl('/login'); return false; }
  if (auth.user()) return true;
  return auth.fetchMe().pipe(
    map(() => true),
    catchError(() => { auth.clear(); router.navigateByUrl('/login'); return of(false); })
  );
};

export const subscriptionGuard: CanActivateFn = () => {
  const auth = inject(AuthService); const router = inject(Router);
  if (auth.hasActiveSubscription()) return true;
  router.navigateByUrl('/plans');
  return false;
};

export const profileGuard: CanActivateFn = () => {
  const ps = inject(ProfileService); const router = inject(Router);
  if (ps.active()) return true;
  router.navigateByUrl('/profiles');
  return false;
};

export const adminGuard: CanActivateFn = () => {
  const auth = inject(AuthService); const router = inject(Router);
  if (auth.isAdmin()) return true;
  router.navigateByUrl('/browse');
  return false;
};
