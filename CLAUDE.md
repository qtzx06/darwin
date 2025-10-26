# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Darwin is a React + Vite landing page featuring advanced visual effects including FBO particle animations, liquid glass morphism effects, and interactive 3D cube grids. The site showcases a modern aesthetic with purple/lilac color theming and smooth animations throughout.

## Development Commands

- `npm run dev` - Start development server with HMR
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Architecture

### Core Structure

The app has a single-page landing design (`App.jsx`) that orchestrates multiple visual components layered on top of each other:

1. **Background Layer** - Wisp FBO particle animation (iframe at `/wisp/index.html`)
2. **Side Panels** - Left/right dither effects with animated patterns
3. **Center Content** - Title, search bar, logo carousel, footer

### Key Visual Components

**Wisp Animation** (`/public/wisp/`)
- Three.js-based FBO particle system with custom shaders
- Implements zoom-in animation triggered by search submission
- Listens for `postMessage` events to trigger zoom effect
- Located in separate iframe for performance isolation

**GlassSearchBar** (`src/components/GlassSearchBar.jsx`)
- Liquid glass morphism effect using SVG filters (`#glass-distortion`)
- Three-layer rendering: glass-filter, glass-overlay, glass-specular
- Uses `feTurbulence` and `feDisplacementMap` for distortion
- Integrated with Framer Motion for smooth transitions

**Dither** (`src/components/Dither.jsx`)
- WebGL shader-based dithered wave animation for side panels
- Uses Three.js with custom vertex/fragment shaders
- Left and right panels have opposite animation directions (`waveSpeed`)
- Post-processing with custom RetroEffect using Bayer matrix dithering

**DecryptedText** (`src/components/DecryptedText.jsx`)
- Character-by-character decryption animation from Evolve component library
- Used for "darwin" title with sequential reveal

**LogoLoop** (`src/components/LogoLoop.jsx`)
- Infinite horizontal scrolling carousel
- Supports both React icon nodes and image sources
- Uses CSS mask for edge fade effects
- ResizeObserver-based responsive behavior

**DevpostCard** (`src/components/DevpostCard.jsx`)
- Fixed footer with centered logo and links
- Easter egg: clicking logo shows "*quack!*" text above it
- Uses CSS Grid for perfect center alignment

### Styling Approach

- **Fonts**: BBH Sans Bartle for title, Geist Mono for all UI text
- **Color Scheme**: Purple/lilac/pink tones (`#f0b0d0` for accents)
- **Glass Effects**: Multiple layered divs with `backdrop-filter: blur()` and SVG distortion filters
- **Animations**: Framer Motion for page transitions, GSAP for 3D cube interactions

### State Management

The app uses minimal React state:
- `isLoading` - Controls loading screen visibility
- `isZooming` - Triggers zoom animation and fades out all content
- `showOverlay` - Black overlay during zoom transition

### Navigation Flow

1. Loading screen displays for 1.5s
2. Landing page fades in with staggered animations
3. Search submission triggers:
   - Zoom-in animation on wisp (via postMessage)
   - Fade out of all UI elements (0.8s)
   - Black overlay fade (1.5s)
   - Navigation to `#orchestration` with query parameter

### Mobile Responsiveness

- Title font reduces from 3rem to 2rem
- Side dither panels hidden on mobile
- Logo loop and search bar scale to full width with padding
- Footer adjusts layout and spacing

## Important Implementation Details

### SVG Filter Reuse
The `#glass-distortion` SVG filter defined in `index.html` is reused across multiple components (GlassSearchBar, potentially DevpostCard). Do not duplicate this filter definition.

### Image Imports in Vite
Assets in `src/assets/` must be imported as modules (e.g., `import livekitLogo from './assets/livekit-text.svg'`). Public assets go in `/public` and are referenced with absolute paths.

### Three.js/React Integration
- Use `@react-three/fiber` for React integration
- Post-processing effects via `@react-three/postprocessing`
- Always set `dpr={1}` on Canvas components for consistent rendering
- Custom shaders use `useRef` for uniform management

### Animation Synchronization
All fade transitions use `duration: 0.8, ease: "easeOut"` for consistency. The `isZooming` state controls synchronized fade-out of all elements.

### Component Class Naming
To avoid CSS conflicts between similar components (e.g., glass effects), use unique class prefixes:
- GlassSearchBar: `.glass-search`, `.glass-content`
- DevpostCard: `.devpost-glass`, `.devpost-content`, `.footer-*`

### Logo Loop Image Filtering
The LogoLoop component applies `filter: brightness(0) invert(1)` to all images to convert them to white, matching the site's aesthetic.
