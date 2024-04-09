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

function toggleCheckbox(tag) {
  const targetButtons = skillsContainer.querySelectorAll(tag);
  const targetButton = skillsContainer.querySelector(tag);

  if (tag != ".all") {
    targetButtons.forEach(item => {
      item.classList.toggle("btn-check--checked");
    });
    if (checkAll()) {
      allBtns.forEach (item => {
        console.log(checkAll());
        item.classList.add("btn-check--checked");
      });
    } else {
      allBtns.forEach (item => {
        console.log(checkAll());
        item.classList.remove("btn-check--checked");
      });
    }
    
    
  } else {
    if (checkAll()) {
      allBtns.forEach (item => {
        skillsContainer.querySelectorAll(".btn-check").forEach(item => {
          item.classList.remove("btn-check--checked");
          });
      });
    } else {
      allBtns.forEach (item => {
        skillsContainer.querySelectorAll(".btn-check").forEach(item => {
        item.classList.add("btn-check--checked");
        });
      });
    }
    
  }

  
  
}


function toggleLight(element) {
  element.classList.toggle("enlightened");
}

function toggleTextLight(element) {
  element.classList.toggle("enlightened-text");
}


//nav-bar

const primaryNav = document.querySelector(".nav-list");
const navToggle = document.querySelector(".mobile-nav-toggle");

navToggle.addEventListener("click", () => {
  const visibility = primaryNav.getAttribute("data-visible");
  if (visibility === "false") {
    primaryNav.setAttribute("data-visible", true);
    navToggle.setAttribute("area-expanded", true);
  } else {
    primaryNav.setAttribute("data-visible", false);
    navToggle.setAttribute("area-expanded", false);
  }


});