import { useEffect } from 'react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const useProgressBar = () => {
  useEffect(() => {
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;

    gsap.to(progressBar, {
      scaleX: 1,
      ease: 'none',
      scrollTrigger: {
        trigger: 'body',
        start: 'top top',
        end: 'bottom bottom',
        scrub: 0.3,
      },
    });
  }, []);
};

export const useHeroAnimations = () => {
  useEffect(() => {
    // Check if we're on landing page
    const heroTitle = document.querySelector('.hero-title');
    if (!heroTitle) return;

    const ctx = gsap.context(() => {
      const heroTl = gsap.timeline();

      // Fragmented identity
      const fragmentedPaths = document.querySelectorAll('.fragmented-identity .organic-path');
      if (fragmentedPaths.length > 0) {
        heroTl.to(
          fragmentedPaths,
          {
            opacity: 0.15,
            duration: 1.2,
            stagger: 0.15,
            ease: 'power2.out',
          },
          0
        );
      }

      // Unified identity core
      const unifiedCore = document.querySelector('.unified-identity .organic-path:nth-child(1)');
      if (unifiedCore) {
        heroTl.to(
          unifiedCore,
          {
            opacity: 0.18,
            scale: 1,
            duration: 0.8,
            ease: 'back.out(1.3)',
          },
          0.3
        );
      }

      // Radiance lines
      const radianceLines = document.querySelectorAll('.unified-identity .organic-path:nth-of-type(n+2):nth-of-type(-n+5)');
      if (radianceLines.length > 0) {
        heroTl.to(
          radianceLines,
          {
            strokeDasharray: 200,
            strokeDashoffset: 200,
            opacity: 0.1,
            duration: 1,
            ease: 'power2.inOut',
          },
          0.3
        );

        heroTl.to(
          radianceLines,
          {
            strokeDashoffset: 0,
            duration: 1.2,
            stagger: 0.1,
            ease: 'power2.inOut',
          },
          0.4
        );
      }

      // Text animations
      const words = document.querySelectorAll('.hero-title .word');
      if (words.length > 0) {
        heroTl.to(
          words,
          {
            y: 0,
            opacity: 1,
            duration: 1.2,
            stagger: 0.06,
            ease: 'power3.out',
          },
          0.4
        );
      }

      const subtitle = document.querySelector('.hero-subtitle');
      if (subtitle) {
        heroTl.to(
          subtitle,
          {
            opacity: 1,
            duration: 1,
            ease: 'power2.inOut',
          },
          0.7
        );
      }

      const scrollIndicator = document.querySelector('.scroll-indicator');
      if (scrollIndicator) {
        heroTl.to(
          scrollIndicator,
          {
            opacity: 1,
            duration: 0.8,
            ease: 'power2.inOut',
          },
          0.9
        );
      }
    });

    return () => ctx.revert();
  }, []);
};

export const useChapterAnimations = () => {
  useEffect(() => {
    const chapters = document.querySelectorAll('.chapter');
    if (chapters.length === 0) return;

    const ctx = gsap.context(() => {
      // Chapter 1: Vision - Central core with radiating lines
      const chapter1 = chapters[0];
      if (chapter1) {
        const content1 = chapter1.querySelector('.chapter-content');
        if (content1) {
          gsap.fromTo(content1, { opacity: 0, x: -50 }, {
            opacity: 1, x: 0, duration: 1,
            scrollTrigger: { trigger: chapter1, start: 'top 70%' },
          });
        }

        const ch1Paths = chapter1.querySelectorAll('.illustration .organic-path');
        const ch1Tl = gsap.timeline({
          scrollTrigger: { trigger: chapter1.querySelector('.illustration'), start: 'top 70%', once: true },
        });

        // Central core appears first
        if (ch1Paths[0]) {
          ch1Tl.to(ch1Paths[0], { opacity: 0.9, scale: 1, duration: 0.8, ease: 'back.out(1.7)' });
        }

        // Radiating lines draw
        const ch1StrokePaths = chapter1.querySelectorAll('.illustration svg path[stroke]');
        ch1StrokePaths.forEach((path) => {
          const p = path as SVGPathElement;
          if (p.getTotalLength) {
            const length = p.getTotalLength();
            p.style.strokeDasharray = String(length);
            p.style.strokeDashoffset = String(length);
          }
        });
        ch1Tl.to(ch1StrokePaths, { strokeDashoffset: 0, opacity: 0.4, duration: 1.2, stagger: 0.15, ease: 'power2.inOut' }, 0.2);
      }

      // Chapter 2: Technology - Sequential flow animation
      const chapter2 = chapters[1];
      if (chapter2) {
        const content2 = chapter2.querySelector('.chapter-content');
        if (content2) {
          gsap.fromTo(content2, { opacity: 0, x: 50 }, {
            opacity: 1, x: 0, duration: 1,
            scrollTrigger: { trigger: chapter2, start: 'top 70%' },
          });
        }

        const ch2Paths = chapter2.querySelectorAll('.illustration .organic-path');
        const ch2Tl = gsap.timeline({
          scrollTrigger: { trigger: chapter2.querySelector('.illustration'), start: 'top 70%', once: true },
        });

        // Sequential flow: document → arrow → blockchain blocks → credential
        if (ch2Paths[0]) ch2Tl.to(ch2Paths[0], { opacity: 0.8, scale: 1, duration: 0.7, ease: 'power3.out' });
        if (ch2Paths[1]) {
          const p = ch2Paths[1] as SVGPathElement;
          if (p.getTotalLength) {
            const len = p.getTotalLength();
            p.style.strokeDasharray = String(len);
            p.style.strokeDashoffset = String(len);
          }
          ch2Tl.to(ch2Paths[1], { strokeDashoffset: 0, opacity: 0.6, duration: 0.8, ease: 'power2.inOut' }, 0.2);
        }
        if (ch2Paths[2]) ch2Tl.to(ch2Paths[2], { opacity: 0.7, scale: 1, duration: 0.6, ease: 'back.out(1.5)' }, 0.5);
        if (ch2Paths[3]) ch2Tl.to(ch2Paths[3], { opacity: 0.6, duration: 0.6, ease: 'power3.out' }, 0.7);
        if (ch2Paths[4]) ch2Tl.to(ch2Paths[4], { opacity: 0.5, scale: 1, duration: 0.6, ease: 'back.out(1.5)' }, 0.9);
        if (ch2Paths[5]) ch2Tl.to(ch2Paths[5], { strokeDashoffset: 0, opacity: 0.5, duration: 0.8, ease: 'power2.inOut' }, 1.0);
      }

      // Chapter 3: Impact - Trajectory line with milestone markers
      const chapter3 = chapters[2];
      if (chapter3) {
        const content3 = chapter3.querySelector('.chapter-content');
        if (content3) {
          gsap.fromTo(content3, { opacity: 0, x: -50 }, {
            opacity: 1, x: 0, duration: 1,
            scrollTrigger: { trigger: chapter3, start: 'top 70%' },
          });
        }

        const ch3Paths = chapter3.querySelectorAll('.illustration .organic-path');
        const ch3Tl = gsap.timeline({
          scrollTrigger: { trigger: chapter3.querySelector('.illustration'), start: 'top 70%', once: true },
        });

        // Trajectory line draws first
        if (ch3Paths[0]) {
          const p = ch3Paths[0] as SVGPathElement;
          if (p.getTotalLength) {
            const len = p.getTotalLength();
            p.style.strokeDasharray = String(len);
            p.style.strokeDashoffset = String(len);
          }
          ch3Tl.to(ch3Paths[0], { strokeDashoffset: 0, opacity: 0.7, duration: 1.5, ease: 'power3.inOut' });
        }

        // Milestone markers pop in
        const markers = Array.from(ch3Paths).slice(1, 5);
        if (markers.length) {
          ch3Tl.to(markers, { opacity: 0.9, scale: 1, duration: 0.5, stagger: 0.2, ease: 'elastic.out(1.2, 0.5)' }, 0.8);
        }
      }

      // Chapter 4: Revolution - Central hub with network nodes
      const chapter4 = chapters[3];
      if (chapter4) {
        const content4 = chapter4.querySelector('.chapter-content');
        if (content4) {
          gsap.fromTo(content4, { opacity: 0, x: 50 }, {
            opacity: 1, x: 0, duration: 1,
            scrollTrigger: { trigger: chapter4, start: 'top 70%' },
          });
        }

        const ch4Paths = chapter4.querySelectorAll('.illustration .organic-path');
        const ch4Tl = gsap.timeline({
          scrollTrigger: { trigger: chapter4.querySelector('.illustration'), start: 'top 70%', once: true },
        });

        // Central hub appears first
        if (ch4Paths[0]) ch4Tl.to(ch4Paths[0], { opacity: 0.9, scale: 1, duration: 0.8, ease: 'back.out(2)' });
        // Network nodes appear
        if (ch4Paths[1]) ch4Tl.to(ch4Paths[1], { opacity: 0.7, scale: 1, duration: 0.5, ease: 'back.out(1.5)' }, 0.3);
        if (ch4Paths[2]) ch4Tl.to(ch4Paths[2], { opacity: 0.6, scale: 1, duration: 0.5, ease: 'back.out(1.5)' }, 0.4);
        if (ch4Paths[3]) ch4Tl.to(ch4Paths[3], { opacity: 0.7, scale: 1, duration: 0.5, ease: 'back.out(1.5)' }, 0.5);
        if (ch4Paths[4]) ch4Tl.to(ch4Paths[4], { opacity: 0.6, scale: 1, duration: 0.5, ease: 'back.out(1.5)' }, 0.6);

        // Connection lines draw
        const ch4StrokePaths = chapter4.querySelectorAll('.illustration svg path[stroke]');
        ch4StrokePaths.forEach((path) => {
          const p = path as SVGPathElement;
          if (p.getTotalLength) {
            const len = p.getTotalLength();
            p.style.strokeDasharray = String(len);
            p.style.strokeDashoffset = String(len);
          }
        });
        ch4Tl.to(ch4StrokePaths, { strokeDashoffset: 0, opacity: 0.4, duration: 1, stagger: 0.15, ease: 'power2.inOut' }, 0.7);
      }

      // Parallax chapter numbers
      gsap.utils.toArray('.chapter-number').forEach((num) => {
        const element = num as HTMLElement;
        gsap.to(element, {
          y: 80,
          opacity: 0.02,
          scrollTrigger: {
            trigger: element.parentElement,
            start: 'top center',
            end: 'bottom center',
            scrub: 1,
          },
        });
      });
    });

    return () => ctx.revert();
  }, []);
};

export const useFinaleAnimations = (shouldInitialize: boolean = true) => {
  useEffect(() => {
    if (!shouldInitialize) return;

    const finaleIllustration = document.querySelector('.finale-illustration');
    const finale = document.querySelector('.finale');
    if (!finale) return;

    const ctx = gsap.context(() => {
      // Illustration container animation
      if (finaleIllustration) {
        gsap.fromTo(
          finaleIllustration,
          { opacity: 0, scale: 0.85 },
          {
            opacity: 1,
            scale: 1,
            duration: 1.2,
            scrollTrigger: {
              trigger: finale,
              start: 'top 70%',
            },
          }
        );
      }

      // Content text animation
      const finaleContent = finale.querySelector(':scope > div:last-child');
      if (finaleContent) {
        gsap.fromTo(
          finaleContent,
          { opacity: 0, y: 40 },
          {
            opacity: 1,
            y: 0,
            duration: 1,
            scrollTrigger: {
              trigger: finale,
              start: 'top 60%',
            },
          }
        );
      }

      // SVG path animations - core appears, then radiating lines draw
      const finaleSvgTl = gsap.timeline({
        scrollTrigger: {
          trigger: finaleIllustration,
          start: 'top 70%',
          once: true,
        },
      });

      // Central core appears with bounce
      const coreShape = finale.querySelector('.finale-illustration .organic-path:first-child');
      if (coreShape) {
        finaleSvgTl.to(coreShape, {
          opacity: 0.95,
          scale: 1,
          duration: 0.8,
          ease: 'back.out(2)',
        });
      }

      // Initialize and animate stroke paths (radiating lines)
      const finaleStrokePaths = finale.querySelectorAll('.finale-illustration svg path[stroke]');
      finaleStrokePaths.forEach((path) => {
        const p = path as SVGPathElement;
        if (p.getTotalLength) {
          const len = p.getTotalLength();
          p.style.strokeDasharray = String(len);
          p.style.strokeDashoffset = String(len);
        }
      });

      finaleSvgTl.to(
        finaleStrokePaths,
        {
          strokeDashoffset: 0,
          opacity: 0.5,
          duration: 1.2,
          stagger: 0.12,
          ease: 'power2.inOut',
        },
        0.3
      );
    });

    return () => ctx.revert();
  }, [shouldInitialize]);
};

export const useCustomCursor = () => {
  useEffect(() => {
    const cursorOuter = document.querySelector('.cursor-outer');
    const cursorInner = document.querySelector('.cursor-inner');
    const spotlightLayer = document.querySelector('.spotlight-layer');

    if (!cursorOuter || !cursorInner) return;

    let cursorX = 0,
      cursorY = 0;
    let dotX = 0,
      dotY = 0;
    let mouseX = 0,
      mouseY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;

      if (spotlightLayer) {
        (spotlightLayer as HTMLElement).style.setProperty('--mouse-x', mouseX + 'px');
        (spotlightLayer as HTMLElement).style.setProperty('--mouse-y', mouseY + 'px');
      }
    };

    const updateCursor = () => {
      cursorX += (mouseX - cursorX) * 0.15;
      cursorY += (mouseY - cursorY) * 0.15;
      dotX += (mouseX - dotX) * 0.4;
      dotY += (mouseY - dotY) * 0.4;

      (cursorOuter as HTMLElement).style.left = cursorX - 20 + 'px';
      (cursorOuter as HTMLElement).style.top = cursorY - 20 + 'px';
      (cursorInner as HTMLElement).style.left = dotX - 4 + 'px';
      (cursorInner as HTMLElement).style.top = dotY - 4 + 'px';

      requestAnimationFrame(updateCursor);
    };

    document.addEventListener('mousemove', handleMouseMove);
    updateCursor();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
};

export const useSpotlightObserver = () => {
  useEffect(() => {
    const spotlightLayer = document.querySelector('.spotlight-layer');
    if (!spotlightLayer) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const anyDarkVisible = entries.some(
          (e) => e.isIntersecting && e.intersectionRatio > 0.2
        );
        spotlightLayer.classList.toggle('active', anyDarkVisible);
      },
      { threshold: [0, 0.2, 0.4, 0.6, 0.8, 1] }
    );

    document.querySelectorAll('.dark').forEach((section) => {
      observer.observe(section);
    });

    return () => observer.disconnect();
  }, []);
};

export const initializeStrokePaths = () => {
  document.querySelectorAll('svg path[stroke]').forEach((path) => {
    const element = path as SVGPathElement;
    const length = element.getTotalLength();
    element.style.strokeDasharray = String(length);
    element.style.strokeDashoffset = String(length);
  });
};

export const useNavbarHideOnScroll = () => {
  useEffect(() => {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    let lastScrollY = 0;
    let tl: gsap.core.Tween | null = null;

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDirection = currentScrollY > lastScrollY ? 'down' : 'up';

      if (scrollDirection === 'down' && currentScrollY > 100) {
        // Scrolling down - hide navbar
        if (tl) tl.kill();
        tl = gsap.to('.navbar', {
          y: -100,
          duration: 0.3,
          ease: 'power2.inOut',
        });
      } else {
        // Scrolling up or near top - show navbar
        if (tl) tl.kill();
        tl = gsap.to('.navbar', {
          y: 0,
          duration: 0.3,
          ease: 'power2.inOut',
        });
      }

      lastScrollY = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
};
