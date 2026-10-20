
const years = document.querySelector("[name='academice_year']");
for (let i = 0; i < years.length; i++) {
  b = years[i].value;
  if (b == years.getAttribute("value")) {
    years[i].setAttribute("selected", "selected");
  }
}
const grades = document.querySelector("[name='grade']");
for (let i = 0; i < grades.length; i++) {
  b = grades[i].value;
  if (b == grades.getAttribute("value")) {
    grades[i].setAttribute("selected", "selected");
  }
}
const sections = document.querySelector("[name='section']");
for (let i = 0; i < sections.length; i++) {
  b = sections[i].value;
  if (b == sections.getAttribute("value")) {
    sections[i].setAttribute("selected", "selected");
  }
}
