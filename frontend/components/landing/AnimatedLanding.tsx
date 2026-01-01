'use client';

import { useEffect } from 'react';
import {
  useProgressBar,
  useHeroAnimations,
  useChapterAnimations,
  useFinaleAnimations,
  useCustomCursor,
  useSpotlightObserver,
  useNavbarHideOnScroll,
  initializeStrokePaths,
} from './useGsapAnimations';
import { Navbar } from './Navbar';

const HeroSection = () => (
  <section className="hero min-h-screen flex flex-col items-center justify-center relative p-4 overflow-hidden bg-[var(--cream)]">
    <svg
      viewBox="0 0 1000 1000"
      fill="none"
      className="absolute top-0 left-0 w-full h-full opacity-[0.12] pointer-events-none"
    >
      <g className="fragmented-identity">
        <path
          className="organic-path"
          d="M 150 300 Q 130 320 140 360 L 160 400 Q 170 420 195 415 L 210 375 Q 215 335 195 315 Z"
          fill="#141413"
          opacity="0.15"
        />
        <path
          className="organic-path"
          d="M 280 250 Q 265 270 275 310 L 295 350 Q 305 370 330 365 L 345 325 Q 350 285 330 265 Z"
          fill="#141413"
          opacity="0.12"
        />
      </g>

      <g className="unified-identity">
        <path
          className="organic-path"
          d="M 700 400 Q 660 430 675 490 Q 695 550 770 560 Q 845 550 865 490 Q 880 430 840 400 Z"
          fill="#141413"
          opacity="0.18"
        />
        <path
          className="organic-path"
          d="M 770 320 Q 800 380 770 440"
          fill="none"
          stroke="#141413"
          strokeWidth="2"
          opacity="0.1"
        />
      </g>
    </svg>

    <h1 className="hero-title landing-h1 text-center relative z-10 text-[var(--charcoal)]">
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          Imagine
        </span>
      </span>
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          a world
        </span>
      </span>
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          where
        </span>
      </span>
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          identity
        </span>
      </span>
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          travels
        </span>
      </span>
      <span className="block">
        <span className="word" style={{ display: 'inline-block', opacity: 0, transform: 'translateY(100%)' }}>
          freely.
        </span>
      </span>
    </h1>

    <p className="hero-subtitle text-center max-w-[700px] mt-8 opacity-0 text-[var(--charcoal)] text-base md:text-lg">
      Government-grade verification meets self-sovereign ownership—
      <br />
      unlocking human potential across borders, forever.
    </p>

    <div className="scroll-indicator absolute bottom-8 opacity-0 flex flex-col items-center gap-2 text-xs uppercase tracking-widest text-[var(--charcoal)]">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 16V8M12 16L16 12M12 16L8 12"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span>Scroll</span>
    </div>
  </section>
);

interface ChapterSectionProps {
  number: number;
  title: string;
  description: {
    title: string;
    paragraphs: string[];
  };
  isLight: boolean;
  children: React.ReactNode;
}

const ChapterSection = ({ number, title, description, isLight, children }: ChapterSectionProps) => (
  <section className={`chapter min-h-screen flex items-center justify-center relative p-6 md:p-12 ${isLight ? 'bg-[var(--cream)] text-[var(--charcoal)]' : 'bg-[var(--charcoal)] text-[var(--cream)]'}`}>
    <span className={`chapter-number absolute top-0 left-0 text-8xl md:text-9xl font-serif opacity-[0.04] font-normal`}>
      {number}
    </span>

    <div className="chapter-inner grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 max-w-6xl w-full relative z-10">
      {number % 2 === 0 ? (
        <>
          {children}
          <div className="chapter-content">
            <p className="landing-label mb-2">{title}</p>
            <h2 className="landing-h2">{description.title}</h2>
            <div className="chapter-description mt-6 space-y-4 text-sm md:text-base opacity-85">
              {description.paragraphs.map((para: string, i: number) => (
                <p key={i}>{para}</p>
              ))}
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="chapter-content">
            <p className="landing-label mb-2">{title}</p>
            <h2 className="landing-h2">{description.title}</h2>
            <div className="chapter-description mt-6 space-y-4 text-sm md:text-base opacity-85">
              {description.paragraphs.map((para: string, i: number) => (
                <p key={i}>{para}</p>
              ))}
            </div>
          </div>
          {children}
        </>
      )}
    </div>
  </section>
);

interface IllustrationProps {
  children: React.ReactNode;
}

const Illustration = ({ children }: IllustrationProps) => (
  <div className="illustration relative h-80 md:h-96 flex items-center justify-center">{children}</div>
);

export const AnimatedLanding = () => {
  useProgressBar();
  useHeroAnimations();
  useChapterAnimations();
  useFinaleAnimations();
  useCustomCursor();
  useSpotlightObserver();
  useNavbarHideOnScroll();

  useEffect(() => {
    initializeStrokePaths();
  }, []);

  return (
    <>
      {/* Navbar */}
      <Navbar />

      {/* Progress Bar */}
      <div className="progress-bar" />

      {/* Spotlight */}
      <div className="spotlight-layer" />

      {/* Custom Cursor */}
      <div className="cursor-outer" />
      <div className="cursor-inner" />

      {/* Hero Section */}
      <HeroSection />

      {/* Chapter 1: Vision */}
      <ChapterSection
        number={1}
        title="The Vision"
        isLight={true}
        description={{
          title: 'One identity.\nInfinite possibility.',
          paragraphs: [
            'For the first time in history, we can separate verification from control.',
            'Imagine proving who you are—once, with government-grade certainty—then carrying that proof across every service, every border, every opportunity. Without repeating KYC. Without surrendering data. Without asking permission.',
            'Your identity becomes your superpower.',
          ],
        }}
      >
        <Illustration>
          <svg viewBox="0 0 500 500" fill="none" className="w-full h-full max-w-[550px]">
            <path
              className="organic-path"
              d="M 200 200 Q 160 220 170 270 Q 185 310 250 320 Q 315 310 330 270 Q 340 220 300 200 Z"
              fill="#141413"
              opacity="0.9"
            />
            <path
              className="organic-path"
              d="M 250 150 Q 270 190 250 250"
              fill="none"
              stroke="#141413"
              strokeWidth="2"
              opacity="0.4"
            />
          </svg>
        </Illustration>
      </ChapterSection>

      {/* Chapter 2: Technology */}
      <ChapterSection
        number={2}
        title="The Technology"
        isLight={false}
        description={{
          title: 'Architecture of trust.',
          paragraphs: [
            'Aadhaar verification flows through encrypted channels to the Solana blockchain, where cryptographic proofs lock your identity into an immutable record.',
            'No company holds your data. No database can be breached. You hold the keys. You grant access. You revoke it anytime.',
            'This is zero-knowledge infrastructure—proving truth without revealing secrets.',
          ],
        }}
      >
        <Illustration>
          <svg viewBox="0 0 500 500" fill="none" className="w-full h-full max-w-[550px]">
            <path
              className="organic-path"
              d="M 60 100 Q 40 120 50 170 L 80 220 Q 95 240 125 230 L 140 170 Q 145 120 115 105 Z"
              fill="#FAF9F5"
              opacity="0.8"
            />
            <path
              className="organic-path"
              d="M 150 170 Q 200 160 250 165"
              fill="none"
              stroke="#FAF9F5"
              strokeWidth="3"
              opacity="0.6"
            />
          </svg>
        </Illustration>
      </ChapterSection>

      {/* Chapter 3: Impact */}
      <ChapterSection
        number={3}
        title="The Impact"
        isLight={true}
        description={{
          title: 'Breaking barriers.\nEnabling dreams.',
          paragraphs: [
            '1.4 billion Indians gain global identity portability. 32 million NRIs prove credentials without embassy visits.',
            'Banks verify customers in 2 seconds, not 2 days. Fintechs cut KYC costs by 90%. Enterprises access verified users instantly.',
            'The estimated market: $52 billion globally. But the real value is human—financial inclusion accelerated, borders erased, opportunity democratized.',
          ],
        }}
      >
        <Illustration>
          <svg viewBox="0 0 500 500" fill="none" className="w-full h-full max-w-[550px]">
            <path
              className="organic-path"
              d="M 100 420 Q 150 370 200 320 Q 260 260 320 180 Q 370 110 430 60"
              fill="none"
              stroke="#141413"
              strokeWidth="4"
              opacity="0.7"
            />
          </svg>
        </Illustration>
      </ChapterSection>

      {/* Chapter 4: Revolution */}
      <ChapterSection
        number={4}
        title="The Revolution"
        isLight={false}
        description={{
          title: 'An identity\nrenaissance.',
          paragraphs: [
            "We're not just building technology. We're catalyzing a shift in how humanity thinks about ownership of self.",
            "Your identity shouldn't be trapped in silos. It shouldn't be sold without consent. It shouldn't require endless repetition.",
            'Join us in creating the world\'s first government-grade self-sovereign identity platform—where 1.4 billion people become truly free to move, to work, to live anywhere on Earth.',
          ],
        }}
      >
        <Illustration>
          <svg viewBox="0 0 500 500" fill="none" className="w-full h-full max-w-[550px]">
            <path
              className="organic-path"
              d="M 250 230 Q 210 250 220 300 Q 240 330 290 320 Q 330 300 320 250 Z"
              fill="#FAF9F5"
              opacity="0.9"
            />
          </svg>
        </Illustration>
      </ChapterSection>

      {/* Finale */}
      <section className="finale bg-[var(--charcoal)] text-[var(--cream)] min-h-screen flex flex-col items-center justify-center text-center gap-12 p-8 md:p-32">
        <div className="finale-illustration w-80 h-80 md:w-96 md:h-96">
          <svg viewBox="0 0 500 500" fill="none" className="w-full h-full">
            <path
              className="organic-path"
              d="M 180 180 Q 140 200 155 260 Q 180 320 250 330 Q 320 320 345 260 Q 360 200 320 180 Z"
              fill="#FAF9F5"
              opacity="0.95"
            />
            <path
              className="organic-path"
              d="M 250 50 Q 300 120 280 190"
              fill="none"
              stroke="#FAF9F5"
              strokeWidth="2"
              opacity="0.5"
            />
          </svg>
        </div>

        <div className="max-w-2xl">
          <p className="landing-label mb-4">Ready for the future?</p>
          <h2 className="landing-h2 mb-8">
            Own Your Identity.
            <br />
            Change Everything.
          </h2>
          <p className="text-base md:text-lg opacity-90 mb-8">
            AadhaarChain is bringing self-sovereign identity to India and the world.
            <br />
            The revolution starts with you.
          </p>
          <a
            href="/identity/create"
            className="inline-block px-12 py-5 bg-[var(--cream)] text-[var(--charcoal)] font-semibold text-lg hover:shadow-lg hover:-translate-y-1 transition-all duration-300 rounded-sm"
          >
            Join the Revolution
          </a>
        </div>
      </section>
    </>
  );
};
