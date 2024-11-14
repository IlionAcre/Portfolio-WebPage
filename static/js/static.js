function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (section) {
      section.scrollIntoView({
          behavior: 'smooth'
      });
  }
}

function adjustLine(containerId, lineContainerId, direction = 'left') {
  const container = document.getElementById(containerId);
  const line = document.getElementById(lineContainerId);

  if (!container || !line) {
      console.error(`Container or line element not found: ${containerId}, ${lineContainerId}`);
      return;
  }

  const width = container.offsetWidth;
  const height = container.offsetHeight;

  // Assuming the width and height provide the dimensions of the entire area to cover
  let lineLength = Math.sqrt((width / 2) ** 2 + height ** 2); // This remains correct for reaching the bottom-center
  
  let angle;
  if (direction === 'left') {
      // Angle for left direct                ion remains unchanged
      angle = Math.atan2(height, width / 2) * (180 / Math.PI) - 0.2;
      line.style.transformOrigin = 'top left';
      line.style.left = '0px'; // Ensure it starts from the top-left
  } else {
      // Correcting angle for the right direction
      // This needs to ensure it points diagonally towards the bottom-center
      angle = - (Math.atan2(height, width / 2) * (180 / Math.PI)) + 0.2;
      line.style.transformOrigin = 'top right';
      line.style.right = '0px'; // Ensure it starts from the top-right
  }

  line.style.position = 'absolute';
  line.style.width = `${lineLength}px`;
  line.style.top = '0px';
  line.style.transform = `rotate(${angle}deg)`;

}

// Improved window resize event handling
function setupResizeListener(containerId, lineContainerId, direction) {
  window.addEventListener('resize', () => adjustLine(containerId, lineContainerId, direction));
}

// Setup for both lines
adjustLine("triangle1", "triangle1-left", 'left');
adjustLine("triangle1", "triangle1-right", 'right');

adjustLine("triangle2", "triangle2-left", 'left');
adjustLine("triangle2", "triangle2-right", 'right');

// Setup resize listeners for dynamic adjustment
setupResizeListener("triangle1", "triangle1-left", 'left');
setupResizeListener("triangle1", "triangle1-right", 'right');

setupResizeListener("triangle2", "triangle2-left", 'left');
setupResizeListener("triangle2", "triangle2-right", 'right');


// Filter buttons

const skillsContainer = document.querySelector(".skills-wrapper");


const allBtn = skillsContainer.querySelector(".all") 
const allBtns = skillsContainer.querySelectorAll(".all") 

function checkAll(){
  const allButtons = skillsContainer.querySelectorAll(".btn-check:not(.all)");
  for (const item of allButtons) {
    if (!item.classList.contains("btn-check--checked")){
      console.log(item.classList);
      return false;
    }
  };
  return true;
}

function filterSkills() {
  const skillCards = document.querySelectorAll(".skill-card");

  // Determine the active filters
  const activeFilters = [];
  if (skillsContainer.querySelector(".technical").classList.contains("btn-check--checked")) {
    activeFilters.push("technical");
  }
  if (skillsContainer.querySelector(".soft").classList.contains("btn-check--checked")) {
    activeFilters.push("soft");
  }

  // If "All" is checked or no specific filters are active, show all skills
  if (activeFilters.length === 0 || skillsContainer.querySelector(".all").classList.contains("btn-check--checked")) {
    skillCards.forEach(card => {
      card.style.display = "flex";
    });
  } else {
    // Filter the skill cards based on the active filters
    skillCards.forEach(card => {
      const skillType = card.getAttribute("data-type");
      if (activeFilters.includes(skillType)) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  }
}

function toggleCheckbox(tag) {
  // Get all buttons of the specified type (e.g., all technical or all soft)
  const targetButtons = skillsContainer.querySelectorAll(tag);
  
  // Remove the checked state from all buttons
  const allButtons = skillsContainer.querySelectorAll(".btn-check");
  allButtons.forEach(button => {
    button.classList.remove("btn-check--checked");
  });

  // Add the checked state only to the clicked button's group
  targetButtons.forEach(button => {
    button.classList.add("btn-check--checked");
  });

  // Run the filtering logic after updating the button states
  filterSkills();
}

function filterSkills() {
  const skillCards = document.querySelectorAll(".skill-card");

  // Determine which filter is active
  let activeFilter = null;
  if (skillsContainer.querySelector(".technical").classList.contains("btn-check--checked")) {
    activeFilter = "technical";
  } else if (skillsContainer.querySelector(".soft").classList.contains("btn-check--checked")) {
    activeFilter = "soft";
  } else if (skillsContainer.querySelector(".all").classList.contains("btn-check--checked")) {
    activeFilter = "all";
  }

  // Show/hide skill cards based on the active filter
  if (activeFilter === "all" || activeFilter === null) {
    // Show all skills if "All" is active or if no filter is selected
    skillCards.forEach(card => {
      card.style.display = "flex";
    });
  } else {
    // Show only the skills that match the active filter type
    skillCards.forEach(card => {
      const skillType = card.getAttribute("data-type");
      if (skillType === activeFilter) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  }
}


function toggleLight(element) {
  element.classList.toggle("enlightened");
}

function toggleTextLight(element) {
  element.classList.toggle("enlightened-text");
}

function toggleTitleLight(element) {
  element.classList.toggle("enlightened-title");
}


//nav-bar
const navTransitionIn = "top 1s ease";
const navTransitionOut = "top 2.5s ease";
const navHideDelay = 2000;

if (window.matchMedia("(max-width: 47rem)").matches) {
  const primaryNav = document.querySelector(".nav-list");
  const navToggle = document.querySelector(".mobile-nav-toggle");
  const navBar = document.querySelector(".nav-bar");
  let lastScrollY = window.scrollY;
  let hideTimeout;

  navBar.style.position = "fixed";
  navBar.style.top = "0";
  navBar.style.width = "100%";
  navBar.style.transition = navTransitionIn;

  navToggle.addEventListener("click", () => {
    const visibility = primaryNav.getAttribute("data-visible");
    if (visibility === "false") {
      primaryNav.setAttribute("data-visible", true);
      navToggle.setAttribute("aria-expanded", true);
      navToggle.style.backgroundImage = "url('/static/images/menu-close.svg')";
      primaryNav.style.transition = navTransitionOut;
      clearTimeout(hideTimeout);
    } else {
      primaryNav.setAttribute("data-visible", false);
      navToggle.setAttribute("aria-expanded", false);
      navToggle.style.backgroundImage = "url('/static/images/menu-open.svg')";
      primaryNav.style.transition = navTransitionOut;
    }
  });

  // Close the menu when a nav button is clicked
  const navButtons = document.querySelectorAll(".nav-btn");
  navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      primaryNav.setAttribute("data-visible", false);
      navToggle.setAttribute("aria-expanded", false);
      navToggle.style.backgroundImage = "url('/static/images/menu-open.svg')";
      primaryNav.style.transition = navTransitionIn;
    });
  });

  // Close the menu on swipe to the right (for mobile)
  let touchStartX = 0;
  let touchEndX = 0;

  primaryNav.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  });

  primaryNav.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipeGesture();
  });

  function handleSwipeGesture() {
    if (touchEndX > touchStartX + 50) { // Swipe right detection
      primaryNav.setAttribute("data-visible", false);
      navToggle.setAttribute("aria-expanded", false);
      navToggle.style.backgroundImage = "url('/static/images/menu-open.svg')";
      primaryNav.style.transition = "transform 1s ease";
    }
  }

  // Show nav-bar on scroll up and hide on scroll down, but do not hide if menu is open or at the top of the page
  window.addEventListener('scroll', () => {
    if (window.scrollY === 0 || window.scrollY < lastScrollY) { // If at the top of the page or scrolling up
      navBar.style.top = '0';
      clearTimeout(hideTimeout);
      if (window.scrollY !== 0) { // Only hide after delay if not at the very top
        hideTimeout = setTimeout(() => {
          if (primaryNav.getAttribute("data-visible") === "false") {
            navBar.style.top = '-100px';
          }
        }, navHideDelay);
      }
    } else if (primaryNav.getAttribute("data-visible") === "false") { // Scrolling down
      navBar.style.top = '-100px';
    }
    lastScrollY = window.scrollY;
  });
}

// Desktop nav-bar behavior (min-width: 47rem)
if (window.matchMedia("(min-width: 47rem)").matches) {
  const mainNav = document.querySelector(".main-nav");
  let lastScrollY = window.scrollY;
  let hideTimeout;

  mainNav.style.position = "fixed";
  mainNav.style.top = "0";
  mainNav.style.width = "100%";
  mainNav.style.transition = navTransitionIn;

  window.addEventListener('scroll', () => {
    if (window.scrollY === 0 || window.scrollY < lastScrollY) { // If at the top of the page or scrolling up
      mainNav.style.top = '0';
      clearTimeout(hideTimeout);
      if (window.scrollY !== 0) { // Only hide after delay if not at the very top
        hideTimeout = setTimeout(() => {
          mainNav.style.top = '-100px';
        }, navHideDelay);
      }
    } else { // Scrolling down
      mainNav.style.top = '-100px';
    }
    lastScrollY = window.scrollY;
  });
}

document.addEventListener('DOMContentLoaded', function () {
  filterSkills();
});


setTimeout(function() {
  const flashMessages = document.querySelector('.flash-messages');
  if (flashMessages) {
    flashMessages.style.transition = 'opacity 4s';
    flashMessages.style.opacity = '0';

    setTimeout(() => flashMessages.remove(), 4000);
  }
}, 2000);

document.querySelectorAll('.input-group input, .input-group textarea').forEach(input => {
  input.addEventListener('input', function() {
      if (input.value.trim() !== "") {
          input.classList.add('has-text');
      } else {
          input.classList.remove('has-text');
      }
  });
});