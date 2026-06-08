import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Title } from '../core/models';
import Hls from 'hls.js';

@Component({
  selector: 'sb-watch', standalone: true, imports: [CommonModule, RouterLink],
  template: `
  <div class="player-wrap">
    @if (title(); as t) {
      <a class="player-back" [routerLink]="['/title', t.slug]">← Retour</a>
      @if (t.video_url) {
        <video #player controls autoplay playsinline crossorigin="anonymous">
          <source [src]="t.video_url">
        </video>
      } @else {
        <div style="color:#fff;text-align:center;padding:40vh 20px">Aucune source vidéo configurée.</div>
      }
    }
  </div>`,
})
export class WatchComponent implements OnInit, OnDestroy {
  private api = inject(ApiService); private route = inject(ActivatedRoute);
  title = signal<Title | null>(null);
  @ViewChild('player') player?: ElementRef<HTMLVideoElement>;
  private timer?: any; private hls?: Hls; private slug = '';

  ngOnInit() {
    this.slug = this.route.snapshot.paramMap.get('slug')!;
    this.api.title(this.slug).subscribe(t => {
      this.title.set(t);
      setTimeout(() => this.setupPlayer(t), 0);
    });
  }
  setupPlayer(t: Title) {
    const v = this.player?.nativeElement; if (!v || !t.video_url) return;
    if (t.video_url.endsWith('.m3u8') && Hls.isSupported()) {
      this.hls = new Hls(); this.hls.loadSource(t.video_url); this.hls.attachMedia(v);
    }
    this.timer = setInterval(() => this.save(false), 10000);
    v.addEventListener('pause', () => this.save(false));
    v.addEventListener('ended', () => this.save(true));
  }
  save(finished: boolean) {
    const v = this.player?.nativeElement; if (!v) return;
    this.api.saveProgress(this.slug, Math.floor(v.currentTime || 0), finished).subscribe();
  }
  ngOnDestroy() { clearInterval(this.timer); this.save(false); this.hls?.destroy(); }
}
