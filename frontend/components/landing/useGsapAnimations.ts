import { useEffect } from 'react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export const useProgressBar = () => {
  useEffect(() => {
    gsap.to('.progress-bar', {
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
    const heroTl = gsap.timeline();

    // Fragmented identity
    heroTl.to(
      '.fragmented-identity .organic-path',
      {
        opacity: 0.15,
        duration: 1.2,
        stagger: 0.15,
        ease: 'power2.out',
      },
      0
    );

    // Unified identity core
    heroTl.to(
      '.unified-identity .organic-path:nth-child(1)',
      {
        opacity: 0.18,
        scale: 1,
        duration: 0.8,
        ease: 'back.out(1.3)',
      },
      0.3
    );

    // Radiance lines
    heroTl.to(
      '.unified-identity .organic-path:nth-of-type(n+2):nth-of-type(-n+5)',
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
      '.unified-identity .organic-path:nth-of-type(n+2):nth-of-type(-n+5)',
      {
        strokeDashoffset: 0,
        duration: 1.2,
        stagger: 0.1,
        ease: 'power2.inOut',
      },
      0.4
    );

    // Text animations
    heroTl.to(
      '.hero-title .word',
      {
        y: 0,
        opacity: 1,
        duration: 1.2,
        stagger: 0.06,
        ease: 'power3.out',
      },
      0.4
    );

    heroTl.to(
      '.hero-subtitle',
      {
        opacity: 1,
        duration: 1,
        ease: 'power2.inOut',
      },
      0.7
    );

    heroTl.to(
      '.scroll-indicator',
      {
        opacity: 1,
        duration: 0.8,
        ease: 'power2.inOut',
      },
      0.9
    );
  }, []);
};

export const useChapterAnimations = () => {
  useEffect(() => {
    // Chapter 1 - Vision
    const chapter1 = document.querySelector('.chapter.light');
    if (chapter1) {
      gsap.set(chapter1.querySelector('.chapter-content'), { opacity: 0, x: -50 });
      gsap.to(chapter1.querySelector('.chapter-content'), {
        opacity: 1,
        x: 0,
        duration: 1,
        scrollTrigger: {
          trigger: chapter1,
          start: 'top 70%',
        },
      });
    }

    // Chapter 2 - Technology
    const chapter2 = document.querySelector('.chapter.dark');
    if (chapter2) {
      gsap.set(chapter2.querySelector('.chapter-content'), { opacity: 0, x: 50 });
      gsap.to(chapter2.querySelector('.chapter-content'), {
        opacity: 1,
        x: 0,
        duration: 1,
        scrollTrigger: {
          trigger: chapter2,
          start: 'top 70%',
        },
      });
    }

    // Chapter 3 - Impact
    const chapter3 = document.querySelectorAll('.chapter.light')[1];
    if (chapter3) {
      gsap.set(chapter3.querySelector('.chapter-content'), { opacity: 0, x: -50 });
      gsap.to(chapter3.querySelector('.chapter-content'), {
        opacity: 1,
        x: 0,
        duration: 1,
        scrollTrigger: {
          trigger: chapter3,
          start: 'top 70%',
        },
      });
    }

    // Chapter 4 - Revolution
    const chapter4 = document.querySelectorAll('.chapter.dark')[1];
    if (chapter4) {
      gsap.set(chapter4.querySelector('.chapter-content'), { opacity: 0, x: 50 });
      gsap.to(chapter4.querySelector('.chapter-content'), {
        opacity: 1,
        x: 0,
        duration: 1,
        scrollTrigger: {
          trigger: chapter4,
          start: 'top 70%',
        },
      });
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
  }, []);
};

export const useFinaleAnimations = () => {
  useEffect(() => {
    gsap.from('.finale-illustration', {
      opacity: 0,
      scale: 0.85,
      duration: 1.2,
      scrollTrigger: {
        trigger: '.finale',
        start: 'top 70%',
      },
    });

    gsap.from('.finale > div:last-child', {
      opacity: 0,
      y: 40,
      duration: 1,
      scrollTrigger: {
        trigger: '.finale',
        start: 'top 60%',
      },
    });
  }, []);
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
