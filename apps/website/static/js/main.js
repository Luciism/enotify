function toTitleCase(str) {
  return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}


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
