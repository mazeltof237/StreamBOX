import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService } from '../core/toast.service';

@Component({
  selector: 'sb-toast', standalone: true, imports: [CommonModule],
  template: `@if (toast.message(); as m) { <div class="toast">{{ m }}</div> }`,
})
export class ToastComponent { toast = inject(ToastService); }
