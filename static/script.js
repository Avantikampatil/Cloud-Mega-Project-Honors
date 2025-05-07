const objDiv = document.getElementById("messageBody");
const personAPIUrl = "https://randomuser.me/api/";
const mainMessages = document.getElementById("mainMessages");
var template = document.querySelector("#messageBlock");

objDiv.scrollTop = objDiv.scrollHeight;

// Create multiple entries in the left panel
for (i = 0; i <= 25; i++) {
  fetch("https://randomuser.me/api/")
    .then((response) => response.json())
    .then((data) => {
      let out = data;
      out = out.results;
      out = out[0];
      var clone = template.content.cloneNode(true);
      let img = clone.getElementById("personHeadshot");
      let personName = clone.getElementById("personName");
      let messagePreview = clone.getElementById("messagePreview");
      img.src = out.picture.thumbnail;
      personName.innerText = `${out.name.first} ${out.name.last}`;
      messagePreview.innerHTML = `${out.location.city} ${out.location.state} ${out.location.postcode} ${out.email}`;
      mainMessages.appendChild(clone);
    });
}
