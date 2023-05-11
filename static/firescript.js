let markers = [];
let infowindows = [];
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 20.5937, lng: 78.9629 },
      zoom: 4,
    });
   
   
    for (let i in dat)
    {      
    let marker = new google.maps.Marker({
      position: { lat: parseInt(dat[i].latitude), lng: parseInt(dat[i].longitude) },
      map,
      title: dat[i].address,
    });
    let infowindow = new google.maps.InfoWindow({
      content: dat[i].DeviceID+", " + dat[i].address,
    });
    infowindows.push(infowindow)
    marker.addListener("click", () => {
      s={
        "lat": dat[i].latitude,
        "long": dat[i].longitude,
      }
      reqss=$.ajax({
        url:"/Node_status",
        type:"POST",
        contentType: "application/json",
        data: JSON.stringify(s)
      });
      reqss.done(function(data){  
        $("#status").html(data)
      });     
           
    });  
    markers.push(marker);
  } 
  seton(map)    
}
function seton(map){
  for (let i = 0; i < markers.length; i++) {
    markers[i].addListener('click',()=>{
    infowindows[i].open({
      anchor: markers[i],
      map,
      shouldFocus: false,
    }); 
  });
    markers[i].setMap(map);
  }
}
function search(){
  p= {
    "node": document.querySelector('#nodeid').value,
    "deviceID": document.getElementById("wid").value, 
  }
  reqss=$.ajax({
    url:"/Node_filter",
    type:"POST",
    contentType: "application/json",
    data: JSON.stringify(p)
  });
  reqss.done(function(data){
    $("#node-state").html(data)
  });  
}


