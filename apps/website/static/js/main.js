function createElementFromHTML(htmlString) {
  // Create a temporary div element
  const tempDiv = document.createElement("div");

  tempDiv.innerHTML = htmlString;

  // Extract the first child element (the one created)
  return tempDiv.firstElementChild;
}


function replaceElement(oldElement, newElement) {
  oldElement.parentNode.replaceChild(newElement, oldElement);
}
