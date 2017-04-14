var r = new Rune({
  container: "#canvas",
  width: 300,
  height: 300,
  debug: false,
});


$.ajax({
  type: 'GET',
  url: "https://gist.githubusercontent.com/titipata/33bd071df166c135bcd5d87a6b53c32c/raw/e662e0dab90dc37dd615020418770655d4fac522/example_bim.json",
  dataType: 'json',
  success: function(result){
    var x = 10;
    var y = 0;
    var xt = 10;
    var yt = 5;

    for (var i = 0; i < result.length; i++) {
      if (result[i].user_id == 1){
        r.rect(x, y, 1, 10)
         .stroke(false)
         .fill(0)
        x++;
      }
      if( x > r.width - 10) {
        x = 10;
        y += 13;
        r.rect(x, y, 1, 10)
         .stroke(false)
         .fill(0)
        x++;
      }
      x++;

      if (result[i].user_id == 0){
        r.ellipse(xt, yt, 2, 2)
         .stroke(false)
         .fill(0)
        xt++;
      }
      if( xt > r.width - 10) {
        xt = 10;
        yt += 13;
        r.ellipse(xt, yt, 2, 2)
         .stroke(false)
         .fill(0)
        xt++;
      }
      xt++;
   }
  r.draw();
  }
});
