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