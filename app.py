from flask import Flask, render_template, jsonify, redirect,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import db
import pyrebase
from geopy.geocoders import Nominatim
from datetime import datetime
from twilio.rest import Client

client = Client("Twilio_Account_SID","Twilio_Auth_Token")

cred = credentials.Certificate("Credkeys/serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    "databaseURL": "Your firebase realtime database url",
    "storageBucket": "Your Firebase storage bucket url"
})
fs= firestore.client()

# #Replace Your firebase config credential here
 
firebaseConfig = {
  "apiKey": "Your firebase api key",
  "authDomain": "Your firebase authDomain",
  "databaseURL": "Your firebase realtime database url",
  "projectId": "your project id",
  "storageBucket": "Your Firebase storage bucket url",
  "messagingSenderId": "firebase sender id",
  "appId": "ypur firebase app ID",
  "measurementId": "your project Measurement ID"
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage() 


#this function is used for extract address from coordinates
def locate(lat,lon):
    cord = [lat,lon]    
    geoLoc = Nominatim(user_agent="GetLoc")
    locname = geoLoc.reverse(cord)
    add = locname.address
    return add
    
#This function is used here to get gateway information from firebase
def Gateway_Info():
    data = db.reference("Gateway-Info").get()
    Gateway_Infos =[]
    if data is None:
        Gateway_Infos = []
        return Gateway_Infos
    else:                
        countries = list(data)
        for country in countries:
            data = db.reference("Gateway-Info").child(country).get()
            states = list(data)
            for state in states:
                data = db.reference("Gateway-Info").child(country).child(state).get()
                cities = list(data)
                for city in cities:
                    data = db.reference("Gateway-Info").child(country).child(state).child(city).get()
                    info = list(data.values())
                    Gateway_Infos = Gateway_Infos+ info     
        return Gateway_Infos



app =Flask(__name__)

#this Route is for render our index.html page
@app.route("/")
def map():
    return render_template("index.html") 

#this route is for load our admin.html page
@app.route("/admin")                                            
def admin():
    Gateway_Id = []
    data= db.reference("Gateway-Info").get()
    gate = []
    if data is None:
        Gateway_Id = []
        return render_template("admin.html",ids=Gateway_Id)
    else:          
        countries = list(data)
        for country in countries:
            data = db.reference("Gateway-Info").child(country).get()
            states = list(data)
            for state in states:
                data = db.reference("Gateway-Info").child(country).child(state).get()
                cities = list(data)
                for city in cities:
                    data = db.reference("Gateway-Info").child(country).child(state).child(city).get()
                    Gateway_Id = list(data)
                    gate = gate+ Gateway_Id
                    gate.sort(reverse=False);                    
            
        return render_template("admin.html",ids=gate)
        
        
#This route is for getting address from coordinates send by javascript by ajax post request.
@app.route("/location", methods=["POST"])                           
def get():
    data = request.get_json()
    add = locate(data["lat"],data["long"])
    print(add)
    return jsonify({'address': add})
    

# This route is to submit the Gateway information to firebase using ajax post request from javascript.
@app.route("/submit", methods=['POST'])                             
def deploy():
    sub = request.get_json()
    add = locate(sub["lat"],sub["long"])
    myadd = add.split(",")
    def int_filter( someList ):
        for v in someList:
            try:
                int(v)
                continue # Skip these
            except ValueError:
                yield v # Keep these    
    myadd = (list(int_filter(myadd)))
    city= myadd[-3]
    state= myadd[-2]
    country= myadd[-1]
    payload = {
        "DeviceID": sub["devid"],
        "latitude":sub["lat"],
        "longitude":sub["long"],
        "address":add,
        "Deloyement_date_time": str(datetime.now())
    }
    db.reference("Gateway-Info").child(country).child(state).child(city).child(sub["devid"]).set(payload)
    print(payload)
    return "success"
    

# This route is to deploy the nodes with null values to firebase using ajax post request from javascript.
@app.route("/nodes", methods=['POST'])                           
def node_deploy():
    sub = request.get_json()
    payload = {
        "fire_Status": 0,
        "Humadity": 0, 
        "Temperature": 0,
        "Battery":0,
        "Last_update": str(datetime.now())
    }    
    db.reference("Nodes-Status").child(sub["wildid"]).child(sub["nodeid"]).set(payload)
    print(payload)
    return "success"
    
# This route is to upload the images from directly html using jinja to firebase storage as well as urls in firestore.
@app.route("/upload", methods=['POST'])
def upload():
    Id = request.form["id"]
    spec = request.form["spec"]
    coords = Gateway_Info()
    for gate in coords:
        if gate["DeviceID"] == Id:
            print(gate)
            newcoord = str(gate["latitude"])+str(gate["longitude"])
    
    files = request.files.getlist('file')
    if files[0].filename == '' :
        ms = "Select a file"
    else:
        for file in files:
            storage.child(Id+"/"+newcoord+"/"+spec+"/"+file.filename).put(file)
            urlss = storage.child(Id+"/"+newcoord+"/"+spec+"/"+file.filename).get_url(None)
            dataa = {
                "Species":spec,
                "URL":urlss
            }
            fs.collection(newcoord).add(dataa)
    return "Successfully uploaded"


#this route is here to open the map.html page for explore the wild life images all over world using map integrated with google map api
@app.route("/map")                                              
def maps():
        return render_template("map.html",data=Gateway_Info()) 


#This route is to get the images after sorting and filtering from map.html using ajax post request from javascript.
@app.route("/Images", methods=["POST"])                     
def show():
    req=request.get_json()
    add = locate(req['lat'],req['long'])
    src = fs.collection(req['coord']).get()
    species = []
    urls = []    
    for sr in src:
        species.append(sr.to_dict()['Species'])
        urls.append(sr.to_dict()['URL'])
    li =list(dict.fromkeys(species))
    if req['spec'] == "All":
        data = {
            "specieslen":len(li),
            "urlslen":len(urls),
            "species": li,
            "urls": urls
        }
        print(data)
        return render_template("image.html",urls=urls,species=li,speclen=len(li),urllen=len(urls),add = add,lat=req['lat'],long=req['long'])
    else:
        spec =str(req['spec'])
        srcf = fs.collection(req['coord']).where("Species","==",spec).get()
        urlsf = []    
        for sr in srcf:
            urlsf.append(sr.to_dict()['URL'])
        data1 = {
            "specieslen":spec,
            "urlslen":len(urlsf),
            "species": li,
            "urls": urlsf
        }
        print(data1)
        return render_template("filter.html",urls=urlsf,species=li,speclen=spec,urllen=len(urlsf),add = add,lat=req['lat'],long=req['long'])

#this route is for load fire.html page which is our node status panel
@app.route("/NodesStatus")
def firepage():
    return render_template("fire.html", data = Gateway_Info()) 

#this route is to get list of nodes according to gateway in same page fire.html
@app.route("/Node_status",methods=["POST"])
def nodestatus():
    if request.method == "POST":
        nodecoord = request.get_json()
        gates = Gateway_Info()
        for gate in gates:
            if gate["latitude"] == nodecoord["lat"] and gate["longitude"] == nodecoord["long"]:
                devid = gate["DeviceID"]
                address = gate["address"]
        nodesdata = db.reference("Nodes-Status").child(devid).get()
        ni = list(nodesdata)
        if nodesdata is None:
            ni = []
            return render_template("node.html",add = address ,NodeIds = ni, wid = devid)
        else:
            return render_template("node.html",add = address ,NodeIds = ni, wid = devid)
            
            
#this route is here for showing nodes data on fire.html page
@app.route("/Node_filter",methods=["POST"])
def nodesfilter():
    if request.method == "POST":
        nodepara = request.get_json()
        nodesdata = db.reference("Nodes-Status").child(nodepara["deviceID"]).child(nodepara["node"]).get()
        print(nodesdata)
        if str(nodesdata["fire_Status"]) == "0":
            return render_template("nodefilter.html",nid = nodepara["node"], humadity = nodesdata["Humadity"], temperature = nodesdata["Temperature"], firestatus = "NO")
        else:
            return render_template("nodefilter.html",nid = nodepara["node"], humadity = nodesdata["Humadity"], temperature = nodesdata["Temperature"], firestatus = "YES")
            
#this route load the subscribe.html page which get user name, number and address then upload it to firebase using ajax post request javascript
@app.route("/Subscribe", methods=["POST","GET"])
def subscribe():
    if request.method == "POST":
        sub = request.get_json()
        add = locate(sub["lat"],sub["long"])
        myadd = add.split(",")
        def int_filter( someList ):
            for v in someList:
                try:
                    int(v)
                    continue # Skip these
                except ValueError:
                    yield v # Keep these    
        myadd = (list(int_filter(myadd)))
        city= myadd[-3]
        state= myadd[-2]
        country= myadd[-1]
        payload = {
            "Name":sub["devid"],
            "latitude":sub["lat"],
            "longitude":sub["long"],
            "address":add,
            "contact_Number":sub["num"],
            "Subscribtion_date_time": str(datetime.now())
        }
        db.reference("User-Info").child(country).child(state).child(city).push(payload)
        print(payload)
        return "success"    
    else:
        return render_template("Subscribe.html") 

#this route is to send alert messages to users  when fire_status change of any node nearby them and in firebase and get trigged the firebase function(onUpdate) then function send post request to this route using axios.
@app.route("/firedetect",methods=["POST"])
def firedetects():   
    if request.method == "POST":
        users = []
        Request_data = request.get_json()
        print(Request_data)
        print(Request_data["fire_status"])
        if Request_data["fire_status"] == 1:            
            data = db.reference("Gateway-Info").get()           
            countries = list(data)
            for country in countries:
                data = db.reference("Gateway-Info").child(country).get()
                states = list(data)
                for state in states:
                    data = db.reference("Gateway-Info").child(country).child(state).get()
                    cities = list(data)
                    for city in cities:
                        data = db.reference("Gateway-Info").child(country).child(state).child(city).get()
                        devices = list(data)
                        for device in devices:
                            if device == Request_data["GatewayID"]:
                                data = db.reference("User-Info").child(country).child(state).child(city).get()
                                users = list(data.values())  
                                for user in users:
                                    message = client.messages.create(
                                        body= f"Wildfire detects by gateway {device} in your city {city}, "+ user["Name"]+"Please save yourself",
                                        from_= +18509035120,
                                        to= user["contact_Number"]
                                    )
        else:            
            data = db.reference("Gateway-Info").get()           
            countries = list(data)
            for country in countries:
                data = db.reference("Gateway-Info").child(country).get()
                states = list(data)
                for state in states:
                    data = db.reference("Gateway-Info").child(country).child(state).get()
                    cities = list(data)
                    for city in cities:
                        data = db.reference("Gateway-Info").child(country).child(state).child(city).get()
                        devices = list(data)
                        for device in devices:
                            if device == Request_data["GatewayID"]:
                                data = db.reference("User-Info").child(country).child(state).child(city).get()
                                users = list(data.values())  
                                for user in users:
                                    message = client.messages.create(
                                        body= f"Wildfire is mitigated in gateway {device} in your city {city}, "+ user["Name"]+",Now you are Safe",
                                        from_= +18509035120,
                                        to= user["contact_Number"]
                                    )
        return "200"

#this route is api for get data from hardware end and update it on firebasae
@app.route("/update",methods=["POST"])
def nodeupdate():
    Updatedata = request.get_json()
    payload ={
        "Battery":Updatedata["Battery"],
        "Humadity":Updatedata["Humadity"],
        "Last_update":str(datetime.now()),
        "Temperature":Updatedata["Temperature"],
        "fire_Status":Updatedata["fire_Status"]
    }
    db.reference("Nodes-Status").child(Updatedata["GatewayID"]).child(Updatedata["NodeID"]).set(payload)
    print("succes")
    return "success"

if __name__ == '__main__':
    app.run(debug=True)