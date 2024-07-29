
var getDaysInMonth = function(month,year) {
    // Here January is 1 based
    //Day 0 is the last day in the previous month
   return new Date(year, month, 0).getDate();
  // Here January is 0 based
  // return new Date(year, month+1, 0).getDate();
  };
  //calculation o fthe energyconsumption and other factors
  document.querySelector('#frmcalculate').addEventListener('submit', function(event) {
    event.preventDefault();
})

  function energyCost(){
    var hours= (document.querySelector("#hoursPerDay").value);
console.log(hours);

var power= document.querySelector("#powerWatts").value

var price=document.querySelector("#Price").value

var month=document.querySelector("#month").value

    
    var b=(power*hours)/1000;
    console.log(hours);
    console.log(power);
    console.log(price);
    console.log(month);
    const date= new Date()
    document.getElementById("costPerHour").innerHTML=b/24;
    console.log(b);
    document.getElementById("costPerMonth").innerHTML=price*b*getDaysInMonth(month,date.getFullYear());
    document.getElementById("costPerDay").innerHTML=b*price;
    document.getElementById("costPerYear").innerHTML=b*365*price;
    document.getElementById("kwhPerDay").innerHTML=b;


}
//validating the data type

