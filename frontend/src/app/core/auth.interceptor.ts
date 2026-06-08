import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';
import { ProfileService } from './profile.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const profileSvc = inject(ProfileService);
  let modified = req;
  const setHeaders: Record<string, string> = {};
  const token = auth.accessToken;
  if (token && req.url.startsWith('/api')) setHeaders['Authorization'] = `Bearer ${token}`;
  const profileId = profileSvc.activeProfileId();
  if (profileId && req.url.startsWith('/api')) setHeaders['X-Profile-Id'] = String(profileId);
  if (Object.keys(setHeaders).length) modified = req.clone({ setHeaders });

  return next(modified).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401 && auth.refreshToken && !req.url.includes('/auth/')) {
        return auth.refresh().pipe(
          switchMap(() => next(req.clone({ setHeaders: { ...setHeaders, Authorization: `Bearer ${auth.accessToken}` } }))),
          catchError(() => { auth.logout(); return throwError(() => err); })
        );
      }
      return throwError(() => err);
    })
  );
};
