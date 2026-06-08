import { Routes } from '@angular/router';
import { authGuard, profileGuard, adminGuard, subscriptionGuard } from './core/guards';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./pages/landing.component').then(m => m.LandingComponent) },
  { path: 'login', loadComponent: () => import('./pages/login.component').then(m => m.LoginComponent) },
  { path: 'signup', loadComponent: () => import('./pages/signup.component').then(m => m.SignupComponent) },

  { path: 'profiles', canActivate: [authGuard], loadComponent: () => import('./pages/profiles.component').then(m => m.ProfilesComponent) },
  { path: 'profiles/new', canActivate: [authGuard], loadComponent: () => import('./pages/profile-form.component').then(m => m.ProfileFormComponent) },
  { path: 'profiles/:id/edit', canActivate: [authGuard], loadComponent: () => import('./pages/profile-form.component').then(m => m.ProfileFormComponent) },

  { path: 'plans', canActivate: [authGuard], loadComponent: () => import('./pages/plans.component').then(m => m.PlansComponent) },
  { path: 'checkout/:code', canActivate: [authGuard], loadComponent: () => import('./pages/checkout.component').then(m => m.CheckoutComponent) },
  { path: 'billing', canActivate: [authGuard], loadComponent: () => import('./pages/billing.component').then(m => m.BillingComponent) },

  { path: 'browse', canActivate: [authGuard, subscriptionGuard, profileGuard], loadComponent: () => import('./pages/browse.component').then(m => m.BrowseComponent) },
  { path: 'search', canActivate: [authGuard, profileGuard], loadComponent: () => import('./pages/search.component').then(m => m.SearchComponent) },
  { path: 'my-list', canActivate: [authGuard, profileGuard], loadComponent: () => import('./pages/my-list.component').then(m => m.MyListComponent) },
  { path: 'genre/:slug', canActivate: [authGuard, profileGuard], loadComponent: () => import('./pages/genre.component').then(m => m.GenreComponent) },
  { path: 'title/:slug', canActivate: [authGuard, profileGuard], loadComponent: () => import('./pages/detail.component').then(m => m.DetailComponent) },
  { path: 'watch/:slug', canActivate: [authGuard, profileGuard], loadComponent: () => import('./pages/watch.component').then(m => m.WatchComponent) },

  { path: 'admin', canActivate: [authGuard, adminGuard], loadComponent: () => import('./pages/admin-dashboard.component').then(m => m.AdminDashboardComponent) },

  { path: '**', redirectTo: '' },
];
