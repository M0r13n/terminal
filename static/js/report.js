// get the form elements defined in your form HTML above
let form = document.getElementById("contactform");
let button = document.getElementById("submitBtn");
let status = document.getElementById("my-form-status");
const URL = "https://formspree.io/mlewwqog";

// Success and Error functions for after the form is submitted
function success() {
  form.reset();
  button.style = "display: none ";
  status.innerHTML = "Thanks!";
}

function error() {
  status.innerHTML = "Oops! There was a problem.";
}

// handle the form submission event
form.addEventListener("submit", function (ev) {
  ev.preventDefault();
  var data = new FormData(form);
  ajax('POST', URL, data, success, error);
  return false;
});

// helper function for sending an AJAX request
function ajax(method, url, data, success, error) {
  var xhr = new XMLHttpRequest();
  xhr.open(method, url);
  xhr.setRequestHeader("Accept", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState !== XMLHttpRequest.DONE) return;
    if (xhr.status === 200) {
      success(xhr.response, xhr.responseType);
    } else {
      error(xhr.status, xhr.response, xhr.responseType);
    }
  };
  xhr.send(data);
}