let markers=[];
let infowindows = [];
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
      mapId: "ccb0451a250a97fd",
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
      content: dat[i].DeviceID+", " +dat[i].address,
    });
    infowindows.push(infowindow)
    marker.addListener("click", () => {
      console.log(String(dat[i].latitude)+String(dat[i].longitude))
      s={
        "coord": String(dat[i].latitude)+String(dat[i].longitude),
        "lat": dat[i].latitude,
        "long": dat[i].longitude,
        "spec": "All"
      }
      reqss=$.ajax({
        url:"/Images",
        type:"POST",
        contentType: "application/json",
        data: JSON.stringify(s)
      });
      reqss.done(function(data){  
        $("#image").html(data)
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
    "lat":document.getElementById("lat").value,
    "long": document.getElementById("long").value,
    "coord": String(document.getElementById("lat").value)+String(document.getElementById("long").value),
    "spec": document.getElementById("wil").value
  }
  reqss=$.ajax({
    url:"/Images",
    type:"POST",
    contentType: "application/json",
    data: JSON.stringify(p)
  });
  reqss.done(function(data){
    $("#image").html(data)
  });  
}

