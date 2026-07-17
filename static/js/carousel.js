const carouselEl = document.querySelector('#project-carousel');

if (carouselEl) {
  // gap matches the measured original: 475px slide + 195px gap = 670px center-to-center spacing
  const splide = new Splide(carouselEl, {
    type: 'loop',
    focus: 'center',
    perPage: 1,
    fixedWidth: '475px',
    gap: '195px',
    arrows: false,
    pagination: false,
    drag: true,
    speed: 250,
  });

  const nextButton = document.querySelector('.carousel-right');
  const prevButton = document.querySelector('.carousel-left');
  const dotsNav = document.querySelector('.carousel-nav');
  const dots = dotsNav ? Array.from(dotsNav.children) : [];
  const slides = Array.from(carouselEl.querySelectorAll('.splide__slide'));

  const setActiveIndex = (index) => {
    slides.forEach((slide, i) => {
      slide.classList.toggle('current-slide', i === index);
    });
    dots.forEach((dot, i) => {
      dot.classList.toggle('current-slide-indicator', i === index);
    });
  };

  // `move` fires right as the transition starts, so the scale-up/scale-down
  // CSS transition on .current-slide runs alongside Splide's own slide transition
  // instead of only after it finishes.
  splide.on('move', (newIndex) => {
    setActiveIndex(newIndex);
  });

  splide.on('mounted', () => {
    setActiveIndex(splide.index);
  });

  splide.mount();

  if (nextButton) {
    nextButton.addEventListener('click', () => splide.go('>'));
  }
  if (prevButton) {
    prevButton.addEventListener('click', () => splide.go('<'));
  }
  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => splide.go(i));
  });
}
