const track = document.querySelector(".carousel-track");
const slides = Array.from(track.children);
const nextButton = document.querySelector(".carousel-right");
const prevButton = document.querySelector(".carousel-left");
const dotsNav = document.querySelector(".carousel-nav");
const dots = Array.from(dotsNav.children);

const slideWidth = slides[0].getBoundingClientRect().width + 100;


const midpoint = Math.floor(slides.length / 2);

// Clone all slides
const clonedSlides = slides.map(slide => {
    const clone = slide.cloneNode(true);
    clone.classList.remove("current-slide");
    return clone;
});

// Append cloned slides to the end of the track
clonedSlides.forEach(clone => {
    track.appendChild(clone);
});

const newSlides = Array.from(track.children);

const leftPosition = 'calc(50% - ' + (slides[0].getBoundingClientRect().width)  / 2 + 'px)';
track.style.left = leftPosition;

const lengthLimit = slides.length + (Math.floor(newSlides.length / 4));
const halfLength = (Math.ceil(newSlides.length / 4));
const rightLimit = (halfLength) * slideWidth * - 1;


const setSlidePosition = (slide, index) => {

    if (index < lengthLimit) {
        slide.style.left = slideWidth * index + "px";
    }
    else {
        const newIndex = index - (lengthLimit);
        slide.style.left = rightLimit + slideWidth * newIndex + "px";
    }

}

newSlides.forEach(setSlidePosition);


const moveToSlide = (track, currentSlide, targetSlide) => { 
    track.style.transform = "translateX(-" + targetSlide.style.left + ")";
    currentSlide.classList.remove("current-slide");
    targetSlide.classList.add("current-slide");
}

const updateDots = (currentDot, targetDot) => {
    currentDot.classList.remove("current-slide-indicator");
    targetDot.classList.add("current-slide-indicator");
}

prevButton.addEventListener("click", e => {
    const currentSlide = track.querySelector(".current-slide");
    const prevIndex = (slides.indexOf(currentSlide) - 1 + slides.length) % slides.length;
    const prevSlide = slides[prevIndex];
    const currentDot = dotsNav.querySelector(".current-slide-indicator");
    const prevDot = dots[prevIndex];

    moveToSlide(track, currentSlide, prevSlide);
    updateDots(currentDot, prevDot);

    if (prevIndex === slides.length - 1) {
        // If previous slide is the last slide, move the last slide to the beginning
        moveToSlide(track, nextSlide, slides[slides.length-1]);
    }
});

nextButton.addEventListener("click", e => {
    const currentSlide = track.querySelector(".current-slide");
    const nextIndex = (slides.indexOf(currentSlide) + 1) % slides.length;
    const nextSlide = slides[nextIndex];
    const currentDot = dotsNav.querySelector(".current-slide-indicator");
    const nextDot = dots[nextIndex];

    moveToSlide(track, currentSlide, nextSlide);
    updateDots(currentDot, nextDot);

    if (nextIndex === 0) {
        // If next slide is the first slide, reset track position to the original first slide
        moveToSlide(track, nextSlide, slides[0]);
    }
})


dotsNav.addEventListener("click", e => {
    const targetDot = e.target.closest("button");

    if (!targetDot) return;

    const currentSlide = track.querySelector(".current-slide");
    const currentDot = dotsNav.querySelector(".current-slide-indicator");
    const targetIndex = dots.findIndex(dot => dot === targetDot);
    const targetSlide = slides[targetIndex];

    moveToSlide(track, currentSlide, targetSlide);

    updateDots(currentDot, targetDot);
} )