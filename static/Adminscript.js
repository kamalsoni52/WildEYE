function empty(){
    let wildid = document.getElementById('wildid').value;

    if(wildid!=""){
        document.getElementById("locate").removeAttribute("disabled");
        
        console.log("hi")
    }
}


function clicklocatee(){
    if ('geolocation' in navigator) {
      console.log('geolocation available');
      let lat = "";
      let lon = "";
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
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;
      });
      });
    }
    else {
      console.log('geolocation not available');
    }
    document.getElementById("submit").removeAttribute("disabled");
}

function sub(){
  let dev = document.getElementById('wildid').value;
  let lat = document.getElementById('latitude').value;
  let lon = document.getElementById('longitude').value;
  let add = document.getElementById('address').value;
  s = {
    "devid":dev,
    "lat":lat,
    "long":lon,
    "add":add
  }
  console.log(JSON.stringify(s));
  reqs=$.ajax({
    url:"/submit",
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

function depNode() {
  let node = document.getElementById('nodes').value;
  let devid = document.querySelector('#wili').value;
  s = {
    "wildid":devid,
    "nodeid": node
  }
  console.log(JSON.stringify(s));
  reqs=$.ajax({
    url:"/nodes",
    type:"POST",
    contentType: "application/json",
    data: JSON.stringify(s)
  });
  reqs.done(function(data){
    console.log(data)
      if (data=="success"){
        window.alert(`Node ${node} successfully deployed to gateway ${devid}`)
        location.reload();
      }
      else{
        window.alert("deployement unsuccessful")
        location.reload();
      }
  });
}


