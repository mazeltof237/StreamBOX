import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ToastComponent } from './shared/toast.component';

@Component({
  selector: 'sb-root',
  standalone: true,
  imports: [RouterOutlet, ToastComponent],
  template: `<router-outlet/><sb-toast/>`,
})
export class AppComponent {}
