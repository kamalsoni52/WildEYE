var input = document.querySelector("#phone"),
    errorMsg = document.querySelector("#error-msg"),
    validMsg = document.querySelector("#valid-msg");

// Error messages based on the code returned from getValidationError
var errorMap = [ "Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];

// Initialise plugin
var intl = window.intlTelInput(input, {
    initialCountry: "auto",
    geoIpLookup: function(success, failure) {
        $.get("https://ipinfo.io", function() {}, "jsonp").always(function(resp) {
            var countryCode = (resp && resp.country) ? resp.country : "in";
            success(countryCode);
        });
    },
    utilsScript: "static/utils.js"
});

var reset = function() {
    input.classList.remove("error");
    errorMsg.innerHTML = "";
    errorMsg.classList.add("hide");
    validMsg.classList.add("hide");
};

// Validate on blur event
input.addEventListener('blur', function() {
    reset();
    if(input.value.trim()){
        if(intl.isValidNumber()){
            validMsg.classList.remove("hide");
        }else{
            input.classList.add("error");
            var errorCode = intl.getValidationError();
            errorMsg.innerHTML = errorMap[errorCode];
            errorMsg.classList.remove("hide");
        }
    }
});

// Reset on keyup/change event
input.addEventListener('change', reset);
input.addEventListener('keyup', reset);


function empty(){
    let name = document.getElementById('username').value;

    if(name!=""){
        document.getElementById("locate").removeAttribute("disabled");
        
        console.log("hi")
    }
}
var lat = "";
var lon = "";

function clicklocatee(){
    if ('geolocation' in navigator) {
      console.log('geolocation available');
      
      navigator.geolocation.getCurrentPosition(position => {
        lat = position.coords.latitude;
        lon = position.coords.longitude;        
        s= { "lat": lat, "long": lon}
        req = $.ajax({
          url:"/location",
          type:"POST",
          contentType: "application/json",
          data: JSON.stringify(s)
      });
      req.done(function(data){
        document.getElementById('address').value = data.address
      });
      });
    }
    else {
      console.log('geolocation not available');
    }
    document.getElementById("Subscribe").removeAttribute("disabled");
}

function sub(){   
    if(intl.isValidNumber()){
        validMsg.classList.remove("hide");
  let dev = document.getElementById('username').value;
  let add = document.getElementById('address').value;
  let number = intl.getNumber();
  s = {
    "devid":dev,
    "lat":lat,
    "long":lon,
    "add":add,
    "num":number
  }
  console.log(JSON.stringify(s));
  reqs=$.ajax({
    url:"/Subscribe",
    type:"POST",
    contentType: "application/json",
    data: JSON.stringify(s)
  });
  reqs.done(function(data){
    console.log(data)
      if (data=="success"){
        window.alert("successfully deployed")
        location.reload();
      }
      else{
        window.alert("deployement unsuccessful")
        location.reload();
      }
  });
}
else{
    window.alert("Number is invalid")
}
}